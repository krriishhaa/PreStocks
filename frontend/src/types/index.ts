export interface User {
  id: number;
  email: string;
  full_name: string;
  age?: number;
  risk_tier: 'beginner' | 'intermediate' | 'advanced';
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface RiskProfile {
  id: number;
  user_id: number;
  risk_tolerance_score: number;
  knowledge_level: number;
}

export interface Portfolio {
  id: number;
  user_id: number;
  total_value: number;
  cash_available: number;
}

export interface Holding {
  id: number;
  portfolio_id: number;
  stock_id: number;
  ticker: string;
  company_name: string;
  quantity: number;
  average_buy_price: number;
}

export interface Stock {
  id: number;
  ticker: string;
  company_name: string;
  sector: string;
  industry: string;
  market_cap: number;
}

export interface RiskFlag {
  id: number;
  stock_id: number;
  flag_type: string;
  severity_score: number;
  explanation: string;
  confidence_score: number;
}
