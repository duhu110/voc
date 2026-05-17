import {
	BarChart3Icon,
	BookOpenTextIcon,
	DatabaseIcon,
	FolderTreeIcon,
	LightbulbIcon,
	TicketIcon,
	TrendingUpIcon,
} from "lucide-react";
import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

const BACKEND_API_URL =
	process.env.BACKEND_API_URL ?? "http://127.0.0.1:8010";

type OverviewData = {
	raw_ticket_count: number;
	classified_ticket_count: number;
	covered_leaf_count?: number;
	classification_coverage_rate?: number;
	summary_count: number;
	active_advice_count: number;
	active_expert_playbook_count: number;
	reviewed_expert_playbook_count: number;
	active_rag_kb_count: number;
	active_rag_document_count: number;
	recent_processing_trend?: ProcessingTrendItem[];
};

type ClassificationDistributionItem = {
	primary_leaf_code: string;
	primary_leaf_name: string;
	ticket_count: number;
};

type ProcessingTrendItem = {
	processing_date: string;
	processed_count: number;
};

type OverviewResponse = {
	status: string;
	data?: OverviewData;
};

type ClassificationDistributionResponse = {
	status: string;
	items?: ClassificationDistributionItem[];
};

const numberFormatter = new Intl.NumberFormat("zh-CN");
const percentFormatter = new Intl.NumberFormat("zh-CN", {
	style: "percent",
	maximumFractionDigits: 1,
});

async function getOverviewData() {
	const [overviewResponse, distributionResponse] = await Promise.all([
		fetch(`${BACKEND_API_URL}/overview`, { cache: "no-store" }),
		fetch(`${BACKEND_API_URL}/overview/classification-distribution?limit=8`, {
			cache: "no-store",
		}),
	]);

	if (!overviewResponse.ok || !distributionResponse.ok) {
		throw new Error("overview request failed");
	}

	const overview = (await overviewResponse.json()) as OverviewResponse;
	const distribution =
		(await distributionResponse.json()) as ClassificationDistributionResponse;

	if (overview.status !== "success" || !overview.data) {
		throw new Error("overview payload invalid");
	}

	return {
		overview: overview.data,
		distribution: distribution.items ?? [],
	};
}

export default async function Dashboard() {
	let overview: OverviewData | null = null;
	let distribution: ClassificationDistributionItem[] = [];

	try {
		const data = await getOverviewData();
		overview = data.overview;
		distribution = data.distribution;
	} catch {
		return (
			<main className="rounded-lg border bg-card p-6 text-card-foreground">
				<p className="text-sm font-medium">首页总览暂时不可用</p>
				<p className="mt-2 text-sm text-muted-foreground">
					无法连接后端 overview 接口，请确认 backend_api 已启动。
				</p>
			</main>
		);
	}

	const ragReady =
		overview.active_rag_kb_count > 0 && overview.active_rag_document_count > 0;
	const classificationCoverageRate =
		overview.classification_coverage_rate ??
		(overview.raw_ticket_count
			? overview.classified_ticket_count / overview.raw_ticket_count
			: 0);
	const coveredLeafCount = overview.covered_leaf_count ?? distribution.length;
	const recentProcessingTrend = overview.recent_processing_trend ?? [];

	const metrics = [
		{
			title: "工单总量",
			value: numberFormatter.format(overview.raw_ticket_count),
			meta: `${numberFormatter.format(overview.classified_ticket_count)} 已分类`,
			icon: TicketIcon,
		},
		{
			title: "分类覆盖",
			value: percentFormatter.format(classificationCoverageRate),
			meta: `${numberFormatter.format(coveredLeafCount)} 个叶子类目`,
			icon: FolderTreeIcon,
		},
		{
			title: "建议库数量",
			value: numberFormatter.format(overview.active_advice_count),
			meta: `${numberFormatter.format(overview.summary_count)} 条摘要来源`,
			icon: LightbulbIcon,
		},
		{
			title: "专家经验数量",
			value: numberFormatter.format(overview.active_expert_playbook_count),
			meta: `${numberFormatter.format(overview.reviewed_expert_playbook_count)} 条已审核`,
			icon: BookOpenTextIcon,
		},
		{
			title: "RAG 状态",
			value: ragReady ? "已就绪" : "待补齐",
			meta: `${numberFormatter.format(overview.active_rag_kb_count)} 个知识库 / ${numberFormatter.format(
				overview.active_rag_document_count
			)} 篇文档`,
			icon: DatabaseIcon,
		},
	];

	return (
		<main className="flex flex-col gap-4">
			<section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
				{metrics.map((metric) => {
					const Icon = metric.icon;
					return (
						<div
							key={metric.title}
							className="rounded-lg border bg-card p-4 text-card-foreground shadow-xs"
						>
							<div className="flex items-center justify-between gap-3">
								<p className="text-sm text-muted-foreground">{metric.title}</p>
								<Icon className="size-4 text-primary" />
							</div>
							<div className="mt-4 text-2xl font-semibold tracking-normal">
								{metric.value}
							</div>
							<p className="mt-1 text-xs text-muted-foreground">{metric.meta}</p>
						</div>
					);
				})}
			</section>

			<section className="grid gap-4 xl:grid-cols-2">
				<Panel
					title="分类分布图"
					description={`Top ${distribution.length} 分类工单量`}
					icon={<BarChart3Icon className="size-4" />}
				>
					<ClassificationChart items={distribution} />
				</Panel>

				<Panel
					title="近期处理趋势"
					description="按分类结果写入日期统计"
					icon={<TrendingUpIcon className="size-4" />}
				>
					<TrendChart items={recentProcessingTrend} />
				</Panel>
			</section>
		</main>
	);
}

function Panel({
	title,
	description,
	icon,
	children,
}: {
	title: string;
	description: string;
	icon: ReactNode;
	children: ReactNode;
}) {
	return (
		<div className="rounded-lg border bg-card p-5 text-card-foreground shadow-xs">
			<div className="flex items-start justify-between gap-4">
				<div>
					<h2 className="text-base font-semibold">{title}</h2>
					<p className="mt-1 text-sm text-muted-foreground">{description}</p>
				</div>
				<div className="rounded-md border bg-muted p-2 text-muted-foreground">
					{icon}
				</div>
			</div>
			<div className="mt-5">{children}</div>
		</div>
	);
}

function ClassificationChart({
	items,
}: {
	items: ClassificationDistributionItem[];
}) {
	const maxCount = Math.max(...items.map((item) => item.ticket_count), 1);

	if (items.length === 0) {
		return <EmptyState text="暂无分类分布数据" />;
	}

	return (
		<div className="space-y-4">
			{items.map((item, index) => {
				const width = `${Math.max((item.ticket_count / maxCount) * 100, 2)}%`;
				return (
					<div key={item.primary_leaf_code} className="grid gap-2">
						<div className="flex items-center justify-between gap-3 text-sm">
							<span className="min-w-0 truncate">
								{index + 1}. {item.primary_leaf_name}
							</span>
							<span className="shrink-0 font-medium">
								{numberFormatter.format(item.ticket_count)}
							</span>
						</div>
						<div className="h-2.5 overflow-hidden rounded-sm bg-muted">
							<div
								className="h-full rounded-sm bg-primary"
								style={{ width }}
							/>
						</div>
					</div>
				);
			})}
		</div>
	);
}

function TrendChart({ items }: { items: ProcessingTrendItem[] }) {
	const maxCount = Math.max(...items.map((item) => item.processed_count), 1);

	if (items.length === 0) {
		return <EmptyState text="暂无近期处理趋势" />;
	}

	return (
		<div className="flex h-72 items-end gap-2 border-b border-l px-2 pt-6">
			{items.map((item) => {
				const height = `${Math.max((item.processed_count / maxCount) * 100, 4)}%`;
				const date = new Date(item.processing_date);
				const label = `${date.getMonth() + 1}/${date.getDate()}`;
				return (
					<div key={item.processing_date} className="flex min-w-0 flex-1 flex-col items-center gap-2">
						<div className="flex h-52 w-full items-end justify-center">
							<div
								className={cn(
									"w-full max-w-8 rounded-t-sm bg-chart-2",
									"transition-colors hover:bg-primary"
								)}
								style={{ height }}
								title={`${label}: ${numberFormatter.format(item.processed_count)}`}
							/>
						</div>
						<div className="text-center">
							<div className="text-xs text-muted-foreground">{label}</div>
							<div className="text-xs font-medium">
								{compactNumber(item.processed_count)}
							</div>
						</div>
					</div>
				);
			})}
		</div>
	);
}

function EmptyState({ text }: { text: string }) {
	return (
		<div className="flex h-72 items-center justify-center rounded-lg border border-dashed text-sm text-muted-foreground">
			{text}
		</div>
	);
}

function compactNumber(value: number) {
	return new Intl.NumberFormat("zh-CN", {
		notation: "compact",
		maximumFractionDigits: 1,
	}).format(value);
}
