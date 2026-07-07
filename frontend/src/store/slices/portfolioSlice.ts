import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { api } from '@/utils/api';
import type { PortfolioFull, Trade } from '@/types/portfolio';

interface PortfolioState {
  data: PortfolioFull | null;
  trades: Trade[];
  loading: boolean;
  error: string | null;
}

const initialState: PortfolioState = {
  data: null,
  trades: [],
  loading: false,
  error: null,
};

export const fetchPortfolio = createAsyncThunk('portfolio/fetch', async () => {
  const { data } = await api.get<PortfolioFull>('/portfolio');
  return data;
});

export const fetchTrades = createAsyncThunk('portfolio/fetchTrades', async () => {
  const { data } = await api.get<Trade[]>('/portfolio/trades');
  return data;
});

const portfolioSlice = createSlice({
  name: 'portfolio',
  initialState,
  reducers: {
    clearPortfolio: (state) => {
      state.data = null;
      state.trades = [];
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchPortfolio.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchPortfolio.fulfilled, (state, action) => {
        state.data = action.payload;
        state.loading = false;
      })
      .addCase(fetchPortfolio.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to load portfolio';
      })
      .addCase(fetchTrades.fulfilled, (state, action) => {
        state.trades = action.payload;
      });
  },
});

export const { clearPortfolio } = portfolioSlice.actions;
export default portfolioSlice.reducer;
