import { cookies } from "next/headers";

export const AUTH_COOKIE_NAME = "voc_access_token";
const BACKEND_API_URL =
	process.env.BACKEND_API_URL ?? "http://127.0.0.1:8010";

export type CurrentUser = {
	id: number;
	username: string;
	display_name?: string | null;
	role: "admin" | "operator" | "viewer" | string;
	status: string;
};

type MeResponse = {
	status: string;
	user?: CurrentUser;
};

export async function getCurrentUser(): Promise<CurrentUser | null> {
	const cookieStore = await cookies();
	const token = cookieStore.get(AUTH_COOKIE_NAME)?.value;

	if (!token) {
		return null;
	}

	try {
		const response = await fetch(`${BACKEND_API_URL}/auth/me`, {
			headers: {
				Authorization: `Bearer ${token}`,
			},
			cache: "no-store",
		});

		if (!response.ok) {
			return null;
		}

		const payload = (await response.json()) as MeResponse;
		return payload.status === "success" && payload.user ? payload.user : null;
	} catch {
		return null;
	}
}
