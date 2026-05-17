import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const AUTH_COOKIE_NAME = "voc_access_token";
const LOGIN_PATH = "/auth";
const APP_HOME_PATH = "/";

export function proxy(request: NextRequest) {
	const { pathname, search } = request.nextUrl;
	const hasToken = Boolean(request.cookies.get(AUTH_COOKIE_NAME)?.value);
	const isLoginRoute = pathname === LOGIN_PATH;

	if (isLoginRoute && hasToken) {
		return NextResponse.redirect(new URL(APP_HOME_PATH, request.url));
	}

	if (!isLoginRoute && !hasToken) {
		const loginUrl = new URL(LOGIN_PATH, request.url);
		loginUrl.searchParams.set("next", `${pathname}${search}`);
		return NextResponse.redirect(loginUrl);
	}

	return NextResponse.next();
}

export const config = {
	matcher: [
		"/((?!_next/static|_next/image|favicon.ico|sitemap.xml|robots.txt|.*\\..*).*)",
	],
};
