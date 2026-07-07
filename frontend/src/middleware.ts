import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

const PROTECTED_PATHS = ['/app'];
const AUTH_PATHS = ['/auth/login', '/auth/signup'];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const token = request.cookies.get('ps_token')?.value;

  // Redirect authenticated users away from auth pages
  if (AUTH_PATHS.some(p => pathname.startsWith(p)) && token) {
    return NextResponse.redirect(new URL('/app/dashboard', request.url));
  }

  // Protect /app/* routes — redirect to login if no token
  if (PROTECTED_PATHS.some(p => pathname.startsWith(p)) && !token) {
    const loginUrl = new URL('/auth/login', request.url);
    loginUrl.searchParams.set('redirect', pathname);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/app/:path*', '/auth/:path*'],
};
