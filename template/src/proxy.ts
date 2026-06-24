import { auth } from "@/lib/auth";
import createIntlMiddleware from "next-intl/middleware";
import { routing } from "@/i18n/routing";
import { NextResponse } from "next/server";

const intlMiddleware = createIntlMiddleware(routing);

// Public pages that don't require authentication
const PUBLIC_PAGES = ["/login", "/signup"];

function isAuthPage(pathname: string): boolean {
  return PUBLIC_PAGES.some((page) => pathname.endsWith(page));
}

function isRootLocalePage(pathname: string): boolean {
  // Matches /pt-BR or /en (with optional trailing slash) but NOT /pt-BR/dashboard etc.
  const segments = pathname.split("/").filter(Boolean);
  if (segments.length === 0) return true; // "/"
  if (segments.length === 1 && routing.locales.includes(segments[0] as never)) {
    return true; // "/pt-BR" or "/en"
  }
  return false;
}

function getLocaleFromPath(pathname: string): string {
  const segment = pathname.split("/")[1];
  return routing.locales.includes(segment as never) ? segment : routing.defaultLocale;
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export default auth((req: any) => {
  const { pathname } = req.nextUrl;

  // Let next-intl handle locale detection + rewriting
  const response = intlMiddleware(req);

  const isAuth = !!req.auth;
  const isAuthRoute = isAuthPage(pathname);
  const isLanding = isRootLocalePage(pathname);

  // Landing page is public — always allow
  if (isLanding) {
    return response;
  }

  // Not authenticated + trying to access protected page → redirect to login
  if (!isAuth && !isAuthRoute && !pathname.startsWith("/api")) {
    const locale = getLocaleFromPath(pathname);
    const loginUrl = new URL(`/${locale}/login`, req.url);
    return NextResponse.redirect(loginUrl);
  }

  // Authenticated + trying to access login/signup → redirect to dashboard
  if (isAuth && isAuthRoute) {
    const locale = getLocaleFromPath(pathname);
    const homeUrl = new URL(`/${locale}/dashboard`, req.url);
    return NextResponse.redirect(homeUrl);
  }

  return response;
});

export const config = {
  matcher: ["/((?!api|_next|_vercel|.*\\..*).*)"],
};
