import React, { useState, useEffect } from 'react';
import api from '../api/axios';
import type { Category } from '../types/api';

export const CategoryManager: React.FC = () => {
  const [categories, setCategories] = useState<Category[]>([]);
  const [newCategoryName, setNewCategoryName] = useState('');
  const [loading, setLoading] = useState(false);

  // Загрузка списка категорий
  const fetchCategories = async () => {
    try {
      setLoading(true);
      const response = await api.get<Category[]>('/admin/categories');
      setCategories(response.data);
    } catch (err) {
      console.error('Ошибка при загрузке категорий:', err);
      alert('Не удалось загрузить категории');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCategories();
  }, []);

  // Создание категории
  const handleCreateCategory = async (e: React.FormEvent) => {
    e.preventDefault();
    const name = newCategoryName.trim();
    if (!name) return;

    try {
      setLoading(true);
      await api.post('/admin/categories', { name });
      setNewCategoryName('');
      await fetchCategories();
    } catch (err: any) {
      if (err.response?.status === 409) {
        alert('Категория с таким названием уже существует');
      } else {
        alert('Ошибка при создании категории');
      }
    } finally {
      setLoading(false);
    }
  };

  // Удаление категории
  const handleDeleteCategory = async (categoryId: number, categoryName: string) => {
    if (!window.confirm(`Удалить категорию «${categoryName}»?`)) return;

    try {
      setLoading(true);
      await api.delete(`/admin/categories/${categoryId}`);
      // Удаляем из локального стейта без повторной загрузки всего списка (для скорости)
      setCategories(prev => prev.filter(cat => cat.id !== categoryId));
    } catch (err: any) {
      if (err.response?.status === 404) {
        alert('Категория не найдена');
      } else {
        alert('Ошибка при удалении категории');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
      <div className="bg-gray-50 p-6 rounded-2xl border border-gray-200">
        <h3 className="text-sm font-bold uppercase tracking-wider text-gray-500 mb-4">
          Управление категориями
        </h3>

        <form onSubmit={handleCreateCategory} className="flex gap-2 mb-4">
          <input
              type="text"
              value={newCategoryName}
              onChange={(e) => setNewCategoryName(e.target.value)}
              placeholder="Новая категория..."
              className="flex-1 px-3 py-2 bg-white border border-gray-200 rounded-xl text-xs outline-none focus:border-gray-400"
              disabled={loading}
          />
          <button
              type="submit"
              disabled={loading || !newCategoryName.trim()}
              className="px-3 py-2 bg-[#801020] text-white rounded-xl text-xs font-medium disabled:opacity-50"
          >
            +
          </button>
        </form>

        <div className="space-y-1.5 max-h-40 overflow-y-auto">
          {categories.length === 0 ? (
              <p className="text-xs text-gray-400 italic px-2">Нет категорий</p>
          ) : (
              categories.map(cat => (
                  <div
                      key={cat.id}
                      className="flex justify-between items-center bg-white px-3 py-2 rounded-lg border border-gray-100 text-xs text-gray-700"
                  >
                    <span>{cat.name}</span>
                    <button
                        type="button"
                        onClick={() => handleDeleteCategory(cat.id, cat.name)}
                        disabled={loading}
                        className="text-red-400 hover:text-red-600 transition disabled:opacity-30"
                        title="Удалить категорию"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                      </svg>
                    </button>
                  </div>
              ))
          )}
        </div>
      </div>
  );
};