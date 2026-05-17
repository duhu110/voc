"use client";

import {
	DatabaseIcon,
	FileTextIcon,
	RefreshCwIcon,
	RotateCcwIcon,
	SearchIcon,
	UploadIcon,
} from "lucide-react";
import { useMemo, useState, type FormEvent } from "react";
import { toast } from "sonner";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardAction, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import {
	Table,
	TableBody,
	TableCell,
	TableHead,
	TableHeader,
	TableRow,
} from "@/components/ui/table";
import { Textarea } from "@/components/ui/textarea";

export type RagMapping = {
	id: number;
	logical_name: string;
	rag_kb_id: string;
	display_name: string;
	description?: string | null;
	metadata?: Record<string, unknown>;
	status: string;
	active_document_count: number;
	total_document_count: number;
	created_at?: string;
	updated_at?: string;
};

export type RagDocument = {
	id: number;
	logical_name: string;
	knowledge_base_name: string;
	rag_kb_id: string;
	rag_document_id: string;
	rag_task_id?: string | null;
	external_id: string;
	source_table: string;
	source_id: string;
	source_version: string;
	title?: string | null;
	metadata?: Record<string, unknown>;
	task_status: string;
	status: string;
	created_at?: string;
	updated_at?: string;
};

export type RagTask = {
	id: number;
	rag_task_id: string;
	rag_document_id?: string | null;
	rag_kb_id: string;
	source_table?: string | null;
	source_id?: string | null;
	task_status: string;
	progress_current: number;
	progress_total: number;
	error_message?: string | null;
	raw_task?: Record<string, unknown>;
	created_at?: string;
	updated_at?: string;
	completed_at?: string | null;
};

type SearchResultItem = {
	chunk_id?: string | number;
	document_id?: string | number;
	title?: string;
	content?: string;
	text?: string;
	score?: number;
	metadata?: Record<string, unknown>;
} & Record<string, unknown>;

type RagData = {
	mappings: RagMapping[];
	documents: RagDocument[];
	tasks: RagTask[];
};

type RagManagementClientProps = {
	apiBaseUrl: string;
	initialData: RagData;
};

const numberFormatter = new Intl.NumberFormat("zh-CN");

const logicalNameLabels: Record<string, string> = {
	expert_playbooks: "专家经验库",
	handling_advices: "历史建议库",
	policy_documents: "政策文档库",
	standard_documents: "规范文档库",
	"voc-expert-playbooks": "专家经验库",
	"voc-handling-advices": "历史建议库",
	"voc-policy-docs": "政策文档库",
	"voc-resolution-summaries": "历史处理摘要库",
};

const documentKinds = [
	{ value: "policy", label: "政策文档" },
	{ value: "standard", label: "规范文档" },
	{ value: "expert_case", label: "专家案例" },
];

export function RagManagementClient({
	apiBaseUrl,
	initialData,
}: RagManagementClientProps) {
	const [data, setData] = useState<RagData>(initialData);
	const [selectedLogicalName, setSelectedLogicalName] = useState(
		initialData.mappings[0]?.logical_name ?? ""
	);
	const [query, setQuery] = useState("");
	const [topK, setTopK] = useState(5);
	const [searchResults, setSearchResults] = useState<SearchResultItem[]>([]);
	const [isSearching, setIsSearching] = useState(false);
	const [isUploading, setIsUploading] = useState(false);
	const [isRefreshing, setIsRefreshing] = useState(false);
	const [uploadKind, setUploadKind] = useState("policy");
	const [uploadTaskId, setUploadTaskId] = useState("");
	const [taskLookupId, setTaskLookupId] = useState("");
	const [taskLookupResult, setTaskLookupResult] = useState<Record<string, unknown> | null>(null);

	const selectedMapping = data.mappings.find(
		(mapping) => mapping.logical_name === selectedLogicalName
	);

	const filteredDocuments = useMemo(
		() =>
			selectedLogicalName
				? data.documents.filter((document) => document.logical_name === selectedLogicalName)
				: data.documents,
		[data.documents, selectedLogicalName]
	);

	const mappingByKbId = useMemo(() => {
		const map = new Map<string, RagMapping>();
		for (const mapping of data.mappings) {
			map.set(mapping.rag_kb_id, mapping);
		}
		return map;
	}, [data.mappings]);

	const summary = {
		activeKb: data.mappings.filter((mapping) => mapping.status === "active").length,
		documents: data.mappings.reduce(
			(total, mapping) => total + Number(mapping.total_document_count ?? 0),
			0
		),
		activeDocuments: data.mappings.reduce(
			(total, mapping) => total + Number(mapping.active_document_count ?? 0),
			0
		),
		failedTasks: data.tasks.filter((task) => isFailedStatus(task.task_status)).length,
	};

	async function refreshData() {
		setIsRefreshing(true);
		try {
			const [mappingsResponse, documentsResponse, tasksResponse] = await Promise.all([
				fetch(`${apiBaseUrl}/rag/mappings`),
				fetch(`${apiBaseUrl}/rag/documents?limit=80`),
				fetch(`${apiBaseUrl}/rag/tasks?limit=80`),
			]);
			if (!mappingsResponse.ok || !documentsResponse.ok || !tasksResponse.ok) {
				throw new Error("refresh failed");
			}
			const [mappings, documents, tasks] = await Promise.all([
				mappingsResponse.json(),
				documentsResponse.json(),
				tasksResponse.json(),
			]);
			setData({
				mappings: mappings.items ?? [],
				documents: documents.items ?? [],
				tasks: tasks.items ?? [],
			});
			toast.success("RAG 数据已刷新");
		} catch {
			toast.error("刷新 RAG 数据失败");
		} finally {
			setIsRefreshing(false);
		}
	}

	async function handleSearch(event: FormEvent<HTMLFormElement>) {
		event.preventDefault();
		if (!selectedLogicalName || !query.trim()) {
			toast.warning("请选择知识库并输入检索内容");
			return;
		}
		setIsSearching(true);
		try {
			const response = await fetch(
				`${apiBaseUrl}/rag/mappings/${encodeURIComponent(selectedLogicalName)}/search`,
				{
					method: "POST",
					headers: { "Content-Type": "application/json" },
					body: JSON.stringify({ query: query.trim(), top_k: topK }),
				}
			);
			if (!response.ok) {
				throw new Error(await response.text());
			}
			const payload = await response.json();
			setSearchResults((payload.results ?? payload.items ?? []) as SearchResultItem[]);
			toast.success("语义检索完成");
		} catch {
			setSearchResults([]);
			toast.error("语义检索失败");
		} finally {
			setIsSearching(false);
		}
	}

	async function handleUpload(event: FormEvent<HTMLFormElement>) {
		event.preventDefault();
		if (!selectedMapping) {
			toast.warning("请先选择可用知识库");
			return;
		}
		const form = event.currentTarget;
		const formData = new FormData(form);
		const file = formData.get("file");
		if (!(file instanceof File) || file.size === 0) {
			toast.warning("请选择需要入库的文档");
			return;
		}

		const title = String(formData.get("title") ?? "").trim();
		const externalId = String(formData.get("external_id") ?? "").trim();
		const metadata = {
			document_kind: uploadKind,
			logical_name: selectedMapping.logical_name,
			uploaded_from: "voc_frontend",
		};

		const payload = new FormData();
		payload.append("file", file);
		if (title) {
			payload.append("title", title);
		}
		if (externalId) {
			payload.append("external_id", externalId);
		}
		payload.append("metadata_json", JSON.stringify(metadata));

		setIsUploading(true);
		try {
			const response = await fetch(
				`${apiBaseUrl}/rag/knowledge-bases/${encodeURIComponent(selectedMapping.rag_kb_id)}/documents`,
				{ method: "POST", body: payload }
			);
			if (!response.ok) {
				throw new Error(await response.text());
			}
			const result = await response.json();
			const nextTaskId = extractTaskId(result);
			if (nextTaskId) {
				setUploadTaskId(nextTaskId);
				setTaskLookupId(nextTaskId);
			}
			form.reset();
			toast.success("文档已提交入库");
			await refreshData();
		} catch {
			toast.error("文档入库提交失败");
		} finally {
			setIsUploading(false);
		}
	}

	async function handleTaskLookup(event: FormEvent<HTMLFormElement>) {
		event.preventDefault();
		if (!taskLookupId.trim()) {
			toast.warning("请输入任务 ID");
			return;
		}
		try {
			const response = await fetch(
				`${apiBaseUrl}/rag/tasks/${encodeURIComponent(taskLookupId.trim())}`
			);
			if (!response.ok) {
				throw new Error(await response.text());
			}
			setTaskLookupResult((await response.json()) as Record<string, unknown>);
			toast.success("任务状态已获取");
		} catch {
			setTaskLookupResult(null);
			toast.error("任务状态查询失败");
		}
	}

	async function retryTask(taskId: string) {
		try {
			const response = await fetch(
				`${apiBaseUrl}/rag/tasks/${encodeURIComponent(taskId)}/retry`,
				{ method: "POST" }
			);
			if (!response.ok) {
				throw new Error(await response.text());
			}
			toast.success("已提交失败任务重试");
			await refreshData();
		} catch {
			toast.error("任务重试失败");
		}
	}

	return (
		<main className="flex flex-col gap-4">
			<section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
				<MetricCard title="业务知识库" value={summary.activeKb} meta="active mappings" />
				<MetricCard title="文档映射" value={summary.documents} meta={`${summary.activeDocuments} active`} />
				<MetricCard title="任务快照" value={data.tasks.length} meta={`${summary.failedTasks} failed`} />
				<MetricCard title="当前知识库" value={selectedMapping?.display_name ?? "未选择"} meta={selectedMapping?.rag_kb_id ?? "no kb_id"} />
			</section>

			<section className="grid gap-4 xl:grid-cols-[1.3fr_0.7fr]">
				<Card>
					<CardHeader>
						<CardTitle className="flex items-center gap-2">
							<DatabaseIcon className="size-4" />
							业务知识库映射
						</CardTitle>
						<CardDescription>专家经验库、历史建议库、政策文档库等 logical_name 与 RAG kb_id 的对应关系</CardDescription>
						<CardAction>
							<Button disabled={isRefreshing} onClick={refreshData} size="sm" variant="outline">
								<RefreshCwIcon className={isRefreshing ? "animate-spin" : ""} />
								刷新
							</Button>
						</CardAction>
					</CardHeader>
					<CardContent>
						<Table>
							<TableHeader>
								<TableRow>
									<TableHead>业务库</TableHead>
									<TableHead>kb_id</TableHead>
									<TableHead>文档</TableHead>
									<TableHead>状态</TableHead>
									<TableHead>同步时间</TableHead>
								</TableRow>
							</TableHeader>
							<TableBody>
								{data.mappings.map((mapping) => (
									<TableRow
										key={mapping.logical_name}
										className={mapping.logical_name === selectedLogicalName ? "bg-muted/60" : ""}
										onClick={() => setSelectedLogicalName(mapping.logical_name)}
									>
										<TableCell>
											<div className="font-medium">{displayLogicalName(mapping)}</div>
											<div className="text-xs text-muted-foreground">{mapping.logical_name}</div>
										</TableCell>
										<TableCell className="max-w-64 truncate font-mono text-xs">{mapping.rag_kb_id}</TableCell>
										<TableCell>{numberFormatter.format(mapping.total_document_count)} / {numberFormatter.format(mapping.active_document_count)}</TableCell>
										<TableCell><StatusBadge status={mapping.status} /></TableCell>
										<TableCell className="text-muted-foreground">{formatDateTime(mapping.updated_at)}</TableCell>
									</TableRow>
								))}
							</TableBody>
						</Table>
					</CardContent>
				</Card>

				<Card>
					<CardHeader>
						<CardTitle className="flex items-center gap-2">
							<SearchIcon className="size-4" />
							语义检索测试
						</CardTitle>
						<CardDescription>/rag/mappings/{"{logical_name}"}/search</CardDescription>
					</CardHeader>
					<CardContent>
						<form className="flex flex-col gap-3" onSubmit={handleSearch}>
							<Select value={selectedLogicalName} onValueChange={setSelectedLogicalName}>
								<SelectTrigger className="w-full">
									<SelectValue placeholder="选择知识库" />
								</SelectTrigger>
								<SelectContent>
									{data.mappings.map((mapping) => (
										<SelectItem key={mapping.logical_name} value={mapping.logical_name}>
											{displayLogicalName(mapping)}
										</SelectItem>
									))}
								</SelectContent>
							</Select>
							<Textarea
								value={query}
								onChange={(event) => setQuery(event.target.value)}
								placeholder="输入投诉场景、处理问题或政策关键词"
								className="min-h-24"
							/>
							<div className="flex items-center gap-2">
								<Input
									min={1}
									max={20}
									type="number"
									value={topK}
									onChange={(event) => setTopK(Number(event.target.value))}
									className="w-24"
								/>
								<Button className="flex-1" disabled={isSearching} type="submit">
									<SearchIcon />
									{isSearching ? "检索中" : "检索"}
								</Button>
							</div>
						</form>
						<Separator className="my-4" />
						<div className="space-y-3">
							{searchResults.length === 0 ? (
								<EmptyState text="暂无检索结果" />
							) : (
								searchResults.map((result, index) => (
									<div key={`${result.chunk_id ?? result.document_id ?? index}`} className="rounded-md border p-3">
										<div className="flex items-center justify-between gap-3">
											<div className="truncate text-sm font-medium">{result.title ?? `结果 ${index + 1}`}</div>
											{typeof result.score === "number" && (
												<Badge variant="outline">{result.score.toFixed(3)}</Badge>
											)}
										</div>
										<p className="mt-2 line-clamp-4 text-sm text-muted-foreground">
											{result.content ?? result.text ?? JSON.stringify(result)}
										</p>
									</div>
								))
							)}
						</div>
					</CardContent>
				</Card>
			</section>

			<section className="grid gap-4 xl:grid-cols-[0.8fr_1.2fr]">
				<Card>
					<CardHeader>
						<CardTitle className="flex items-center gap-2">
							<UploadIcon className="size-4" />
							RAG 文档入库管理
						</CardTitle>
						<CardDescription>上传政策文档、规范文档、专家案例文档到当前知识库</CardDescription>
					</CardHeader>
					<CardContent>
						<form className="flex flex-col gap-3" onSubmit={handleUpload}>
							<Select value={uploadKind} onValueChange={setUploadKind}>
								<SelectTrigger className="w-full">
									<SelectValue />
								</SelectTrigger>
								<SelectContent>
									{documentKinds.map((kind) => (
										<SelectItem key={kind.value} value={kind.value}>
											{kind.label}
										</SelectItem>
									))}
								</SelectContent>
							</Select>
							<Input name="title" placeholder="文档标题" />
							<Input name="external_id" placeholder="外部编号，可选" />
							<Input name="file" type="file" />
							<Button disabled={isUploading || !selectedMapping} type="submit">
								<UploadIcon />
								{isUploading ? "提交中" : "提交入库"}
							</Button>
						</form>
						{uploadTaskId && (
							<p className="mt-3 truncate text-xs text-muted-foreground">
								最近提交任务：<span className="font-mono">{uploadTaskId}</span>
							</p>
						)}
					</CardContent>
				</Card>

				<Card>
					<CardHeader>
						<CardTitle className="flex items-center gap-2">
							<FileTextIcon className="size-4" />
							本地文档映射
						</CardTitle>
						<CardDescription>rag_documents 中记录的文档、任务和同步状态</CardDescription>
					</CardHeader>
					<CardContent>
						<Table>
							<TableHeader>
								<TableRow>
									<TableHead>标题</TableHead>
									<TableHead>来源</TableHead>
									<TableHead>任务</TableHead>
									<TableHead>状态</TableHead>
									<TableHead>更新时间</TableHead>
								</TableRow>
							</TableHeader>
							<TableBody>
								{filteredDocuments.map((document) => (
									<TableRow key={document.id}>
										<TableCell>
											<div className="max-w-72 truncate font-medium">{document.title ?? document.external_id}</div>
											<div className="text-xs text-muted-foreground">{document.knowledge_base_name}</div>
										</TableCell>
										<TableCell className="text-xs text-muted-foreground">{document.source_table}:{document.source_id}</TableCell>
										<TableCell className="max-w-40 truncate font-mono text-xs">{document.rag_task_id ?? "-"}</TableCell>
										<TableCell><StatusBadge status={document.task_status} /></TableCell>
										<TableCell className="text-muted-foreground">{formatDateTime(document.updated_at)}</TableCell>
									</TableRow>
								))}
							</TableBody>
						</Table>
						{filteredDocuments.length === 0 && <EmptyState text="当前知识库暂无文档映射" />}
					</CardContent>
				</Card>
			</section>

			<Card>
				<CardHeader>
					<CardTitle className="flex items-center gap-2">
						<RotateCcwIcon className="size-4" />
						向量化任务状态
					</CardTitle>
					<CardDescription>查看任务进度，失败任务可直接重试</CardDescription>
				</CardHeader>
				<CardContent className="space-y-4">
					<form className="flex flex-col gap-2 sm:flex-row" onSubmit={handleTaskLookup}>
						<Input
							value={taskLookupId}
							onChange={(event) => setTaskLookupId(event.target.value)}
							placeholder="输入 rag_task_id 查询实时状态"
							className="font-mono"
						/>
						<Button type="submit" variant="outline">
							<SearchIcon />
							查询任务
						</Button>
					</form>
					{taskLookupResult && (
						<pre className="max-h-52 overflow-auto rounded-md border bg-muted p-3 text-xs">
							{JSON.stringify(taskLookupResult, null, 2)}
						</pre>
					)}
					<Table>
						<TableHeader>
							<TableRow>
								<TableHead>任务 ID</TableHead>
								<TableHead>知识库</TableHead>
								<TableHead>进度</TableHead>
								<TableHead>状态</TableHead>
								<TableHead>错误</TableHead>
								<TableHead>操作</TableHead>
							</TableRow>
						</TableHeader>
						<TableBody>
							{data.tasks.map((task) => {
								const mapping = mappingByKbId.get(task.rag_kb_id);
								return (
									<TableRow key={task.rag_task_id}>
										<TableCell className="max-w-64 truncate font-mono text-xs">{task.rag_task_id}</TableCell>
										<TableCell>{mapping ? displayLogicalName(mapping) : task.rag_kb_id}</TableCell>
										<TableCell>{task.progress_current} / {task.progress_total}</TableCell>
										<TableCell><StatusBadge status={task.task_status} /></TableCell>
										<TableCell className="max-w-72 truncate text-muted-foreground">{task.error_message ?? "-"}</TableCell>
										<TableCell>
											<Button
												disabled={!isFailedStatus(task.task_status)}
												onClick={() => retryTask(task.rag_task_id)}
												size="sm"
												variant="outline"
											>
												<RotateCcwIcon />
												重试
											</Button>
										</TableCell>
									</TableRow>
								);
							})}
						</TableBody>
					</Table>
					{data.tasks.length === 0 && <EmptyState text="暂无向量化任务快照" />}
				</CardContent>
			</Card>
		</main>
	);
}

function MetricCard({
	title,
	value,
	meta,
}: {
	title: string;
	value: number | string;
	meta: string;
}) {
	return (
		<div className="rounded-lg border bg-card p-4 text-card-foreground shadow-xs">
			<p className="text-sm text-muted-foreground">{title}</p>
			<div className="mt-3 truncate text-2xl font-semibold tracking-normal">
				{typeof value === "number" ? numberFormatter.format(value) : value}
			</div>
			<p className="mt-1 truncate text-xs text-muted-foreground">{meta}</p>
		</div>
	);
}

function StatusBadge({ status }: { status: string }) {
	const normalized = status.toLowerCase();
	if (isFailedStatus(normalized)) {
		return <Badge variant="destructive">{status}</Badge>;
	}
	if (["active", "completed", "success", "succeeded", "done"].includes(normalized)) {
		return <Badge>{status}</Badge>;
	}
	if (["running", "processing", "queued", "pending"].includes(normalized)) {
		return <Badge variant="secondary">{status}</Badge>;
	}
	return <Badge variant="outline">{status}</Badge>;
}

function EmptyState({ text }: { text: string }) {
	return (
		<div className="rounded-md border border-dashed p-6 text-center text-sm text-muted-foreground">
			{text}
		</div>
	);
}

function displayLogicalName(mapping: RagMapping) {
	return logicalNameLabels[mapping.logical_name] ?? mapping.display_name ?? mapping.logical_name;
}

function isFailedStatus(status: string) {
	return ["failed", "error", "errored"].includes(status.toLowerCase());
}

function formatDateTime(value?: string | null) {
	if (!value) {
		return "-";
	}
	return new Intl.DateTimeFormat("zh-CN", {
		month: "2-digit",
		day: "2-digit",
		hour: "2-digit",
		minute: "2-digit",
	}).format(new Date(value));
}

function extractTaskId(payload: Record<string, unknown>) {
	const candidates = [
		payload.task_id,
		payload.rag_task_id,
		payload.id,
		(payload.task as Record<string, unknown> | undefined)?.id,
		(payload.task as Record<string, unknown> | undefined)?.task_id,
	];
	return candidates.find((candidate): candidate is string => typeof candidate === "string") ?? "";
}
