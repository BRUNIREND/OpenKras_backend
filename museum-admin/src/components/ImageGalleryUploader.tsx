import React, { useState } from 'react';
import api from '../api/axios';
import type { MediaObject } from '../types/api';

interface ImageGalleryUploaderProps {
  images: MediaObject[]; 
  onChange: (updatedImages: MediaObject[]) => void;
}

export const ImageGalleryUploader: React.FC<ImageGalleryUploaderProps> = ({ images, onChange }) => {
  const [isUploading, setIsUploading] = useState(false);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;
    const files = Array.from(e.target.files);
    setIsUploading(false);

    try {
      const uploadedMedia: MediaObject[] = [...images];

      for (const file of files) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('media_type', 'image');

        const response = await api.post('/admin/media', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        
        
        uploadedMedia.push(response.data); 
      }

      onChange(uploadedMedia);
    } catch (err) {
      alert('Ошибка при загрузке изображений');
    } finally {
      setIsUploading(false);
      e.target.value = '';
    }
  };

  const handleDeleteImage = async (mediaId: number, index: number) => {
    try {
      // Отправляем запрос на удаление в API
      await api.delete(`/admin/media/${mediaId}`);
      
      // Если бэк успешно удалил, убираем из локального стейта фронтенда
      const updatedImages = images.filter((_, i) => i !== index);
      onChange(updatedImages);
      
      alert('Изображение физически удалено с сервера');
    } catch (err) {
      console.error(err);
      alert('Не удалось удалить файл с сервера. Возможно, он используется в другом маршруте.');
    }
  };

  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
      {images.map((img, idx) => (
        <div key={`gallery-item-${idx}-${img.id || ''}`} className="relative aspect-video rounded-xl overflow-hidden border border-gray-200 group">
          <img src={img.file_url} alt="" className="w-full h-full object-cover" /> {/* 👈 Достаем url */}
          <button
            type="button"
            onClick={() => handleDeleteImage(img.id, idx)}
            className="absolute top-1.5 right-1.5 bg-black/60 text-white p-1 rounded-md text-[10px] opacity-0 group-hover:opacity-100 transition-opacity"
          >
            ✕
          </button>
        </div>
      ))}
      <label className="aspect-video border-2 border-dashed border-gray-200 rounded-xl flex flex-col items-center justify-center text-gray-400 cursor-pointer hover:bg-gray-50 transition">
        <input type="file" accept=".jpg,.jpeg,.png,.webp" multiple className="hidden" onChange={handleFileChange} />
        <span className="text-xl">{isUploading ? '⏳' : '⊕'}</span>
      </label>
    </div>
  );
};