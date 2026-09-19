import React, { useState, useEffect } from 'react';
import api from '../api/axios';
import type { FullExcursion } from '../types/api'; // Используем обновленный тип
import { ExcursionEditor } from './ExcursionEditor';
import {CategoryManager} from "../components/CategoryManager.tsx";

interface ExcursionsProps {
  onLogout: () => void;
}

export const Excursions: React.FC<ExcursionsProps> = ({ onLogout }) => {
  // Меняем тип стейта на FullExcursion[], так как бэкенд возвращает объекты с массивом картинок
  const [excursions, setExcursions] = useState<FullExcursion[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [editingId, setEditingId] = useState<number | null | 'new'>(null);
  const [showCategoryManager, setShowCategoryManager] = useState(false);
  const fetchExcursions = async () => {
    try {
      setIsLoading(true);
      
      // Запрашиваем данные с параметрами пагинации
      const response = await api.get<FullExcursion[]>('/admin/excursions', {
        params: {
          skip: 0,
          limit: 20 
        }
      });
      
      setExcursions(response.data);
    } catch (err) {
      alert('Ошибка при загрузке маршрутов музея. Проверьте параметры skip/limit или модель Media.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchExcursions();
  }, []);

  const handlePublish = async (id: number) => {
    try {
      await api.put(`/admin/excursions/${id}/publish`);
      alert('Маршрут успешно опубликован и доступен в приложении!');
      fetchExcursions();
    } catch (err) {
      alert('Не удалось опубликовать маршрут');
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Вы уверены, что хотите удалить этот маршрут и все связанные точки?')) return;
    try {
      await api.delete(`/admin/excursions/${id}`);
      fetchExcursions();
    } catch (err) {
      alert('Ошибка при удалении маршрута');
    }
  };

  // Если активирован режим редактирования или создания
  if (editingId) {
    return (
      <ExcursionEditor 
        excursionId={editingId === 'new' ? undefined : editingId} 
        onBack={() => {
          setEditingId(null);
          fetchExcursions(); 
        }} 
      />
    );
  }
  return (
    <div className="min-h-screen bg-white font-sans text-gray-900">
      {/* Шапка панели */}
      <header className="max-w-7xl mx-auto px-8 py-6 flex justify-between items-center border-b border-gray-100">
        <div className="flex items-center gap-3">
          <span className="text-xl font-bold tracking-tight text-gray-800">Музейный гид</span>
          <span className="px-2.5 py-1 text-xs font-semibold text-blue-600 bg-blue-50 rounded-md">Admin</span>
        </div>
        <button
          onClick={onLogout}
          className="text-sm font-medium text-gray-500 hover:text-red-600 transition-colors"
        >
          Выйти
        </button>
      </header>

      {/* Основной контент */}
      <main className="max-w-6xl mx-auto px-8 py-12">
        
        {/* Заголовок секции и кнопка создания */}
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-2xl font-bold text-gray-900 tracking-tight">Все маршруты</h1>

          <div className="flex gap-3">
            <button
                onClick={() => setShowCategoryManager(true)}
                className="flex items-center gap-2 bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2.5 rounded-xl font-medium transition text-sm"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24"
                   stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round"
                      d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"/>
              </svg>
              Категории
            </button>
            <button
                onClick={() => setEditingId('new')}
                className="flex items-center gap-2 bg-[#801020] hover:bg-[#660d1a] active:scale-[0.98] text-white px-5 py-3 rounded-2xl font-medium shadow-sm transition-all text-sm"
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2.5}
                   stroke="currentColor" className="w-4 h-4">
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15"/>
              </svg>
              Создать маршрут
            </button>
          </div>
        </div>

        {/* Таблица маршрутов */}
        <div
            className="bg-white border border-gray-200 rounded-2xl overflow-hidden shadow-[0_4px_20px_rgba(0,0,0,0.02)]">
          <table className="w-full text-left border-collapse">
            <thead>
            <tr className="border-b border-gray-200 bg-gray-50/50 text-xs font-semibold text-gray-500 uppercase tracking-wider">
              <th className="py-4 px-6 w-[120px]">Обложка</th>
              <th className="py-4 px-6">Название</th>
              <th className="py-4 px-6">Краткое описание</th>
                <th className="py-4 px-6 w-[140px]">Статус</th>
                <th className="py-4 px-6 w-[160px] text-center">Действия</th>
              </tr>
            </thead>
            
            <tbody className="divide-y divide-gray-100 text-sm">
              {isLoading ? (
                <tr>
                  <td colSpan={5} className="py-10 text-center text-gray-400">
                    Загрузка данных...
                  </td>
                </tr>
              ) : excursions.length === 0 ? (
                <tr>
                  <td colSpan={5} className="py-12 text-center text-gray-400">
                    Маршруты еще не созданы. Нажмите «Создать маршрут», чтобы начать.
                  </td>
                </tr>
              ) : (
                excursions.map((exc) => (
                  <tr key={exc.id} className="hover:bg-gray-50/70 transition-colors">
                    
                    <td className="py-4 px-6">
                      <div className="w-16 h-12 bg-gray-50 rounded-lg border border-gray-200/60 flex items-center justify-center text-gray-400 text-xs overflow-hidden">
                        {exc.images && exc.images.length > 0 ? (
                          <img 
                            src={exc.images[0].file_url} 
                            alt={exc.title} 
                            className="w-full h-full object-cover"
                          />
                        ) : (
                          <span className="text-[10px] text-gray-300 italic">Нет фото</span>
                        )}
                      </div>
                    </td>

                    {/* Название */}
                    <td className="py-4 px-6 font-semibold text-gray-800">
                      {exc.title}
                    </td>

                    {/* Описание */}
                    <td className="py-4 px-6 text-gray-500 max-w-[300px] truncate">
                      {exc.description || <span className="italic text-gray-300">Описания нет</span>}
                    </td>

                    {/* Статус */}
                    <td className="py-4 px-6">
                      <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium ${
                        exc.status === 'published' 
                          ? 'bg-green-50 text-green-700 border border-green-200/50' 
                          : 'bg-amber-50 text-amber-700 border border-amber-200/50'
                      }`}>
                        {exc.status === 'published' ? 'Опубликован' : 'Черновик'}
                      </span>
                    </td>

                    {/* Действия */}
                    <td className="py-4 px-6 text-center">
                      <div className="flex justify-center items-center gap-3 text-gray-500">
                        
                        <button 
                          onClick={() => setEditingId(exc.id)}
                          className="p-1.5 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                          title="Редактировать"
                        >
                          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-[18px] h-[18px]">
                            <path strokeLinecap="round" strokeLinejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L6.832 19.82a4.5 4.5 0 0 1-1.897 1.13l-2.685.8.8-2.685a4.5 4.5 0 0 1 1.13-1.897L16.863 4.487Zm0 0L19.5 7.125" />
                          </svg>
                        </button>

                        {/* Кнопка Удалить */}
                        <button 
                          onClick={() => handleDelete(exc.id)}
                          className="p-1.5 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                          title="Удалить"
                        >
                          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-[18px] h-[18px]">
                            <path strokeLinecap="round" strokeLinejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" />
                          </svg>
                        </button>

                        {/* Кнопка Опубликовать */}
                        {exc.status === 'draft' ? (
                          <button 
                            onClick={() => handlePublish(exc.id)}
                            className="p-1.5 hover:text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                            title="Опубликовать в приложение"
                          >
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-[18px] h-[18px]">
                              <path strokeLinecap="round" strokeLinejoin="round" d="M9 8.25H7.5a2.25 2.25 0 0 0-2.25 2.25v9a2.25 2.25 0 0 0 2.25 2.25h9a2.25 2.25 0 0 0 2.25-2.25v-9a2.25 2.25 0 0 0-2.25-2.25H15m0-3-3-3m0 0-3 3m3-3V15" />
                            </svg>
                          </button>
                        ) : (
                          <div className="w-[30px]" />
                        )}

                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

      </main>
      {/* Модальное окно категорий */}
      {showCategoryManager && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">
            <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full mx-4 p-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-lg font-bold text-gray-900">Управление категориями</h2>
                <button
                    onClick={() => setShowCategoryManager(false)}
                    className="text-gray-400 hover:text-gray-600 transition p-1"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              <CategoryManager />
            </div>
          </div>
      )}
    </div>
  );
};