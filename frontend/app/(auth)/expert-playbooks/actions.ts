"use server";

const BACKEND_API_URL =
	process.env.BACKEND_API_URL ?? "http://127.0.0.1:8010";

export type ReviewStatus = "draft" | "reviewed";
export type PlaybookStatus = "active" | "inactive";

export type ExpertPlaybookListItem = {
	id: number;
	scenario_key: string;
	title: string;
	case_description?: string | null;
	source_file?: string | null;
	source_case_no?: number | null;
	primary_leaf_code?: string | null;
	primary_leaf_name?: string | null;
	product_tag_code?: string | null;
	product_tag_name?: string | null;
	request_tag_code?: string | null;
	request_tag_name?: string | null;
	trigger_keywords: string[];
	review_status: ReviewStatus | string;
	priority: number;
	status: PlaybookStatus | string;
	created_at?: string | null;
	updated_at?: string | null;
};

export type ExpertPlaybook = ExpertPlaybookListItem & {
	source_case_title?: string | null;
	verify_steps: string[];
	judgment_rules: string[];
	execution_steps: string[];
	callback_requirements: string[];
	communication_tips: string[];
	raw_case_text?: string | null;
};

export type ExpertPlaybookPayload = {
	scenario_key?: string;
	title: string;
	case_description?: string | null;
	source_file?: string;
	source_case_no?: number | null;
	source_case_title?: string | null;
	trigger_keywords: string[];
	primary_leaf_code?: string | null;
	primary_leaf_name?: string | null;
	product_tag_code?: string | null;
	product_tag_name?: string | null;
	request_tag_code?: string | null;
	request_tag_name?: string | null;
	verify_steps: string[];
	judgment_rules: string[];
	execution_steps: string[];
	callback_requirements: string[];
	communication_tips: string[];
	raw_case_text?: string | null;
	review_status: ReviewStatus;
	priority: number;
	status: PlaybookStatus;
};

export type PlaybookListParams = {
	query?: string;
	status?: string;
	review_status?: string;
	primary_leaf_code?: string;
	page?: number;
	page_size?: number;
};

type ListResponse = {
	status: string;
	items?: ExpertPlaybookListItem[];
	total?: number;
	page?: number;
	page_size?: number;
};

type DetailResponse = {
	status: string;
	item?: ExpertPlaybook;
};

function buildUrl(path: string, params?: Record<string, string | number | undefined>) {
	const url = new URL(`${BACKEND_API_URL}${path}`);
	Object.entries(params ?? {}).forEach(([key, value]) => {
		if (value !== undefined && value !== "") {
			url.searchParams.set(key, String(value));
		}
	});
	return url;
}

async function readError(response: Response) {
	try {
		const payload = (await response.json()) as { detail?: string };
		return payload.detail ?? `HTTP ${response.status}`;
	} catch {
		return `HTTP ${response.status}`;
	}
}

export async function listExpertPlaybooks(params: PlaybookListParams = {}) {
	const response = await fetch(
		buildUrl("/expert-playbooks", {
			query: params.query,
			status: params.status,
			review_status: params.review_status,
			primary_leaf_code: params.primary_leaf_code,
			page: params.page ?? 1,
			page_size: params.page_size ?? 20,
		}),
		{ cache: "no-store" }
	);

	if (!response.ok) {
		throw new Error(await readError(response));
	}

	const payload = (await response.json()) as ListResponse;
	if (payload.status !== "success") {
		throw new Error("专家剧本列表响应异常");
	}

	return {
		items: payload.items ?? [],
		total: payload.total ?? 0,
		page: payload.page ?? 1,
		page_size: payload.page_size ?? 20,
	};
}

export async function getExpertPlaybook(id: number) {
	const response = await fetch(`${BACKEND_API_URL}/expert-playbooks/${id}`, {
		cache: "no-store",
	});

	if (!response.ok) {
		throw new Error(await readError(response));
	}

	const payload = (await response.json()) as DetailResponse;
	if (payload.status !== "success" || !payload.item) {
		throw new Error("专家剧本详情响应异常");
	}

	return payload.item;
}

export async function createExpertPlaybook(payload: ExpertPlaybookPayload) {
	const response = await fetch(`${BACKEND_API_URL}/expert-playbooks`, {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify({
			...payload,
			scenario_key: payload.scenario_key,
			source_file: payload.source_file || "manual",
		}),
		cache: "no-store",
	});

	if (!response.ok) {
		throw new Error(await readError(response));
	}

	const data = (await response.json()) as DetailResponse;
	if (data.status !== "success" || !data.item) {
		throw new Error("专家剧本新增响应异常");
	}

	return data.item;
}

export async function updateExpertPlaybook(
	id: number,
	payload: ExpertPlaybookPayload
) {
	const patch = { ...payload };
	delete patch.scenario_key;
	delete patch.source_file;
	const response = await fetch(`${BACKEND_API_URL}/expert-playbooks/${id}`, {
		method: "PATCH",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify(patch),
		cache: "no-store",
	});

	if (!response.ok) {
		throw new Error(await readError(response));
	}

	const data = (await response.json()) as DetailResponse;
	if (data.status !== "success" || !data.item) {
		throw new Error("专家剧本编辑响应异常");
	}

	return data.item;
}
