import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface UiState {
  sidebarOpen: boolean;
  modalOpen: string | null;
  toasts: Array<{ id: string; message: string; type: 'success' | 'error' | 'info' }>;
}

const initialState: UiState = {
  sidebarOpen: true,
  modalOpen: null,
  toasts: [],
};

const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    toggleSidebar: (state) => {
      state.sidebarOpen = !state.sidebarOpen;
    },
    openModal: (state, action: PayloadAction<string>) => {
      state.modalOpen = action.payload;
    },
    closeModal: (state) => {
      state.modalOpen = null;
    },
    addToast: (state, action: PayloadAction<{ id: string; message: string; type: 'success' | 'error' | 'info' }>) => {
      state.toasts.push(action.payload);
    },
    removeToast: (state, action: PayloadAction<string>) => {
      state.toasts = state.toasts.filter(t => t.id !== action.payload);
    },
  },
});

export const { toggleSidebar, openModal, closeModal, addToast, removeToast } = uiSlice.actions;
export default uiSlice.reducer;
