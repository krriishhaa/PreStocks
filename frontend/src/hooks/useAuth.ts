import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '@/store/store';
import { setUser, logout as logoutAction } from '@/store/slices/authSlice';
import apiClient from '@/utils/api';

export function useAuth() {
  const dispatch = useDispatch();
  const { user, isAuthenticated, loading, error } = useSelector((state: RootState) => state.auth);

  const login = async (email: string, password: string) => {
    const response = await apiClient.post('/auth/login', { email, password });
    const { access_token, refresh_token } = response.data;
    localStorage.setItem('access_token', access_token);
    localStorage.setItem('refresh_token', refresh_token);
    // Fetch user profile
    const userResponse = await apiClient.get('/users/me');
    dispatch(setUser(userResponse.data));
    return response.data;
  };

  const signup = async (data: { email: string; password: string; full_name?: string; age?: number }) => {
    const response = await apiClient.post('/auth/signup', data);
    const { access_token, refresh_token } = response.data;
    localStorage.setItem('access_token', access_token);
    localStorage.setItem('refresh_token', refresh_token);
    return response.data;
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    dispatch(logoutAction());
  };

  return { user, isAuthenticated, loading, error, login, signup, logout };
}
