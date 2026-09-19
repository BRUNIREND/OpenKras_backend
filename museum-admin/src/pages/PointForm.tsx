import React, { useState } from 'react';
import api from '../api/axios';
import { ImageGalleryUploader } from '../components/ImageGalleryUploader';
import type { Point, PointContent, MediaObject } from '../types/api';

interface PointFormProps {
  point?: Partial<Point>;
  onSave: (pointData: Partial<Point>) => void;
  onCancel: () => void;
}


export const PointForm: React.FC<PointFormProps> = ({ point, onSave, onCancel }) => {
  // Координаты и радиус
  const [latitude, setLatitude] = useState(point?.latitude?.toString() || '');
  const [longitude, setLongitude] = useState(point?.longitude?.toString() || '');
  const [radius, setRadius] = useState(point?.radius_meters?.toString() || '20');
  
  // Текстовый контент локации
  const [name, setName] = useState(point?.contents?.[0]?.name || '');
  const [description, setDescription] = useState(point?.contents?.[0]?.description || '');
  const [address, setAddress] = useState(point?.contents?.[0]?.address || '');
  
  // Картинки локации (работаем со списком MediaObject[])
  const [pointImages, setPointImages] = useState<MediaObject[]>(point?.contents?.[0]?.images || []);
  
  // Аудиогид локации (храним объект целиком для отображения плеера/ссылки)
  const [audioFile, setAudioFile] = useState<MediaObject | null>(point?.contents?.[0]?.audio || null);
  const [isUploadingAudio, setIsUploadingAudio] = useState(false);

  // --- Загрузка аудиофайла на бэкенд ---
  const handleAudioUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;
    const file = e.target.files[0];

    const formData = new FormData();
    formData.append('file', file);
    formData.append('media_type', 'audio');

    try {
      setIsUploadingAudio(true);
      
      const response = await api.post<MediaObject>('/admin/media', formData );
      // Бэкенд возвращает полный объект { id, file_url, media_type }
      setAudioFile(response.data);
      alert('Аудиогид успешно загружен на сервер!');
    } catch (err) {
      console.error(err);
      alert('Не удалось загрузить аудиофайл');
    } finally {
      setIsUploadingAudio(false);
      e.target.value = '';
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Формируем чистый контент для отправки/сохранения в стейте редактора
    const pointContent: Partial<PointContent> = {
      lang: 'ru',
      name,
      description,
      address,
      // Для отображения в превью оставляем объекты:
      audio: audioFile || undefined,
      images: pointImages,
      // Для валидации бэкенда при сохранении подкладываем ID:
      media_ids: pointImages.map(img => img.id)
    };

    const updatedPoint: Partial<Point> = {
      ...point, // Сохраняем временный id или id из БД, если он был
      latitude: parseFloat(latitude),
      longitude: parseFloat(longitude),
      radius_meters: parseInt(radius, 10) || 20,
      contents: [pointContent as PointContent]
    };

    onSave(updatedPoint);
  };

  return (
    <div className="max-w-3xl mx-auto bg-white p-8 rounded-2xl border border-gray-200 shadow-sm">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-xl font-bold text-gray-900">
          {point?.id ? 'Редактирование локации' : 'Новая точка маршрута'}
        </h3>
        <button type="button" onClick={onCancel} className="text-sm text-gray-400 hover:text-gray-600">
          Отмена
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Текстовые поля локации */}
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-1.5">Название локации</label>
            <input 
              type="text" required value={name} onChange={(e) => setName(e.target.value)}
              className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl outline-none focus:border-gray-400 text-sm"
              placeholder="Например: Зал этнографии или Памятник архитектуры"
            />
          </div>
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-1.5">Адрес</label>
            <input 
              type="text" value={address} onChange={(e) => setAddress(e.target.value)}
              className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl outline-none focus:border-gray-400 text-sm"
              placeholder="Например: Цокольный этаж, экспозиция №3"
            />
          </div>
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-1.5">Описание локации</label>
            <textarea 
              value={description} onChange={(e) => setDescription(e.target.value)} rows={4}
              className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl outline-none focus:border-gray-400 text-sm resize-none"
              placeholder="Расскажите историю этого места для мобильного гида..."
            />
          </div>
        </div>

        <hr className="border-gray-100" />

        {/* Геоданные / Метки позиционирования */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-1.5">Широта (Latitude)</label>
            <input 
              type="number" step="any" required value={latitude} onChange={(e) => setLatitude(e.target.value)}
              className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl outline-none focus:border-gray-400 text-sm font-mono"
              placeholder="56.0104"
            />
          </div>
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-1.5">Долгота (Longitude)</label>
            <input 
              type="number" step="any" required value={longitude} onChange={(e) => setLongitude(e.target.value)}
              className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl outline-none focus:border-gray-400 text-sm font-mono"
              placeholder="92.8686"
            />
          </div>
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-1.5">Радиус активации (м)</label>
            <input 
              type="number" required value={radius} onChange={(e) => setRadius(e.target.value)}
              className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl outline-none focus:border-gray-400 text-sm"
              placeholder="20"
            />
          </div>
        </div>

        <hr className="border-gray-100" />

        {/* Загрузка галереи для конкретной точки */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">Фотографии локации</label>
          <ImageGalleryUploader 
            images={pointImages}
            onChange={(updatedImages: MediaObject[]) => setPointImages(updatedImages)}
          />
        </div>

        {/* Интерактивный блок загрузки аудиогида */}
        <div className="p-4 bg-blue-50/40 border border-blue-100 rounded-2xl flex items-center justify-between">
          <div className="flex items-center gap-3 overflow-hidden mr-4">
            <span className="text-xl flex-shrink-0">🎵</span>
            <div className="overflow-hidden">
              <p className="text-xs font-bold text-gray-700">
                {isUploadingAudio ? '⏳ Аудиофайл загружается на сервер...' : audioFile ? '🔥 Аудиогид успешно прикреплен' : 'Аудиогид для точки'}
              </p>
              <p className="text-[11px] text-gray-400 truncate max-w-sm font-mono">
                {audioFile ? audioFile.file_url : 'Допускаются файлы формата .mp3, .wav или .ogg'}
              </p>
            </div>
          </div>
          <div className="flex gap-2 flex-shrink-0">
            {audioFile && (
              <button 
                type="button" 
                onClick={() => setAudioFile(null)}
                className="px-3 py-1.5 bg-red-50 text-red-600 border border-red-100 rounded-xl text-xs font-medium hover:bg-red-100 transition"
              >
                Удалить
              </button>
            )}
            <label className="px-4 py-1.5 bg-white border border-gray-200 rounded-xl text-xs font-semibold hover:bg-gray-50 cursor-pointer shadow-sm transition">
              <input 
                type="file" 
                accept=".mp3,.wav,.ogg" 
                className="hidden" 
                onChange={handleAudioUpload} 
                disabled={isUploadingAudio} 
              />
              {audioFile ? 'Изменить' : 'Выбрать файл'}
            </label>
          </div>
        </div>

        {/* Панель кнопок */}
        <div className="flex justify-end gap-3 pt-4 border-t border-gray-50">
          <button 
            type="button" onClick={onCancel}
            className="px-5 py-2.5 border border-gray-200 rounded-xl text-sm font-medium hover:bg-gray-50 transition"
          >
            Назад к списку
          </button>
          <button 
            type="submit"
            disabled={isUploadingAudio}
            className="px-6 py-2.5 bg-[#801020] text-white rounded-xl text-sm font-semibold hover:bg-[#660d1a] disabled:bg-gray-200 disabled:text-gray-400 transition shadow-sm"
          >
            Сохранить точку
          </button>
        </div>
      </form>
    </div>
  );
};