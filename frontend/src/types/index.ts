export type { User } from './user';
export type { Stock, PricePoint } from './stock';
export type { RiskFlag, CompositeRiskScore } from './flags';
export type { Holding, Trade, PortfolioFull, PortfolioSummary } from './portfolio';

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface RiskProfile {
  id: number;
  user_id: number;
  risk_tolerance_score: number;
  knowledge_level: number;
}
