import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import type { RiskFlag, CompositeRiskScore, FlagsState } from "@/types/flags";

const initialState: FlagsState = {
  flags: [],
  compositeScores: {},
  isLoading: false,
  error: null,
};

const flagsSlice = createSlice({
  name: "flags",
  initialState,
  reducers: {
    setFlags(state, action: PayloadAction<RiskFlag[]>) {
      state.flags = action.payload;
      state.isLoading = false;
    },
    addFlag(state, action: PayloadAction<RiskFlag>) {
      state.flags.unshift(action.payload);
    },
    resolveFlag(state, action: PayloadAction<string>) {
      const flag = state.flags.find((f) => f.id === action.payload);
      if (flag) flag.resolved = true;
    },
    setCompositeScore(state, action: PayloadAction<CompositeRiskScore>) {
      state.compositeScores[action.payload.symbol] = action.payload;
    },
    setMultipleScores(state, action: PayloadAction<CompositeRiskScore[]>) {
      for (const score of action.payload) {
        state.compositeScores[score.symbol] = score;
      }
    },
    setLoading(state, action: PayloadAction<boolean>) {
      state.isLoading = action.payload;
    },
    setError(state, action: PayloadAction<string>) {
      state.error = action.payload;
      state.isLoading = false;
    },
  },
});

export const {
  setFlags,
  addFlag,
  resolveFlag,
  setCompositeScore,
  setMultipleScores,
  setLoading,
  setError,
} = flagsSlice.actions;
export default flagsSlice.reducer;
