import { FileClockIcon, Layers3Icon, PackageIcon, TagIcon } from "lucide-react";
import type { ReactNode } from "react";

import {
	AdviceFilterForm,
	type AdviceFilterOption,
	type AdviceFilterValues,
} from "@/app/(auth)/handling-advices/filter-form";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
	Table,
	TableBody,
	TableCell,
	TableHead,
	TableHeader,
	TableRow,
} from "@/components/ui/table";

const BACKEND_API_URL =
	process.env.BACKEND_API_URL ?? "http://127.0.0.1:8010";

type SearchParams = Promise<{ [key: string]: string | string[] | undefined }>;

type HandlingAdvice = {
	id: number;
	primary_leaf_code?: string | null;
	primary_leaf_name?: string | null;
	product_tag_code?: string | null;
	product_tag_name?: string | null;
	request_tag_code?: string | null;
	request_tag_name?: string | null;
	risk_tag_code?: string | null;
	risk_tag_name?: string | null;
	advice_title?: string | null;
	advice_content?: string | null;
	applicability_note?: string | null;
	source_summary_count?: number | null;
	latest_source_ticket_id?: string | null;
	status?: string | null;
	updated_at?: string | null;
};

type HandlingAdviceResponse = {
	status: string;
	items?: HandlingAdvice[];
	total?: number;
	page?: number;
	page_size?: number;
};

const numberFormatter = new Intl.NumberFormat("zh-CN");

export default async function HandlingAdvicesPage({
	searchParams,
}: {
	searchParams: SearchParams;
}) {
	const rawParams = await searchParams;
	const filters = normalizeFilters(rawParams);
	const page = positiveNumber(firstParam(rawParams.page), 1);
	const pageSize = 20;

	let list: HandlingAdviceResponse | null = null;
	let optionItems: HandlingAdvice[] = [];
	let error = false;

	try {
		const [listResponse, optionResponse] = await Promise.all([
			fetch(buildAdviceUrl({ ...filters, page, page_size: pageSize }), {
				cache: "no-store",
			}),
			fetch(buildAdviceUrl({ status: filters.status, page: 1, page_size: 100 }), {
				cache: "no-store",
			}),
		]);

		if (!listResponse.ok || !optionResponse.ok) {
			throw new Error("handling advices request failed");
		}

		list = (await listResponse.json()) as HandlingAdviceResponse;
		const options = (await optionResponse.json()) as HandlingAdviceResponse;
		optionItems = options.items ?? [];
		if (list.status !== "success") {
			throw new Error("handling advices payload invalid");
		}
	} catch {
		error = true;
	}

	if (error || !list) {
		return (
			<main className="rounded-lg border bg-card p-6 text-card-foreground">
				<p className="text-sm font-medium">历史建议库暂时不可用</p>
				<p className="mt-2 text-sm text-muted-foreground">
					无法连接后端 /handling-advices 接口，请确认 backend_api 已启动。
				</p>
			</main>
		);
	}

	const items = list.items ?? [];
	const total = list.total ?? 0;
	const currentPage = list.page ?? page;
	const totalPages = Math.max(Math.ceil(total / pageSize), 1);
	const optionsSource = mergeOptionSource(optionItems, items);

	return (
		<main className="flex flex-col gap-4">
			<section className="flex flex-col gap-4 rounded-lg border bg-card p-5 text-card-foreground shadow-xs lg:flex-row lg:items-center lg:justify-between">
				<div className="flex min-w-0 items-start gap-3">
					<div className="rounded-md border bg-muted p-2 text-muted-foreground">
						<FileClockIcon className="size-5" />
					</div>
					<div className="min-w-0">
						<h1 className="text-xl font-semibold tracking-normal">
							历史建议库
						</h1>
						<p className="mt-1 text-sm text-muted-foreground">
							查看 advice_builder_agent 从历史摘要归纳出的可复用处理建议。
						</p>
					</div>
				</div>
				<div className="grid grid-cols-3 gap-3 text-sm lg:min-w-96">
					<SummaryTile icon={<Layers3Icon />} label="匹配建议" value={total} />
					<SummaryTile
						icon={<PackageIcon />}
						label="产品范围"
						value={uniqueCount(optionsSource, "product_tag_code")}
					/>
					<SummaryTile
						icon={<TagIcon />}
						label="诉求范围"
						value={uniqueCount(optionsSource, "request_tag_code")}
					/>
				</div>
			</section>

			<AdviceFilterForm
				categoryOptions={toOptions(
					optionsSource,
					"primary_leaf_code",
					"primary_leaf_name"
				)}
				filters={filters}
				productOptions={toOptions(
					optionsSource,
					"product_tag_code",
					"product_tag_name"
				)}
				requestOptions={toOptions(
					optionsSource,
					"request_tag_code",
					"request_tag_name"
				)}
			/>

			<section className="rounded-lg border bg-card text-card-foreground shadow-xs">
				<div className="flex items-center justify-between gap-3 border-b p-4">
					<div>
						<h2 className="text-base font-semibold">建议列表</h2>
						<p className="mt-1 text-sm text-muted-foreground">
							按来源摘要数量降序排列
						</p>
					</div>
					<div className="text-sm text-muted-foreground">
						{numberFormatter.format(total)} 条
					</div>
				</div>

				{items.length === 0 ? (
					<div className="flex h-56 items-center justify-center text-sm text-muted-foreground">
						当前筛选条件下暂无历史建议
					</div>
				) : (
					<Table>
						<TableHeader>
							<TableRow>
								<TableHead className="min-w-80">建议</TableHead>
								<TableHead>分类</TableHead>
								<TableHead>产品</TableHead>
								<TableHead>诉求</TableHead>
								<TableHead>适用条件</TableHead>
								<TableHead className="text-right">来源摘要</TableHead>
								<TableHead>状态</TableHead>
								<TableHead>更新</TableHead>
							</TableRow>
						</TableHeader>
						<TableBody>
							{items.map((item) => (
								<TableRow key={item.id}>
									<TableCell className="max-w-xl whitespace-normal">
										<div className="font-medium">
											{item.advice_title || `建议 #${item.id}`}
										</div>
										<p className="mt-1 line-clamp-2 text-sm text-muted-foreground">
											{item.advice_content || "暂无建议内容"}
										</p>
									</TableCell>
									<TableCell>
										<TagLabel
											code={item.primary_leaf_code}
											name={item.primary_leaf_name}
										/>
									</TableCell>
									<TableCell>
										<TagLabel
											code={item.product_tag_code}
											name={item.product_tag_name}
										/>
									</TableCell>
									<TableCell>
										<TagLabel
											code={item.request_tag_code}
											name={item.request_tag_name}
										/>
									</TableCell>
									<TableCell className="max-w-xs whitespace-normal text-sm text-muted-foreground">
										{item.applicability_note || "未设置"}
									</TableCell>
									<TableCell className="text-right font-medium">
										{numberFormatter.format(item.source_summary_count ?? 0)}
									</TableCell>
									<TableCell>
										<StatusBadge status={item.status} />
									</TableCell>
									<TableCell className="text-sm text-muted-foreground">
										{formatDate(item.updated_at)}
									</TableCell>
								</TableRow>
							))}
						</TableBody>
					</Table>
				)}
			</section>

			<div className="flex items-center justify-end gap-2">
				<Button asChild disabled={currentPage <= 1} variant="outline">
					<a
						aria-disabled={currentPage <= 1}
						href={pageHref(filters, currentPage - 1)}
					>
						上一页
					</a>
				</Button>
				<div className="px-2 text-sm text-muted-foreground">
					{currentPage} / {totalPages}
				</div>
				<Button asChild disabled={currentPage >= totalPages} variant="outline">
					<a
						aria-disabled={currentPage >= totalPages}
						href={pageHref(filters, currentPage + 1)}
					>
						下一页
					</a>
				</Button>
			</div>
		</main>
	);
}

function SummaryTile({
	icon,
	label,
	value,
}: {
	icon: ReactNode;
	label: string;
	value: number;
}) {
	return (
		<div className="rounded-md border bg-background p-3">
			<div className="flex items-center gap-2 text-xs text-muted-foreground [&_svg]:size-3.5">
				{icon}
				{label}
			</div>
			<div className="mt-2 text-lg font-semibold">
				{numberFormatter.format(value)}
			</div>
		</div>
	);
}

function StatusBadge({ status }: { status?: string | null }) {
	if (status === "active") {
		return <Badge>启用</Badge>;
	}
	if (status === "inactive") {
		return <Badge variant="secondary">停用</Badge>;
	}
	return <Badge variant="outline">{status || "未知"}</Badge>;
}

function TagLabel({
	code,
	name,
}: {
	code?: string | null;
	name?: string | null;
}) {
	if (!code && !name) {
		return <span className="text-sm text-muted-foreground">全部</span>;
	}

	return (
		<div className="max-w-44">
			<div className="truncate text-sm font-medium">{name || code}</div>
			{code ? (
				<div className="truncate text-xs text-muted-foreground">{code}</div>
			) : null}
		</div>
	);
}

function normalizeFilters(params: Awaited<SearchParams>): AdviceFilterValues {
	return {
		query: firstParam(params.query) ?? "",
		status: cleanFilterValue(firstParam(params.status)) || "active",
		primary_leaf_code: cleanFilterValue(firstParam(params.primary_leaf_code)),
		product_tag_code: cleanFilterValue(firstParam(params.product_tag_code)),
		request_tag_code: cleanFilterValue(firstParam(params.request_tag_code)),
	};
}

function buildAdviceUrl(params: Partial<AdviceFilterValues> & {
	page: number;
	page_size: number;
}) {
	const search = new URLSearchParams();
	for (const [key, value] of Object.entries(params)) {
		if (value !== undefined && value !== null && `${value}`.trim() !== "") {
			search.set(key, `${value}`);
		}
	}
	return `${BACKEND_API_URL}/handling-advices?${search.toString()}`;
}

function pageHref(filters: AdviceFilterValues, page: number) {
	const params = new URLSearchParams();
	for (const [key, value] of Object.entries(filters)) {
		if (value) {
			params.set(key, value);
		}
	}
	params.set("page", `${Math.max(page, 1)}`);
	return `/handling-advices?${params.toString()}`;
}

function firstParam(value: string | string[] | undefined) {
	if (Array.isArray(value)) {
		return value[0];
	}
	return value;
}

function cleanFilterValue(value: string | undefined) {
	if (!value || value === "__all__") {
		return "";
	}
	return value;
}

function positiveNumber(value: string | undefined, fallback: number) {
	const parsed = Number(value);
	return Number.isFinite(parsed) && parsed > 0 ? Math.floor(parsed) : fallback;
}

function formatDate(value?: string | null) {
	if (!value) {
		return "-";
	}
	const date = new Date(value);
	if (Number.isNaN(date.getTime())) {
		return value;
	}
	return date.toLocaleDateString("zh-CN");
}

function mergeOptionSource(primary: HandlingAdvice[], secondary: HandlingAdvice[]) {
	const seen = new Set<number>();
	const merged: HandlingAdvice[] = [];
	for (const item of [...primary, ...secondary]) {
		if (!seen.has(item.id)) {
			seen.add(item.id);
			merged.push(item);
		}
	}
	return merged;
}

function toOptions(
	items: HandlingAdvice[],
	codeKey: "primary_leaf_code" | "product_tag_code" | "request_tag_code",
	nameKey: "primary_leaf_name" | "product_tag_name" | "request_tag_name"
): AdviceFilterOption[] {
	const options = new Map<string, string>();
	for (const item of items) {
		const code = item[codeKey];
		if (!code || options.has(code)) {
			continue;
		}
		options.set(code, item[nameKey] || code);
	}
	return Array.from(options, ([code, name]) => ({ code, name })).sort((a, b) =>
		a.name.localeCompare(b.name, "zh-CN")
	);
}

function uniqueCount(
	items: HandlingAdvice[],
	key: "primary_leaf_code" | "product_tag_code" | "request_tag_code"
) {
	return new Set(items.map((item) => item[key]).filter(Boolean)).size;
}
