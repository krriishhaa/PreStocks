// PreStocks — State Management (Redux-like store pattern)
const listeners = new Set();
let state = {
  user: { tier: 'beginner', name: 'Demo User', avatar: 'DU' },
  ui: { activeView: 'dashboard-view', sidebarOpen: false, theme: 'light' },
  notifications: []
};

function getState() { return state; }

function setState(partial) {
  state = { ...state, ...partial };
  listeners.forEach(fn => fn(state));
}

function subscribe(fn) {
  listeners.add(fn);
  return () => listeners.delete(fn);
}

function dispatch(action) {
  switch (action.type) {
    case 'SET_VIEW':
      setState({ ui: { ...state.ui, activeView: action.payload } });
      break;
    case 'ADD_NOTIFICATION':
      setState({ notifications: [...state.notifications, { ...action.payload, id: Date.now(), read: false }] });
      break;
    case 'DISMISS_NOTIFICATION':
      setState({ notifications: state.notifications.filter(n => n.id !== action.payload) });
      break;
    case 'SET_THEME':
      setState({ ui: { ...state.ui, theme: action.payload } });
      document.documentElement.setAttribute('data-theme', action.payload);
      break;
    default:
      break;
  }
}

export { getState, setState, subscribe, dispatch };
