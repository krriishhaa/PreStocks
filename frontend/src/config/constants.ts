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

export const RISK_LEVELS = {
  low: { label: 'Low Risk', color: '#10B981', bg: 'rgba(16,185,129,0.1)' },
  medium: { label: 'Medium Risk', color: '#F59E0B', bg: 'rgba(245,158,11,0.1)' },
  high: { label: 'High Risk', color: '#EF4444', bg: 'rgba(239,68,68,0.1)' },
  critical: { label: 'Critical', color: '#7C3AED', bg: 'rgba(124,58,237,0.1)' },
} as const;
