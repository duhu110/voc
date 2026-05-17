import { cookies } from "next/headers";

import { AUTH_COOKIE_NAME } from "@/app/(auth)/auth";

export const BACKEND_API_URL =
	process.env.BACKEND_API_URL ?? "http://127.0.0.1:8010";

export type ApiResult<T> =
	| { ok: true; data: T }
	| { ok: false; error: string; status?: number };

export async function backendFetch<T>(
	path: string,
	init: RequestInit = {}
): Promise<ApiResult<T>> {
	const cookieStore = await cookies();
	const token = cookieStore.get(AUTH_COOKIE_NAME)?.value;
	const headers = new Headers(init.headers);

	if (token) {
		headers.set("Authorization", `Bearer ${token}`);
	}

	try {
		const response = await fetch(`${BACKEND_API_URL}${path}`, {
			...init,
			headers,
			cache: "no-store",
		});
		const payload = (await response.json().catch(() => null)) as
			| (T & { detail?: string; message?: string })
			| null;

		if (!response.ok || !payload) {
			return {
				ok: false,
				status: response.status,
				error:
					payload?.detail ??
					payload?.message ??
					`后端接口返回 ${response.status}`,
			};
		}

		return { ok: true, data: payload };
	} catch {
		return { ok: false, error: "无法连接 backend_api，请确认服务已启动。" };
	}
}

export function firstParam(
	value: string | string[] | undefined,
	fallback = ""
) {
	if (Array.isArray(value)) {
		return value[0] ?? fallback;
	}
	return value ?? fallback;
}
