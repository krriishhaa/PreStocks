export interface Holding {
  id: number;
  symbol: string;
  company_name: string | null;
  shares: number;
  avg_buy_price: number;
  current_price: number | null;
  market_value: number;
  unrealized_pnl: number;
  unrealized_pnl_pct: number;
}

export interface Trade {
  id: number;
  symbol: string;
  company_name: string | null;
  side: "buy" | "sell";
  order_type: string;
  shares: number;
  price: number;
  total_amount: number;
  status: string;
  executed_at: string;
}

export interface PortfolioSummary {
  total_value: number;
  cash: number;
  invested: number;
  pnl: number;
  pnl_pct: number;
  positions: number;
  initial_capital: number;
}

export interface PortfolioFull {
  id: number;
  name: string;
  cash: number;
  initial_capital: number;
  total_value: number;
  total_invested: number;
  unrealized_pnl: number;
  positions: number;
  holdings: Holding[];
}

export interface PortfolioChartPoint {
  date: string;
  value: number;
}
