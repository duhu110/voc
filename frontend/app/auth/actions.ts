"use server";

import { cookies } from "next/headers";
import { redirect } from "next/navigation";

const AUTH_COOKIE_NAME = "voc_access_token";
const BACKEND_API_URL =
	process.env.BACKEND_API_URL ?? "http://127.0.0.1:8010";

type LoginActionState = {
	error?: string;
	errorId?: number;
};

type LoginResponse = {
	status: string;
	access_token?: string;
	token_type?: string;
	expires_in?: number;
};

export async function login(
	_prevState: LoginActionState,
	formData: FormData
): Promise<LoginActionState> {
	const username = String(formData.get("username") ?? "").trim();
	const password = String(formData.get("password") ?? "");

	if (!username || !password) {
		return { error: "请输入用户名和密码。", errorId: Date.now() };
	}

	let response: Response;
	try {
		response = await fetch(`${BACKEND_API_URL}/auth/login`, {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
			},
			body: JSON.stringify({ username, password }),
			cache: "no-store",
		});
	} catch {
		return {
			error: "无法连接后端认证服务，请确认 backend_api 已启动。",
			errorId: Date.now(),
		};
	}

	if (!response.ok) {
		return {
			error: "用户名或密码不正确，或账号当前不可用。",
			errorId: Date.now(),
		};
	}

	const payload = (await response.json()) as LoginResponse;
	if (payload.status !== "success" || !payload.access_token) {
		return { error: "后端登录响应缺少访问令牌。", errorId: Date.now() };
	}

	const cookieStore = await cookies();
	cookieStore.set(AUTH_COOKIE_NAME, payload.access_token, {
		httpOnly: true,
		maxAge: payload.expires_in ?? 60 * 60,
		path: "/",
		sameSite: "lax",
		secure: process.env.NODE_ENV === "production",
	});

	redirect("/");
}
