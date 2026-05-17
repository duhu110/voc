import { DatabaseIcon } from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { RagManagementClient, type RagDocument, type RagMapping, type RagTask } from "@/app/(auth)/rag/rag-management-client";

const BACKEND_API_URL =
	process.env.BACKEND_API_URL ?? "http://127.0.0.1:8010";

type ListResponse<T> = {
	status: string;
	items?: T[];
};

async function fetchRagData() {
	const [mappingsResponse, documentsResponse, tasksResponse] = await Promise.all([
		fetch(`${BACKEND_API_URL}/rag/mappings`, { cache: "no-store" }),
		fetch(`${BACKEND_API_URL}/rag/documents?limit=80`, { cache: "no-store" }),
		fetch(`${BACKEND_API_URL}/rag/tasks?limit=80`, { cache: "no-store" }),
	]);

	if (!mappingsResponse.ok) {
		throw new Error("rag request failed");
	}

	const mappings = (await mappingsResponse.json()) as ListResponse<RagMapping>;
	const documents = documentsResponse.ok
		? ((await documentsResponse.json()) as ListResponse<RagDocument>)
		: { status: "unavailable", items: [] };
	const tasks = tasksResponse.ok
		? ((await tasksResponse.json()) as ListResponse<RagTask>)
		: { status: "unavailable", items: [] };

	return {
		mappings: mappings.items ?? [],
		documents: documents.items ?? [],
		tasks: tasks.items ?? [],
	};
}

export default async function RagPage() {
	let data: Awaited<ReturnType<typeof fetchRagData>> | null = null;

	try {
		data = await fetchRagData();
	} catch {
		data = null;
	}

	if (!data) {
		return (
			<main className="flex flex-col gap-4">
				<Card>
					<CardHeader>
						<div className="flex items-center gap-3">
							<div className="rounded-md border bg-muted p-2 text-muted-foreground">
								<DatabaseIcon className="size-4" />
							</div>
							<div>
								<CardTitle>知识库 / RAG</CardTitle>
								<CardDescription>
									无法连接后端 RAG 接口，请确认 backend_api 已启动且数据库表已初始化。
								</CardDescription>
							</div>
						</div>
					</CardHeader>
					<CardContent className="text-sm text-muted-foreground">
						需要的接口包括 /rag/mappings、/rag/documents、/rag/tasks 和
						/rag/mappings/{"{logical_name}"}/search。
					</CardContent>
				</Card>
			</main>
		);
	}

	return <RagManagementClient apiBaseUrl={BACKEND_API_URL} initialData={data} />;
}
