import { useSelector, useDispatch } from 'react-redux';
import { useState } from 'react';
import { RootState } from '@/store/store';
import { setUser, logout as logoutAction } from '@/store/slices/authSlice';
import { api } from '@/utils/api';

export function useAuth() {
  const dispatch = useDispatch();
  const { user, isAuthenticated, loading, error } = useSelector((state: RootState) => state.auth);
  const [isLoading, setIsLoading] = useState(false);

  const login = async (email: string, password: string) => {
    setIsLoading(true);
    try {
      const response = await api.post('/auth/login', { email, password });
      const { access_token, refresh_token } = response.data;
      localStorage.setItem('ps_token', access_token);
      localStorage.setItem('ps_refresh_token', refresh_token);
      const userResponse = await api.get('/users/me');
      dispatch(setUser(userResponse.data));
      return response.data;
    } finally {
      setIsLoading(false);
    }
  };

  const signup = async (data: { email: string; password: string; full_name?: string }) => {
    setIsLoading(true);
    try {
      const response = await api.post('/auth/register', data);
      const { access_token, refresh_token } = response.data;
      localStorage.setItem('ps_token', access_token);
      localStorage.setItem('ps_refresh_token', refresh_token);
      return response.data;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('ps_token');
    localStorage.removeItem('ps_refresh_token');
    dispatch(logoutAction());
  };

  return { user, isAuthenticated, isLoading, loading, error, login, signup, logout };
}
