import  { useState } from 'react';
import { Login } from './pages/Login';
import { Excursions } from './pages/Excursions';

function App() {
  const [token, setToken] = useState<string | null>(localStorage.getItem('admin_token'));

  const handleLoginSuccess = (newToken: string) => {
    setToken(newToken);
  };

  const handleLogout = () => {
    localStorage.removeItem('admin_token');
    setToken(null);
  };

  return (
    <>
      {!token ? (
        <Login onLoginSuccess={handleLoginSuccess} />
      ) : (
        <Excursions onLogout={handleLogout} />
      )}
    </>
  );
}

export default App;