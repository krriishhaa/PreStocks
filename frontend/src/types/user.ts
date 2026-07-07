export interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
  riskTolerance?: "conservative" | "moderate" | "aggressive";
  createdAt: string;
}

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  token: string | null;
  error: string | null;
}
