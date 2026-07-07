// PreStocks — Design System Tokens (JS access to design tokens)

export const colors = {
  primary: '#1E40AF',
  primaryHover: '#1530A8',
  primaryLight: '#DBEAFE',
  primarySurface: '#EFF6FF',
  success: '#10B981',
  successLight: '#D1FAE5',
  warning: '#F59E0B',
  warningLight: '#FEF3C7',
  danger: '#EF4444',
  dangerLight: '#FEE2E2',
  gray50: '#F8FAFC',
  gray200: '#E2E8F0',
  gray500: '#64748B',
  gray800: '#1E293B',
};

export const spacing = {
  xs: '4px', sm: '8px', md: '12px', lg: '16px', xl: '20px', '2xl': '24px', '3xl': '32px', '4xl': '40px'
};

export const breakpoints = {
  mobile: 599,
  tablet: 1024,
  desktop: 1440,
  ultrawide: 2560
};

export function isMobile() { return window.innerWidth <= breakpoints.mobile; }
export function isTablet() { return window.innerWidth > breakpoints.mobile && window.innerWidth <= breakpoints.tablet; }
export function isDesktop() { return window.innerWidth > breakpoints.tablet; }
