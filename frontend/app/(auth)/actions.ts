"use server";

import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { AUTH_COOKIE_NAME } from "@/app/(auth)/auth";

export async function logout() {
	const cookieStore = await cookies();
	cookieStore.delete(AUTH_COOKIE_NAME);

	redirect("/auth");
}
