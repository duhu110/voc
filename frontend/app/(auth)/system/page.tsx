import { ActivityIcon, DatabaseIcon, SettingsIcon, ShieldIcon } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import {
	Card,
	CardContent,
	CardHeader,
} from "@/components/ui/card";
import { DataNotice, StatusBadge, SystemPageHeader, SystemSectionGrid } from "@/app/(auth)/system/_components/system-layout";
import { backendFetch } from "@/app/(auth)/system/_lib/api";

type HealthResponse = {
	status: string;
	database?: { status?: string; db?: string; db_user?: string };
	rag?: { status?: string; detail?: unknown };
};

type AdminCheckResponse = {
	status: string;
	user?: { username?: string; role?: string; status?: string };
};

export default async function SystemPage() {
	const [health, admin] = await Promise.all([
		backendFetch<HealthResponse>("/health"),
		backendFetch<AdminCheckResponse>("/auth/admin-check"),
	]);

	return (
		<main className="flex flex-col gap-4">
			<SystemPageHeader
				title="系统管理"
				description="集中管理账号、分类标签、后台任务与运行配置状态。"
			/>

			{(!health.ok || !admin.ok) && (
				<DataNotice
					title="部分管理接口暂时不可用"
					description={!health.ok ? health.error : admin.ok ? "" : admin.error}
					variant="error"
				/>
			)}

			<section className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
				<StatusCard
					title="后端服务"
					icon={<ActivityIcon className="size-4" />}
					status={health.ok ? health.data.status : "error"}
					meta={health.ok ? "backend_api /health" : health.error}
				/>
				<StatusCard
					title="数据库"
					icon={<DatabaseIcon className="size-4" />}
					status={health.ok ? health.data.database?.status : "unknown"}
					meta={
						health.ok
							? `${health.data.database?.db ?? "unknown"} / ${
									health.data.database?.db_user ?? "unknown"
								}`
							: "未取得数据库状态"
					}
				/>
				<StatusCard
					title="RAG 服务"
					icon={<SettingsIcon className="size-4" />}
					status={health.ok ? health.data.rag?.status : "unknown"}
					meta="RagClient health"
				/>
				<StatusCard
					title="管理权限"
					icon={<ShieldIcon className="size-4" />}
					status={admin.ok ? admin.data.user?.role : "denied"}
					meta={
						admin.ok
							? `${admin.data.user?.username ?? "unknown"} / ${
									admin.data.user?.status ?? "unknown"
								}`
							: admin.error
					}
				/>
			</section>

			<SystemSectionGrid />
		</main>
	);
}

function StatusCard({
	title,
	icon,
	status,
	meta,
}: {
	title: string;
	icon: React.ReactNode;
	status?: string | null;
	meta: string;
}) {
	return (
		<Card size="sm">
			<CardHeader className="pb-0">
				<div className="flex items-center justify-between gap-3">
					<div className="flex items-center gap-2 text-sm text-muted-foreground">
						{icon}
						<span>{title}</span>
					</div>
					<StatusBadge status={status} />
				</div>
			</CardHeader>
			<CardContent>
				<p className="truncate text-sm text-muted-foreground" title={meta}>
					{meta}
				</p>
				<Badge className="mt-3" variant="outline">
					实时读取
				</Badge>
			</CardContent>
		</Card>
	);
}
