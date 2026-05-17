import { DatabaseIcon, ServerCogIcon, ShieldCheckIcon } from "lucide-react";

import {
	Card,
	CardContent,
	CardHeader,
	CardTitle,
} from "@/components/ui/card";
import { DataNotice, StatusBadge, SystemPageHeader } from "@/app/(auth)/system/_components/system-layout";
import { BACKEND_API_URL, backendFetch } from "@/app/(auth)/system/_lib/api";

type HealthResponse = {
	status: string;
	database?: Record<string, unknown>;
	rag?: Record<string, unknown>;
};

type AdminCheckResponse = {
	status: string;
	user?: Record<string, unknown>;
};

export default async function ConfigPage() {
	const [health, admin] = await Promise.all([
		backendFetch<HealthResponse>("/health"),
		backendFetch<AdminCheckResponse>("/auth/admin-check"),
	]);

	return (
		<main className="flex flex-col gap-4">
			<SystemPageHeader
				title="系统配置"
				description="展示当前前端连接的后端地址、健康检查、数据库连接和管理员权限检查结果。"
			/>

			<section className="grid gap-4 xl:grid-cols-3">
				<ConfigCard
					icon={<ServerCogIcon className="size-4" />}
					title="后端地址"
					status="active"
					rows={[
						["BACKEND_API_URL", BACKEND_API_URL],
						["Health endpoint", "/health"],
						["Admin endpoint", "/auth/admin-check"],
					]}
				/>
				<ConfigCard
					icon={<DatabaseIcon className="size-4" />}
					title="数据库"
					status={health.ok ? String(health.data.database?.status ?? "unknown") : "error"}
					rows={health.ok ? objectRows(health.data.database) : [["error", health.error]]}
				/>
				<ConfigCard
					icon={<ShieldCheckIcon className="size-4" />}
					title="管理员权限"
					status={admin.ok ? String(admin.data.user?.role ?? "unknown") : "denied"}
					rows={admin.ok ? objectRows(admin.data.user) : [["error", admin.error]]}
				/>
			</section>

			<Card>
				<CardHeader>
					<CardTitle>健康检查原始响应</CardTitle>
				</CardHeader>
				<CardContent>
					{!health.ok ? (
						<DataNotice
							title="健康检查读取失败"
							description={health.error}
							variant="error"
						/>
					) : (
						<pre className="max-h-[520px] overflow-auto rounded-lg border bg-muted/40 p-4 text-xs leading-6">
							{JSON.stringify(health.data, null, 2)}
						</pre>
					)}
				</CardContent>
			</Card>
		</main>
	);
}

function ConfigCard({
	icon,
	title,
	status,
	rows,
}: {
	icon: React.ReactNode;
	title: string;
	status: string;
	rows: Array<[string, string]>;
}) {
	return (
		<Card size="sm">
			<CardHeader>
				<div className="flex items-center justify-between gap-3">
					<CardTitle className="flex items-center gap-2">
						{icon}
						{title}
					</CardTitle>
					<StatusBadge status={status} />
				</div>
			</CardHeader>
			<CardContent>
				<div className="space-y-3">
					{rows.map(([key, value]) => (
						<div className="grid gap-1" key={key}>
							<div className="text-xs text-muted-foreground">{key}</div>
							<div className="break-all text-sm font-medium">{value}</div>
						</div>
					))}
				</div>
			</CardContent>
		</Card>
	);
}

function objectRows(value: Record<string, unknown> | undefined) {
	return Object.entries(value ?? {}).map(([key, item]) => [
		key,
		typeof item === "string" ? item : JSON.stringify(item),
	]) as Array<[string, string]>;
}
