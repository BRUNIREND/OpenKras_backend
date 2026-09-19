import React, { useState } from 'react';
import api from '../api/axios';
import type { LoginResponse } from '../types/api';

interface LoginProps {
  onLoginSuccess: (token: string) => void;
}
interface MuseumIconProps {
  className?: string;
  size?: number;
}

export const MuseumIcon: React.FC<MuseumIconProps> = ({ className = '', size = 120 }) => {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      width={size}
      height={size}
      fill="none"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={`text-[#801020] ${className}`} // По умолчанию красим в твой бордовый цвет
    >
      {/* Треугольный фронтон (крыша) */}
      <polygon points="12 2 2 7 22 7" fill="currentColor" fillOpacity="1" />
      
      {/* Архитрав (балка под крышей) */}
      
      {/* Колонны музея */}
      <line x1="6" y1="9" x2="6" y2="19" strokeWidth="2" />
      <line x1="10" y1="9" x2="10" y2="19" strokeWidth="2" />
      <line x1="14" y1="9" x2="14" y2="19" strokeWidth="2" />
      <line x1="18" y1="9" x2="18" y2="19" strokeWidth="2" />
      
      {/* Ступени / Основание здания */}
      <line x1="2" y1="19" x2="22" y2="19" />
      <line x1="1" y1="20" x2="23" y2="20" />
    </svg>
  );
};

export const Login: React.FC<LoginProps> = ({ onLoginSuccess }) => {
  const [email, setEmail] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [error, setError] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError('');

        try {
        const response = await api.post<LoginResponse>('/auth/login', {
            email: email,       
            password: password,
        });

        const { access_token } = response.data;

        // Сохраняем токен и меняем состояние приложения
        localStorage.setItem('admin_token', access_token);

        api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
        onLoginSuccess(access_token);
        } catch (err: any) {
            if (err.response && err.response.data && err.response.data.detail) {
                setError(err.response.data.detail);
            } else {
                setError('Неверный логин, пароль или отсутствуют права администратора.');
            }
            } finally {
            setIsLoading(false);
        }
    };

  return (
    
    <div className="flex items-center justify-center min-h-screen bg-white">
      
      <div className="w-full max-w-[420px] p-10 bg-white rounded-3xl shadow-[0_8px_30px_rgba(0,0,0,0.05)] border border-gray-100 flex flex-col items-center">
        
        
        <div className="flex justify-center items-center mb-4 text-[#801020]">
          <MuseumIcon/>
        </div>

        <h2 className="text-2xl font-bold text-gray-800 text-center mb-1">
          Музейный гид
        </h2>
        <p className="text-sm text-gray-500 text-center mb-9">
          Админ-панель управления маршрутами
        </p>
        
        {error && (
          <div className="w-full p-3 mb-4 text-xs text-red-600 bg-red-50 rounded-xl border border-red-100 text-center">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="w-full space-y-6">
          
          <div className="flex flex-col">
            <label className="text-sm font-medium text-gray-600 mb-2 pl-1">
              Логин
            </label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-2.5 bg-white border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-100 focus:border-blue-400 outline-none text-gray-900 placeholder-gray-400 transition shadow-inner"
              placeholder="museum@example.com"
            />
          </div>

          <div className="flex flex-col">
            <label className="text-sm font-medium text-gray-600 mb-2 pl-1">
              Пароль
            </label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-2.5 bg-white border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-100 focus:border-blue-400 outline-none text-gray-900 placeholder-gray-400 transition shadow-inner"
              placeholder="••••••"
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className={`w-full py-3 px-4 font-medium text-white bg-[#801020] hover:bg-[#660a18] active:scale-[0.98] rounded-xl transition-all shadow-md ${
              isLoading ? 'opacity-60 cursor-not-allowed' : ''
            }`}
          >
            {isLoading ? 'Вход...' : 'Войти в панель'}
          </button>
        </form>

        

      </div>
    </div>
  );
};