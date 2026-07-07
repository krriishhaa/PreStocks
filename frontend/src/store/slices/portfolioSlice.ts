import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { Portfolio, Holding } from '@/types';

interface PortfolioState {
  portfolio: Portfolio | null;
  holdings: Holding[];
  loading: boolean;
  error: string | null;
}

const initialState: PortfolioState = {
  portfolio: null,
  holdings: [],
  loading: false,
  error: null,
};

const portfolioSlice = createSlice({
  name: 'portfolio',
  initialState,
  reducers: {
    setPortfolio: (state, action: PayloadAction<Portfolio>) => {
      state.portfolio = action.payload;
    },
    setHoldings: (state, action: PayloadAction<Holding[]>) => {
      state.holdings = action.payload;
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload;
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },
  },
});

export const { setPortfolio, setHoldings, setLoading, setError } = portfolioSlice.actions;
export default portfolioSlice.reducer;
