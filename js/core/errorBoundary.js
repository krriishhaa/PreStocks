// PreStocks — Error Boundary (global error handling)

let errorContainer = null;

function init() {
  errorContainer = document.getElementById('error-boundary');

  window.addEventListener('error', (event) => {
    console.error('[ErrorBoundary] Uncaught error:', event.error);
    showFallback(event.message, event.filename, event.lineno);
  });

  window.addEventListener('unhandledrejection', (event) => {
    console.error('[ErrorBoundary] Unhandled promise rejection:', event.reason);
    showFallback(event.reason?.message || 'Async operation failed');
  });
}

function showFallback(message, file, line) {
  if (!errorContainer) return;
  errorContainer.style.display = 'block';
  errorContainer.innerHTML = `
    <div class="error-boundary-content">
      <svg width="48" height="48" fill="none" stroke="var(--color-danger)" stroke-width="1.5"><circle cx="24" cy="24" r="20"/><path d="M24 16v8m0 4h.01"/></svg>
      <h3>Something went wrong</h3>
      <p>${message || 'An unexpected error occurred.'}</p>
      <button class="btn btn-primary btn-md" onclick="location.reload()">Reload Page</button>
    </div>
  `;
}

function clearError() {
  if (errorContainer) {
    errorContainer.style.display = 'none';
    errorContainer.innerHTML = '';
  }
}

export { init, showFallback, clearError };
