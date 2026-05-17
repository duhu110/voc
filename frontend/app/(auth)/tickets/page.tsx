import Link from "next/link";
import {
	ArrowLeftIcon,
	ArrowRightIcon,
	CheckCircle2Icon,
	ClockIcon,
	FilterIcon,
	SearchIcon,
	TicketIcon,
} from "lucide-react";

import { AdviceRegenerator } from "@/app/(auth)/tickets/advice-button";
import type {
	TicketDetailResponse,
	TicketListItem,
	TicketListResponse,
} from "@/app/(auth)/tickets/types";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";
import {
	Table,
	TableBody,
	TableCell,
	TableHead,
	TableHeader,
	TableRow,
} from "@/components/ui/table";
import { cn } from "@/lib/utils";

const BACKEND_API_URL =
	process.env.BACKEND_API_URL ?? "http://127.0.0.1:8010";

const pageSize = 12;

type PageProps = {
	searchParams?: Promise<Record<string, string | string[] | undefined>>;
};

type ParsedParams = {
	query: string;
	status: "all" | "done" | "pending";
	page: number;
	ticketId: string;
};

export default async function TicketsPage({ searchParams }: PageProps) {
	const params = parseParams((await searchParams) ?? {});

	let list: TicketListResponse;
	try {
		list = await fetchTickets(params);
	} catch {
		return (
			<main className="rounded-lg border bg-card p-6 text-card-foreground">
				<p className="text-sm font-medium">工单中心暂时不可用</p>
				<p className="mt-2 text-sm text-muted-foreground">
					无法连接后端 tickets 接口，请确认 backend_api 已启动。
				</p>
			</main>
		);
	}

	const items = list.items ?? [];
	const firstTicketId = items.find((item) => item.ticket_id)?.ticket_id ?? "";
	const selectedTicketId = params.ticketId || firstTicketId;
	const detail = selectedTicketId ? await fetchTicketDetail(selectedTicketId) : null;
	const total = list.total ?? 0;
	const totalPages = Math.max(Math.ceil(total / pageSize), 1);

	return (
		<main className="flex flex-col gap-4">
			<section className="grid gap-3 sm:grid-cols-3">
				<MetricCard label="历史工单" value={formatNumber(total)} icon={<TicketIcon />} />
				<MetricCard
					label="当前页已分类"
					value={formatNumber(items.filter((item) => item.converger_agent_status).length)}
					icon={<CheckCircle2Icon />}
				/>
				<MetricCard
					label="当前筛选"
					value={statusLabel(params.status)}
					icon={<FilterIcon />}
				/>
			</section>

			<section className="grid gap-4 xl:grid-cols-2">
				<Card>
					<CardHeader>
						<CardTitle>历史工单列表</CardTitle>
						<CardDescription>按工单编号、投诉内容、投诉现象检索。</CardDescription>
					</CardHeader>
					<CardContent className="space-y-4">
						<FilterForm params={params} />
						<TicketsTable
							items={items}
							params={params}
							selectedTicketId={selectedTicketId}
						/>
						<Pagination
							params={params}
							total={total}
							totalPages={totalPages}
						/>
					</CardContent>
				</Card>

				<TicketDetailPanel
					detail={detail}
					ticketId={selectedTicketId}
				/>
			</section>
		</main>
	);
}

async function fetchTickets(params: ParsedParams): Promise<TicketListResponse> {
	const query = new URLSearchParams({
		page: String(params.page),
		page_size: String(pageSize),
	});

	if (params.query) {
		query.set("query", params.query);
	}
	if (params.status !== "all") {
		query.set("converger_agent_status", params.status === "done" ? "true" : "false");
	}

	const response = await fetch(`${BACKEND_API_URL}/tickets?${query}`, {
		cache: "no-store",
	});
	if (!response.ok) {
		throw new Error("tickets request failed");
	}
	return (await response.json()) as TicketListResponse;
}

async function fetchTicketDetail(ticketId: string): Promise<TicketDetailResponse | null> {
	try {
		const response = await fetch(
			`${BACKEND_API_URL}/tickets/${encodeURIComponent(ticketId)}`,
			{ cache: "no-store" }
		);
		if (!response.ok) {
			return null;
		}
		return (await response.json()) as TicketDetailResponse;
	} catch {
		return null;
	}
}

function FilterForm({ params }: { params: ParsedParams }) {
	return (
		<form className="grid gap-3 md:grid-cols-[1fr_160px_auto]" action="/tickets">
			<div className="relative">
				<SearchIcon className="pointer-events-none absolute left-2.5 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
				<Input
					className="pl-8"
					defaultValue={params.query}
					name="query"
					placeholder="搜索工单编号、投诉内容、投诉现象"
				/>
			</div>
			<select
				className="h-9 rounded-md border border-input bg-background px-2.5 text-sm shadow-xs outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50 dark:bg-input/30"
				defaultValue={params.status}
				name="status"
			>
				<option value="all">全部状态</option>
				<option value="done">已分类</option>
				<option value="pending">待分类</option>
			</select>
			<Button type="submit">
				<FilterIcon />
				筛选
			</Button>
		</form>
	);
}

function TicketsTable({
	items,
	params,
	selectedTicketId,
}: {
	items: TicketListItem[];
	params: ParsedParams;
	selectedTicketId: string;
}) {
	if (!items.length) {
		return (
			<div className="flex h-56 items-center justify-center rounded-lg border border-dashed text-sm text-muted-foreground">
				暂无符合条件的历史工单
			</div>
		);
	}

	return (
		<Table>
			<TableHeader>
				<TableRow>
					<TableHead>工单</TableHead>
					<TableHead>分类结果</TableHead>
					<TableHead className="hidden 2xl:table-cell">标签</TableHead>
					<TableHead className="text-right">状态</TableHead>
				</TableRow>
			</TableHeader>
			<TableBody>
				{items.map((item) => (
					<TableRow
						key={item.ticket_id}
						className={cn(
							item.ticket_id === selectedTicketId && "bg-muted/70"
						)}
					>
						<TableCell className="max-w-[320px] whitespace-normal">
							{item.ticket_id ? (
								<Link
									className="font-medium text-foreground hover:underline"
									href={ticketHref(params, item.ticket_id)}
								>
									{item.ticket_id}
								</Link>
							) : (
								<span className="font-medium text-muted-foreground">
									无工单编号
								</span>
							)}
							<p className="mt-1 line-clamp-2 text-xs leading-5 text-muted-foreground">
								{item.complaint_phenomenon || item.biz_content_preview || "无摘要"}
							</p>
							<p className="mt-1 text-xs text-muted-foreground">
								{joinText([item.user_city, item.accept_time])}
							</p>
						</TableCell>
						<TableCell className="max-w-[220px] whitespace-normal">
							{item.primary_leaf_name ? (
								<>
									<p className="text-sm">{item.primary_leaf_name}</p>
									<p className="mt-1 text-xs text-muted-foreground">
										{item.primary_leaf_code}
									</p>
								</>
							) : (
								<span className="text-sm text-muted-foreground">暂无分类</span>
							)}
						</TableCell>
						<TableCell className="hidden whitespace-normal 2xl:table-cell">
							<div className="flex flex-wrap gap-1.5">
								{item.product_tag_name && (
									<Badge variant="secondary">{item.product_tag_name}</Badge>
								)}
								{item.request_tag_name && (
									<Badge variant="outline">{item.request_tag_name}</Badge>
								)}
							</div>
						</TableCell>
						<TableCell className="text-right">
							<StatusBadge value={item.converger_agent_status} />
						</TableCell>
					</TableRow>
				))}
			</TableBody>
		</Table>
	);
}

function TicketDetailPanel({
	detail,
	ticketId,
}: {
	detail: TicketDetailResponse | null;
	ticketId: string;
}) {
	if (!ticketId) {
		return (
			<Card>
				<CardContent className="flex h-96 items-center justify-center text-sm text-muted-foreground">
					请选择一个历史工单
				</CardContent>
			</Card>
		);
	}

	if (!detail?.ticket) {
		return (
			<Card>
				<CardHeader>
					<CardTitle>工单详情</CardTitle>
					<CardDescription>未能读取工单 {ticketId} 的详情。</CardDescription>
				</CardHeader>
			</Card>
		);
	}

	return (
		<Card>
			<CardHeader>
				<div className="flex flex-wrap items-start justify-between gap-3">
					<div>
						<CardTitle className="flex items-center gap-2">
							{ticketId}
							<StatusBadge value={Boolean(detail.ticket.converger_agent_status)} />
						</CardTitle>
						<CardDescription>
							{joinText([
								asText(detail.ticket.user_city),
								asText(detail.ticket.accept_time),
								asText(detail.ticket.line_category),
							]) || "历史工单详情"}
						</CardDescription>
					</div>
				</div>
			</CardHeader>
			<CardContent className="space-y-6">
				<DetailSection
					items={[
						["业务分类", detail.ticket.biz_category],
						["投诉现象", detail.ticket.complaint_phenomenon],
						["重复次数", detail.ticket.repeat_count],
						["催办次数", detail.ticket.urge_count],
						["震荡次数", detail.ticket.oscillation_count],
					]}
					title="基础信息"
				/>
				<TextSection title="投诉内容" value={detail.ticket.biz_content} />
				<ClassificationSection classification={detail.classification} />
				<SummarySection summary={detail.summary} />
				<AdviceRegenerator ticketId={ticketId} />
			</CardContent>
		</Card>
	);
}

function ClassificationSection({
	classification,
}: {
	classification?: Record<string, unknown> | null;
}) {
	if (!classification) {
		return (
			<EmptySection
				icon={<ClockIcon />}
				text="暂无分类结果和标签"
				title="分类结果"
			/>
		);
	}

	return (
		<section className="space-y-3">
			<SectionTitle title="分类结果与标签" />
			<div className="grid gap-3 sm:grid-cols-2">
				<InfoLine label="叶子类目" value={joinText([classification.primary_leaf_name, classification.primary_leaf_code])} />
				<InfoLine label="产品标签" value={joinText([classification.product_tag_name, classification.product_tag_code])} />
				<InfoLine label="诉求标签" value={joinText([classification.request_tag_name, classification.request_tag_code])} />
				<InfoLine label="风险标签" value={joinText([classification.risk_tag_name, classification.risk_tag_code])} />
				<InfoLine label="情绪标签" value={joinText([classification.emotion_tag_name, classification.emotion_tag_code])} />
				<InfoLine label="线路类型" value={classification.line_category} />
			</div>
		</section>
	);
}

function SummarySection({ summary }: { summary?: Record<string, unknown> | null }) {
	if (!summary) {
		return (
			<EmptySection
				icon={<ClockIcon />}
				text="暂无历史处理摘要"
				title="历史处理摘要"
			/>
		);
	}

	return (
		<section className="space-y-3">
			<SectionTitle title="历史处理摘要" />
			<TextSection
				title="处理摘要"
				value={summary.resolution_summary ?? summary.summary}
			/>
			<div className="grid gap-3 sm:grid-cols-2">
				<InfoLine label="来源工单" value={summary.source_ticket_id} />
				<InfoLine label="创建时间" value={summary.created_at} />
			</div>
		</section>
	);
}

function DetailSection({
	title,
	items,
}: {
	title: string;
	items: [string, unknown][];
}) {
	return (
		<section className="space-y-3">
			<SectionTitle title={title} />
			<div className="grid gap-3 sm:grid-cols-2">
				{items.map(([label, value]) => (
					<InfoLine key={label} label={label} value={value} />
				))}
			</div>
		</section>
	);
}

function TextSection({ title, value }: { title: string; value: unknown }) {
	const text = asText(value);
	if (!text) {
		return null;
	}

	return (
		<section className="space-y-2">
			<SectionTitle title={title} />
			<p className="whitespace-pre-wrap rounded-md border bg-muted/30 p-3 text-sm leading-6 text-muted-foreground">
				{text}
			</p>
		</section>
	);
}

function InfoLine({ label, value }: { label: string; value: unknown }) {
	return (
		<div className="rounded-md border p-3">
			<p className="text-xs text-muted-foreground">{label}</p>
			<p className="mt-1 break-words text-sm font-medium">
				{asText(value) || "未记录"}
			</p>
		</div>
	);
}

function EmptySection({
	icon,
	text,
	title,
}: {
	icon: React.ReactNode;
	text: string;
	title: string;
}) {
	return (
		<section className="space-y-3">
			<SectionTitle title={title} />
			<div className="flex items-center gap-2 rounded-md border border-dashed p-3 text-sm text-muted-foreground [&>svg]:size-4">
				{icon}
				{text}
			</div>
		</section>
	);
}

function SectionTitle({ title }: { title: string }) {
	return (
		<div className="flex items-center gap-3">
			<h2 className="text-sm font-medium">{title}</h2>
			<Separator className="flex-1" />
		</div>
	);
}

function MetricCard({
	label,
	value,
	icon,
}: {
	label: string;
	value: string;
	icon: React.ReactNode;
}) {
	return (
		<Card size="sm">
			<CardContent className="flex items-center justify-between gap-4">
				<div>
					<p className="text-sm text-muted-foreground">{label}</p>
					<p className="mt-2 text-2xl font-semibold">{value}</p>
				</div>
				<div className="rounded-md border bg-muted p-2 text-primary [&>svg]:size-5">
					{icon}
				</div>
			</CardContent>
		</Card>
	);
}

function Pagination({
	params,
	total,
	totalPages,
}: {
	params: ParsedParams;
	total: number;
	totalPages: number;
}) {
	return (
		<div className="flex flex-wrap items-center justify-between gap-3 text-sm text-muted-foreground">
			<span>
				共 {formatNumber(total)} 条，第 {params.page} / {totalPages} 页
			</span>
			<div className="flex items-center gap-2">
				<Button asChild disabled={params.page <= 1} size="sm" variant="outline">
					<Link href={pageHref(params, Math.max(params.page - 1, 1))}>
						<ArrowLeftIcon />
						上一页
					</Link>
				</Button>
				<Button
					asChild
					disabled={params.page >= totalPages}
					size="sm"
					variant="outline"
				>
					<Link href={pageHref(params, Math.min(params.page + 1, totalPages))}>
						下一页
						<ArrowRightIcon />
					</Link>
				</Button>
			</div>
		</div>
	);
}

function StatusBadge({ value }: { value?: boolean | null }) {
	if (value === true) {
		return <Badge variant="secondary">已分类</Badge>;
	}
	if (value === false) {
		return <Badge variant="outline">待分类</Badge>;
	}
	return <Badge variant="outline">未知</Badge>;
}

function parseParams(
	input: Record<string, string | string[] | undefined>
): ParsedParams {
	const first = (value: string | string[] | undefined) =>
		Array.isArray(value) ? value[0] : value;
	const statusRaw = first(input.status);
	const pageRaw = Number(first(input.page) ?? "1");
	return {
		query: first(input.query)?.trim() ?? "",
		status:
			statusRaw === "done" || statusRaw === "pending" ? statusRaw : "all",
		page: Number.isFinite(pageRaw) && pageRaw > 0 ? Math.floor(pageRaw) : 1,
		ticketId: first(input.ticket_id)?.trim() ?? "",
	};
}

function ticketHref(params: ParsedParams, ticketId: string) {
	const query = baseQuery(params);
	query.set("ticket_id", ticketId);
	return `/tickets?${query}`;
}

function pageHref(params: ParsedParams, nextPage: number) {
	const query = baseQuery({ ...params, page: nextPage });
	return `/tickets?${query}`;
}

function baseQuery(params: ParsedParams) {
	const query = new URLSearchParams();
	if (params.query) {
		query.set("query", params.query);
	}
	if (params.status !== "all") {
		query.set("status", params.status);
	}
	if (params.page > 1) {
		query.set("page", String(params.page));
	}
	return query;
}

function statusLabel(status: ParsedParams["status"]) {
	return status === "done" ? "已分类" : status === "pending" ? "待分类" : "全部";
}

function joinText(values: unknown[]) {
	return values.map(asText).filter(Boolean).join(" / ");
}

function asText(value: unknown) {
	if (value === null || value === undefined) {
		return "";
	}
	if (typeof value === "string") {
		return value.trim();
	}
	if (typeof value === "number" || typeof value === "boolean") {
		return String(value);
	}
	return "";
}

function formatNumber(value: number) {
	return new Intl.NumberFormat("zh-CN").format(value);
}
