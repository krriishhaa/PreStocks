// PreStocks — Router Module (SPA client-side routing)

const routes = new Map();
let currentRoute = '/';

function register(path, handler) {
  routes.set(path, handler);
}

function navigate(path, pushState = true) {
  currentRoute = path;
  if (pushState) window.history.pushState({ path }, '', `#${path}`);
  const handler = routes.get(path);
  if (handler) handler();
}

function getCurrentRoute() { return currentRoute; }

function init() {
  window.addEventListener('popstate', (e) => {
    const path = e.state?.path || '/';
    navigate(path, false);
  });

  const hash = window.location.hash.slice(1);
  if (hash && routes.has(hash)) {
    navigate(hash, false);
  }
}

export { register, navigate, getCurrentRoute, init };
