import { RefreshCwIcon, SearchIcon } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
	Card,
	CardContent,
	CardHeader,
	CardTitle,
} from "@/components/ui/card";
import { DataNotice, StatusBadge, SystemPageHeader } from "@/app/(auth)/system/_components/system-layout";
import { backendFetch, firstParam } from "@/app/(auth)/system/_lib/api";

type SearchParams = Record<string, string | string[] | undefined>;

type RagHealthResponse = {
	status?: string;
	detail?: unknown;
};

type TaskResponse = {
	status?: string;
	task?: unknown;
	[key: string]: unknown;
};

export default async function TasksPage({
	searchParams,
}: {
	searchParams?: Promise<SearchParams>;
}) {
	const params = (await searchParams) ?? {};
	const taskId = firstParam(params.task_id).trim();
	const [health, task] = await Promise.all([
		backendFetch<RagHealthResponse>("/rag/health"),
		taskId
			? backendFetch<TaskResponse>(`/rag/tasks/${encodeURIComponent(taskId)}`)
			: Promise.resolve(null),
	]);

	return (
		<main className="flex flex-col gap-4">
			<SystemPageHeader
				title="任务中心"
				description="数据来自 backend_api/routes/rag.py，可查询 RAG 文档上传后的异步任务状态。"
			/>

			<section className="grid gap-4 xl:grid-cols-[360px_1fr]">
				<Card>
					<CardHeader>
						<CardTitle className="flex items-center gap-2">
							<SearchIcon className="size-4" />
							任务查询
						</CardTitle>
					</CardHeader>
					<CardContent>
						<form className="flex flex-col gap-3">
							<Input
								defaultValue={taskId}
								name="task_id"
								placeholder="输入 RAG task_id"
							/>
							<Button type="submit">
								<SearchIcon className="size-4" />
								查询任务
							</Button>
						</form>

						<div className="mt-6 rounded-lg border bg-muted/30 p-4">
							<div className="flex items-center justify-between gap-3">
								<p className="text-sm font-medium">RAG 服务状态</p>
								<StatusBadge
									status={health.ok ? health.data.status ?? "success" : "error"}
								/>
							</div>
							<p className="mt-2 text-xs text-muted-foreground">
								接口：GET /rag/health
							</p>
						</div>
					</CardContent>
				</Card>

				<Card>
					<CardHeader>
						<div className="flex items-center justify-between gap-3">
							<CardTitle>任务详情</CardTitle>
							<Button asChild size="sm" variant="outline">
								<a href={taskId ? `/system/tasks?task_id=${encodeURIComponent(taskId)}` : "/system/tasks"}>
									<RefreshCwIcon className="size-4" />
									刷新
								</a>
							</Button>
						</div>
					</CardHeader>
					<CardContent>
						{!taskId ? (
							<DataNotice
								title="等待输入任务编号"
								description="上传知识库文档后，将返回的 task_id 填入这里即可查看处理进度。"
							/>
						) : task && !task.ok ? (
							<DataNotice
								title="任务读取失败"
								description={task.error}
								variant="error"
							/>
						) : (
							<pre className="max-h-[620px] overflow-auto rounded-lg border bg-muted/40 p-4 text-xs leading-6">
								{JSON.stringify(task?.data ?? {}, null, 2)}
							</pre>
						)}
					</CardContent>
				</Card>
			</section>
		</main>
	);
}
