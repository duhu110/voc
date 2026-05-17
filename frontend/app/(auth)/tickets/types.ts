export type TicketListItem = {
	ticket_id: string;
	accept_month?: string | null;
	accept_time?: string | null;
	user_city?: string | null;
	line_category?: string | null;
	biz_category?: string | null;
	complaint_phenomenon?: string | null;
	biz_content_preview?: string | null;
	repeat_count?: number | null;
	urge_count?: number | null;
	oscillation_count?: number | null;
	converger_agent_status?: boolean | null;
	primary_leaf_code?: string | null;
	primary_leaf_name?: string | null;
	product_tag_name?: string | null;
	request_tag_name?: string | null;
};

export type TicketListResponse = {
	status: string;
	items?: TicketListItem[];
	total?: number;
	page?: number;
	page_size?: number;
};

export type TicketDetailResponse = {
	status: string;
	ticket?: Record<string, unknown>;
	classification?: Record<string, unknown> | null;
	summary?: Record<string, unknown> | null;
};

export type AdviceResult = {
	ticket_id?: string;
	classification?: Record<string, unknown>;
	matched_advices?: Record<string, unknown>[];
	expert_playbooks?: Record<string, unknown>[];
	expert_actions?: Record<string, unknown>[];
	experience_actions?: Record<string, unknown>[];
	summary_samples?: Record<string, unknown>[];
	recommended_actions?: Record<string, unknown>[];
	final_action_plan?: Record<string, unknown> | string | string[];
	reply_standards?: Record<string, unknown> | string | string[];
	risk_notes?: string[];
	confidence?: string;
	needs_human_review?: boolean;
};

export type AdviceActionState = {
	status: "idle" | "success" | "error";
	error?: string;
	result?: AdviceResult;
};
