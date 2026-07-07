export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/';
export const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws';
export const APP_NAME = process.env.NEXT_PUBLIC_APP_NAME || 'PreStocks';

export const STARTING_PORTFOLIO_VALUE = 10000;

export const RISK_TIERS = {
  beginner: 1,
  intermediate: 2,
  advanced: 3,
} as const;

export const RISK_FLAG_TYPES = [
  'volatility',
  'valuation',
  'balance_sheet',
  'insider_activity',
  'short_interest',
  'earnings_risk',
  'liquidity',
  'social_hype',
] as const;
