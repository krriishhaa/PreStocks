export interface Holding {
  symbol: string;
  name: string;
  shares: number;
  avgCost: number;
  currentPrice: number;
  totalValue: number;
  totalReturn: number;
  totalReturnPercent: number;
  dayChange: number;
  dayChangePercent: number;
}

export interface Transaction {
  id: string;
  symbol: string;
  action: "buy" | "sell";
  shares: number;
  price: number;
  total: number;
  timestamp: string;
  status: "filled" | "pending" | "cancelled";
}

export interface Portfolio {
  totalValue: number;
  cashBalance: number;
  dayChange: number;
  dayChangePercent: number;
  totalReturn: number;
  totalReturnPercent: number;
  holdings: Holding[];
  transactions: Transaction[];
}

export interface PortfolioChartPoint {
  date: string;
  value: number;
}
