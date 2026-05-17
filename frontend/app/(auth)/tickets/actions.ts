"use server";

import type { AdviceActionState } from "@/app/(auth)/tickets/types";

const BACKEND_API_URL =
	process.env.BACKEND_API_URL ?? "http://127.0.0.1:8010";

export async function regenerateTicketAdvice(
	_prevState: AdviceActionState,
	formData: FormData
): Promise<AdviceActionState> {
	const ticketId = String(formData.get("ticket_id") ?? "").trim();

	if (!ticketId) {
		return { status: "error", error: "缺少工单编号。" };
	}

	const params = new URLSearchParams({
		use_existing_classification: "true",
		include_processing_context: "false",
		advice_limit: "5",
		sample_limit: "5",
	});

	let response: Response;
	try {
		response = await fetch(
			`${BACKEND_API_URL}/tickets/${encodeURIComponent(ticketId)}/advice?${params}`,
			{
				method: "POST",
				cache: "no-store",
			}
		);
	} catch {
		return {
			status: "error",
			error: "无法连接后端建议生成接口，请确认 backend_api 已启动。",
		};
	}

	const payload = (await response.json().catch(() => null)) as {
		status?: string;
		detail?: string;
		result?: AdviceActionState["result"];
	} | null;

	if (!response.ok || payload?.status !== "success" || !payload.result) {
		return {
			status: "error",
			error: payload?.detail ?? "重新生成建议失败。",
		};
	}

	return {
		status: "success",
		result: payload.result,
	};
}
