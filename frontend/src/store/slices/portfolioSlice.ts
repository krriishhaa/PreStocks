import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { Portfolio, Holding, Transaction } from '@/types';

interface PortfolioState {
  portfolio: Portfolio;
  holdings: Holding[];
  loading: boolean;
  error: string | null;
}

const initialPortfolio: Portfolio = {
  totalValue: 100000,
  cashBalance: 85000,
  dayChange: 245.30,
  dayChangePercent: 0.25,
  totalReturn: 1245.30,
  totalReturnPercent: 1.25,
  holdings: [
    { symbol: "STRP", name: "Stripe", shares: 10, avgCost: 850, currentPrice: 892, totalValue: 8920, totalReturn: 420, totalReturnPercent: 4.94, dayChange: 35, dayChangePercent: 0.39 },
    { symbol: "SPCX", name: "SpaceX", shares: 5, avgCost: 1200, currentPrice: 1260, totalValue: 6300, totalReturn: 300, totalReturnPercent: 5.0, dayChange: -12, dayChangePercent: -0.09 },
  ],
  transactions: [],
};

const initialState: PortfolioState = {
  portfolio: initialPortfolio,
  holdings: initialPortfolio.holdings,
  loading: false,
  error: null,
};

const portfolioSlice = createSlice({
  name: 'portfolio',
  initialState,
  reducers: {
    setPortfolio: (state, action: PayloadAction<Portfolio>) => {
      state.portfolio = action.payload;
      state.holdings = action.payload.holdings;
    },
    setHoldings: (state, action: PayloadAction<Holding[]>) => {
      state.holdings = action.payload;
      state.portfolio.holdings = action.payload;
    },
    addTransaction: (state, action: PayloadAction<Transaction>) => {
      state.portfolio.transactions.push(action.payload);
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload;
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },
  },
});

export const { setPortfolio, setHoldings, addTransaction, setLoading, setError } = portfolioSlice.actions;
export default portfolioSlice.reducer;
