import React, { useState, useEffect } from 'react';
import api from '../api/axios';
import { PointForm } from './PointForm'; 
import { ImageGalleryUploader } from '../components/ImageGalleryUploader';
import type {FullExcursion, Point, MediaObject, Category} from '../types/api';

// Разделяем понятие экрана (основной UI / форма точки / полноэкранный превью) и вкладок внутри редактора
type ActiveTab = 'BASIC_INFO' | 'POINTS_LIST';
type ScreenMode = 'EDITOR' | 'POINT_FORM' | 'PREVIEW';

interface ExcursionEditorProps {
  excursionId?: number; // Если передан — мы в режиме РЕДАКТИРОВАНИЯ, если нет — СОЗДАНИЯ
  onBack: () => void;
}

export const ExcursionEditor: React.FC<ExcursionEditorProps> = ({ excursionId, onBack }) => {
  // Управление экранами и вкладками
  const [screenMode, setScreenMode] = useState<ScreenMode>('EDITOR');
  const [activeTab, setActiveTab] = useState<ActiveTab>('BASIC_INFO');
  
  // Статусы загрузок
  const [isSaving, setIsSaving] = useState(false);
  const [isPublishing, setIsPublishing] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  
  const [currentImgIdx, setCurrentImgIdx] = useState(0);


  //category
  const [categories, setCategories] = useState<Category[]>([]);



  // Единый источник правды для данных экскурсии
  const [data, setData] = useState<Partial<FullExcursion>>({
    id: excursionId,
    title: '',
    description: '',
    status: 'draft',
    category_id: undefined,
    images: [], 
    points: [],
    distance: undefined,
    duration: undefined,

  });

  // Состояния для редактирования конкретной точки
  const [editingPoint, setEditingPoint] = useState<Partial<Point> | null>(null);
  const [editingPointIndex, setEditingPointIndex] = useState<number | null>(null);



  useEffect(() => {
    const loadCategories = async () => {
      try {
        setIsLoading(true);
        const response = await api.get<Category[]>('/admin/categories');
        setCategories(response.data);
      } catch (err) {
        console.error('Ошибка загрузки категорий', err);
      } finally {
        setIsLoading(false);

      }
    };
    loadCategories();
  }, []);

  useEffect(() => {
    if (excursionId) {
      const loadExcursionData = async () => {
        try {
          setIsLoading(true);
          const response = await api.get<FullExcursion>(`/admin/excursions/${excursionId}`);
          setData(response.data);
        } catch (err) {
          console.error('Ошибка при загрузке экскурсии:', err);
          alert('Не удалось загрузить данные экскурсии для редактирования');
        } finally {
          setIsLoading(false);
        }
      };
      loadExcursionData();
    }
  }, [excursionId]);

  const handleSaveBasicInfo = async () => {
    if (!data.title?.trim()) {
      alert('Пожалуйста, введите название экскурсии');
      return;
    }

    try {
      setIsSaving(true);
      const payload = {
        id: data.id,
        title: data.title,
        description: data.description || '',
        category_id: data.category_id || 1,
        distance: data.distance !== undefined && data.distance !== null ? data.distance : null,
        duration: data.duration !== undefined && data.duration !== null ? data.duration : null,
      };

      const currentImages = data.images || [];
      const isNewExcursion = !data.id; 

      if (!isNewExcursion) {
        await api.put(`/admin/excursions/${data.id}`, payload);
        alert('Изменения успешно сохранены в черновик!');
      } else {
        const response = await api.post('/admin/excursions/create', payload);
        const createdId = response.data.id;
        
        // Обновляем локальный стейт данными с бэка
        setData(prev => ({ 
          ...prev, 
          id: createdId,
          points: prev.points || [], 
          images: prev.images || []
        }));

        if (currentImages.length > 0) {
          for (let i = 0; i < currentImages.length; i++) {
            await api.post(`/admin/excursions/${createdId}/media`, {
              media_id: currentImages[i].id,
              position: i + 1
            });
          }
        }
      }

      setActiveTab('POINTS_LIST');
    } catch (err) {
      console.error('Ошибка сохранения экскурсии:', err);
      alert('Ошибка при сохранении данных экскурсии.');
    } finally {
      setIsSaving(false);
    }
  };

  // --- 3. Добавление / Обновление точки на бэкенде ---
  const handleSavePoint = async (pointData: Partial<Point>) => {
    try {
      setIsSaving(true);
      const currentPoints = [...(data.points || [])];
      
      // Маппим contents, собирая все id медиафайлов в плоский массив media_ids
      const formattedContents = (pointData.contents || []).map(content => {
        const mediaIds: number[] = [];
        
        if (content.audio?.id) {
          mediaIds.push(content.audio.id);
        }
        
        if (content.images && content.images.length > 0) {
          content.images.forEach(img => {
            if (img.id) mediaIds.push(img.id);
          });
        }

        return {
          lang: content.lang,
          name: content.name,
          description: content.description,
          address: content.address,
          media_ids: mediaIds // Бэкенд ждет именно это поле
        };
      });

      const pointPosition = editingPointIndex !== null 
        ? (editingPointIndex + 1) 
        : (currentPoints.length + 1);

      const pointPayload = {
        excursion_id: Number(data.id), 
        latitude: pointData.latitude || 0,
        longitude: pointData.longitude || 0,
        radius_meters: pointData.radius_meters || 20,
        position: pointPosition,
        contents: formattedContents
      };
      
      let responseData: Point;

      if (editingPointIndex !== null && pointData.id) {
        const response = await api.put<Point>(`/admin/excursions/points/${pointData.id}`, pointPayload);
        responseData = response.data;
        currentPoints[editingPointIndex] = responseData;
      } else {

        const response  = await api.post<Point>('/admin/excursions/points', pointPayload);
        responseData = response.data;
        currentPoints.push(responseData);
      }

      setData(prev => ({ ...prev, points: currentPoints }));
      
      setScreenMode('EDITOR'); 
      setEditingPoint(null);
      setEditingPointIndex(null);
    } catch (err) {
      console.error('Ошибка при сохранении точки:', err);
      alert('Не удалось сохранить точку на сервере.');
    } finally {
      setIsSaving(false);
    }
  };

  // --- 4. Удаление точки с бэкенда ---
  const handleDeletePoint = async (index: number) => {
    const targetPoint = data.points?.[index];
    if (!targetPoint) return;

    if (!confirm('Удалить эту локацию из маршрута?')) return;

    try {
      setIsSaving(true);
      
      if (targetPoint.id) {
        await api.delete(`/admin/excursions/points/${targetPoint.id}`);
      }

      const remainingPoints = (data.points || []).filter((_, i) => i !== index);
      const updatedPoints = remainingPoints.map((p, i) => ({ ...p, position: i + 1 }));
      
      
      setData(prev => ({ ...prev, points: updatedPoints }));
    } catch (err) {
      console.error('Ошибка при удалении точки:', err);
      alert('Не удалось удалить точку на сервере.');
    } finally {
      setIsSaving(false);
    }
  };

  // --- 4. Публикация всей экскурсии ---
  const handlePublishExcursion = async () => {
    if (!data.id) {
      alert('Невозможно опубликовать несохраненную экскурсию');
      return;
    }
    try {
      setIsPublishing(true);
      await api.put(`/admin/excursions/${data.id}/publish`);
      alert('Экскурсия успешно опубликована и доступна пользователям!');
      onBack();
    } catch (err) {
      console.error(err);
      alert('Ошибка при публикации экскурсии.');
    } finally {
      setIsPublishing(false);
    }
  };

  const movePoint = (index: number, direction: 'up' | 'down') => {
    const currentPoints = [...(data.points || [])];
    const targetIndex = direction === 'up' ? index - 1 : index + 1;
    if (targetIndex < 0 || targetIndex >= currentPoints.length) return;

    const temp = currentPoints[index];
    currentPoints[index] = currentPoints[targetIndex];
    currentPoints[targetIndex] = temp;

    const updatedPoints = currentPoints.map((p, i) => ({ ...p, position: i + 1 }));
    setData(prev => ({ ...prev, points: updatedPoints }));
  };

  if (isLoading) {
    return <div className="min-h-screen flex items-center justify-center text-sm text-gray-500">Загрузка данных...</div>;
  }

  
  // Экран публикации и компактного предпросмотра
  if (screenMode === 'PREVIEW') {
    // Собираем все картинки экскурсии для карусели
    const allImages = data.images && data.images.length > 0 ? data.images : [];
    
    // Функции для прокрутки карусели картинок (если их много)
    const handleNextImage = (totalImages: number) => {
      if (totalImages <= 1) return;
      setCurrentImgIdx(prevIdx => (prevIdx + 1) % totalImages);
    };

    const handlePrevImage = (totalImages: number) => {
      if (totalImages <= 1) return;
      setCurrentImgIdx(prevIdx => (prevIdx - 1 + totalImages) % totalImages);
    };

    return (
      <div className="min-h-screen bg-white py-8 px-6 font-sans text-gray-900">
        <div className="max-w-4xl mx-auto">
          
          {/* Верхняя навигационная панель */}
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
            <div>
              <button 
                type="button" 
                onClick={() => setScreenMode('EDITOR')} 
                className="text-sm font-medium text-gray-500 hover:text-gray-800 transition flex items-center gap-2 mb-1"
              >
                ← Назад к списку маршрутов
              </button>
              <h1 className="text-xl font-bold text-gray-900">Проверьте информацию перед публикацией</h1>
            </div>
            
            {/* Кнопки управления */}
            <div className="flex items-center gap-3 w-full md:w-auto">
              <button
                type="button"
                onClick={() => setScreenMode('EDITOR')}
                className="flex-1 md:flex-none px-5 py-2.5 bg-gray-200 hover:bg-gray-300 text-gray-800 font-semibold rounded-lg text-sm transition"
              >
                Редактировать
              </button>
              <button
                type="button"
                onClick={handlePublishExcursion}
                disabled={isPublishing}
                className="flex-1 md:flex-none px-5 py-2.5 bg-[#801020] hover:bg-[#660d1a] text-white font-semibold rounded-lg text-sm transition disabled:bg-gray-300"
              >
                {isPublishing ? 'Публикация...' : 'Опубликовать'}
              </button>
            </div>
          </div>

          {/* Галерея/Карусель картинок во всю ширину */}
          <div className="relative w-full aspect-[21/9] bg-gray-100 rounded-lg overflow-hidden mb-8 group">
            {allImages.length > 0 ? (
              <div className="flex w-full h-full transition-transform duration-300">

                <img 
                  src={allImages[currentImgIdx || 0]?.file_url} 
                  alt="Медиа файлы экскурсии" 
                  className="w-full h-full object-cover"
                />
              </div>
            ) : (
              <div className="w-full h-full flex items-center justify-center text-gray-400 text-sm italic">
                🏞 Изображения маршрута не загружены
              </div>
            )}

            {/* Стрелки навигации для карусели (появляются при ховере) */}
            {allImages.length > 1 && (
              <>
                <button
                  type="button"
                  onClick={() => handlePrevImage(allImages.length)}
                  className="absolute left-4 top-1/2 -translate-y-1/2 w-10 h-10 rounded-full bg-white shadow-md flex items-center justify-center text-gray-700 hover:bg-gray-50 transition"
                >
                  ‹
                </button>
                <button
                  type="button"
                  onClick={() => handleNextImage(allImages.length)}
                  className="absolute right-4 top-1/2 -translate-y-1/2 w-10 h-10 rounded-full bg-white shadow-md flex items-center justify-center text-gray-700 hover:bg-gray-50 transition"
                >
                  ›
                </button>
              </>
            )}
          </div>

          {/* Список точек маршрута */}
          <div className="space-y-12">
            {(!data.points || data.points.length === 0) ? (
              <p className="text-sm text-gray-400 italic">Точки маршрута не найдены.</p>
            ) : (
              data.points.map((point, idx) => {
                const content = point.contents?.[0];

                return (
                  <div key={point.id || idx} className="space-y-4">
                    
                    {/* Шапка точки: Позиция в розовом круге, Название, Адрес */}
                    <div className="flex items-start gap-4">
                      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-[#FCE8EB] text-[#801020] flex items-center justify-center text-sm font-bold mt-0.5">
                        {point.position || (idx + 1)}
                      </div>
                      <div>
                        <h3 className="text-base font-bold text-gray-900 leading-tight">
                          {content?.name || 'Локация без названия'}
                        </h3>
                        {content?.address && (
                          <p className="text-xs text-gray-400 font-medium mt-0.5">
                            {content.address}
                          </p>
                        )}
                      </div>
                    </div>

                    {/* Текст описания точки (разбитый по абзацам) */}
                    <div className="text-sm text-gray-800 leading-relaxed space-y-4 pl-12 whitespace-pre-line">
                      {content?.description ? (
                        content.description
                      ) : (
                        <p className="text-gray-400 italic">Описание для данной локации отсутствует.</p>
                      )}
                    </div>

                  </div>
                );
              })
            )}
          </div>

        </div>
      </div>
    );
  }

  // ОСНОВНОЙ РЕДАКТОР (Экраны EDITOR и POINT_FORM рендерятся тут)
  return (
    <div className="min-h-screen bg-white font-sans text-gray-900 pb-20">
      <header className="max-w-6xl mx-auto px-8 py-6 flex justify-between items-center border-b border-gray-100 mb-8">
        <div>
          <button onClick={onBack} className="text-sm text-gray-400 hover:text-gray-600 transition mb-1 block">
            ← К списку экскурсий
          </button>
          <h1 className="text-xl font-bold text-gray-800">
            {data.id ? `Редактирование экскурсии #${data.id}` : 'Создание новой экскурсии'}
          </h1>
        </div>
        <div className="flex gap-3">
          <button 
            onClick={handleSaveBasicInfo}
            disabled={isSaving}
            className="px-5 py-2.5 bg-gray-300 text-black hover:bg-gray-400 rounded-xl text-sm font-medium transition"
          >
            {isSaving ? 'Сохранение...' : 'Сохранить как черновик'}
          </button>
          <button 
            onClick={() => setScreenMode('PREVIEW')}
            disabled={!data.id}
            className="px-5 py-2.5 bg-[#801020] hover:bg-[#660d1a] text-white rounded-xl text-sm font-medium transition disabled:bg-gray-200"
          >
            Экран публикации
          </button>
        </div>
      </header>

      {/* Переключатель вкладок — Рендерится только в режиме EDITOR */}
      {screenMode === 'EDITOR' && (
        <div className="max-w-4xl mx-auto px-8 mb-8">
          <div className="flex gap-8 border-b border-gray-200 text-sm font-medium text-gray-400">
            <button 
              type="button"
              onClick={() => setActiveTab('BASIC_INFO')} 
              className={`pb-3 transition-all ${activeTab === 'BASIC_INFO' ? 'text-gray-900 font-bold border-b-2 border-gray-900' : 'hover:text-gray-600'}`}
            >
              1. Основная информация
            </button>
            <button 
              type="button"
              onClick={() => { if (data.id) setActiveTab('POINTS_LIST'); else alert('Сначала нажмите кнопку "Сохранить инфо"!'); }} 
              className={`pb-3 transition-all ${!data.id ? 'opacity-40 cursor-not-allowed' : ''} ${activeTab === 'POINTS_LIST' ? 'text-gray-900 font-bold border-b-2 border-gray-900' : 'hover:text-gray-600'}`}
            >
              2. Точки маршрута ({data.points?.length || 0})
            </button>
          </div>
        </div>
      )}

      <main className="max-w-4xl mx-auto px-8">
        {/* Экран формы создания/редактирования точки */}
        {screenMode === 'POINT_FORM' && (
          <div className="py-4">
            <PointForm 
              point={editingPoint || undefined}
              onSave={handleSavePoint}
              onCancel={() => { setScreenMode('EDITOR'); setEditingPoint(null); setEditingPointIndex(null); }}
            />
          </div>
        )}

        {/* Вкладка 1: Основное инфо */}
        {screenMode === 'EDITOR' && activeTab === 'BASIC_INFO' && (
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Название маршрута</label>
                <input
                    type="text"
                    className="w-full p-4 bg-gray-50 border border-gray-200 rounded-2xl outline-none focus:border-gray-400 text-sm"
                    placeholder="Введите название экскурсии..."
                    value={data.title || ''}
                    onChange={(e) => setData(prev => ({...prev, title: e.target.value}))}
                />
              </div>
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Категория маршрута</label>
                <select
                    className="w-full p-4 bg-gray-50 border border-gray-200 rounded-2xl text-sm outline-none focus:border-gray-400"
                    value={data.category_id ?? ''}
                    onChange={(e) => {
                      const val = e.target.value;
                      setData(prev => ({
                        ...prev,
                        category_id: val ? parseInt(val) : undefined
                      }));
                    }}
                >
                  <option value="">-- Выберите категорию --</option>
                  {categories.map(cat => (
                      <option key={cat.id} value={cat.id}>
                        {cat.name}
                      </option>
                  ))}
                </select>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Длина маршрута (км)</label>
                  <input
                      type="number"
                      step="0.1"
                      className="w-full p-4 bg-gray-50 border border-gray-200 rounded-2xl text-sm"
                      placeholder="Например: 2.5"
                      value={data.distance ?? ''}
                      onChange={(e) => setData(prev => ({
                        ...prev,
                        distance: e.target.value ? parseFloat(e.target.value) : undefined
                      }))}
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Длительность (мин)</label>
                  <input
                      type="number"
                      className="w-full p-4 bg-gray-50 border border-gray-200 rounded-2xl text-sm"
                      placeholder="Например: 60"
                      value={data.duration ?? ''}
                      onChange={(e) => setData(prev => ({
                        ...prev,
                        duration: e.target.value ? parseInt(e.target.value) : undefined
                      }))}
                  />
                </div>
              </div>


              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Краткое описание</label>
                <textarea
                    className="w-full p-4 bg-gray-50 border border-gray-200 rounded-2xl h-40 resize-none"
                    placeholder="Опишите экскурсию..."
                    value={data.description || ''}
                    onChange={(e) => setData(prev => ({...prev, description: e.target.value}))}
                />
              </div>
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Обложка / Фотогалерея</label>
                <ImageGalleryUploader
                    images={data.images || []}
                    onChange={(updatedImages: MediaObject[]) => {
                      setData(prev => {
                        if (!prev.id && excursionId) {
                          return {...prev, id: excursionId, images: updatedImages};
                        }
                        return {...prev, images: updatedImages};
                      });
                    }}
                />
              </div>
            </div>
        )}

        {/* Вкладка 2: Список точек маршрута */}
        {screenMode === 'EDITOR' && activeTab === 'POINTS_LIST' && (
            <div className="space-y-6">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-bold text-gray-800">Локации маршрута</h3>
                <button
                    type="button"
                    onClick={() => {
                      setEditingPoint(null);
                      setEditingPointIndex(null);
                      setScreenMode('POINT_FORM');
                    }}
                    className="bg-[#801020] hover:bg-[#660d1a] text-white px-4 py-2.5 rounded-xl font-medium text-xs shadow-sm"
                >
                  + Добавить новую точку
                </button>
              </div>

              <div className="bg-white border rounded-2xl overflow-hidden">
                <table className="w-full text-left border-collapse">
                  <thead>
                  <tr className="border-b bg-gray-50 text-xs font-semibold text-gray-500 uppercase">
                    <th className="py-4 px-6 text-center w-[100px]">Сортировка</th>
                    <th className="py-4 px-6 w-[60px]">Позиция</th>
                    <th className="py-4 px-6">Название локации</th>
                    <th className="py-4 px-6 text-center w-[120px]">Действия</th>
                  </tr>
                </thead>
                <tbody className="divide-y text-sm">
                  {(!data.points || data.points.length === 0) ? (
                    <tr>
                      <td colSpan={4} className="py-12 text-center text-gray-400 italic">Точки еще не добавлены.</td>
                    </tr>
                  ) : (
                    data.points.map((p, idx) => (
                      <tr key={p.id || idx} className="hover:bg-gray-50/50">
                        <td className="py-4 px-6 text-center">
                          <button type="button" disabled={idx === 0} onClick={() => movePoint(idx, 'up')} className="mr-1 opacity-60 disabled:opacity-20">🔼</button>
                          <button type="button" disabled={idx === (data.points?.length || 0) - 1} onClick={() => movePoint(idx, 'down')} className="opacity-60 disabled:opacity-20">🔽</button>
                        </td>
                        <td className="py-4 px-6 font-bold text-gray-400">{p.position}</td>
                        <td className="py-4 px-6 font-semibold text-gray-800">{p.contents?.[0]?.name || 'Без названия'}</td>
                        <td className="py-4 px-6 text-center">
                          <button type="button" onClick={() => { setEditingPoint(p); setEditingPointIndex(idx); setScreenMode('POINT_FORM'); }} className="text-blue-600 mr-3">✎</button>
                          <button type="button" onClick={() => handleDeletePoint(idx)} className="text-red-600">🗑</button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};