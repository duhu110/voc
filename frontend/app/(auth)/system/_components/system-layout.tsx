import type { ReactNode } from "react";
import Link from "next/link";
import {
	ActivityIcon,
	ArrowRightIcon,
	FolderTreeIcon,
	ShieldCheckIcon,
	SlidersHorizontalIcon,
	TagsIcon,
	UsersRoundIcon,
} from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from "@/components/ui/card";
import { cn } from "@/lib/utils";

export const systemSections = [
	{
		title: "用户管理",
		description: "查看管理员、运营人员、只读用户的账号状态。",
		href: "/system/users",
		icon: UsersRoundIcon,
		endpoint: "GET /users",
	},
	{
		title: "分类标签",
		description: "读取分类树与产品、诉求、情绪、风险标签。",
		href: "/system/taxonomy",
		icon: TagsIcon,
		endpoint: "GET /taxonomy/*",
	},
	{
		title: "任务中心",
		description: "查询 RAG 文档处理任务和知识库服务状态。",
		href: "/system/tasks",
		icon: FolderTreeIcon,
		endpoint: "GET /rag/tasks/{id}",
	},
	{
		title: "系统配置",
		description: "检查后端健康、数据库连接、RAG 服务与管理员权限。",
		href: "/system/config",
		icon: SlidersHorizontalIcon,
		endpoint: "GET /health",
	},
] as const;

export function SystemPageHeader({
	title,
	description,
	children,
}: {
	title: string;
	description: string;
	children?: ReactNode;
}) {
	return (
		<div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
			<div>
				<div className="flex items-center gap-2 text-sm text-muted-foreground">
					<ShieldCheckIcon className="size-4" />
					<span>系统管理</span>
				</div>
				<h1 className="mt-2 text-2xl font-semibold tracking-normal">
					{title}
				</h1>
				<p className="mt-1 max-w-3xl text-sm text-muted-foreground">
					{description}
				</p>
			</div>
			{children}
		</div>
	);
}

export function SystemSectionGrid({ className }: { className?: string }) {
	return (
		<div className={cn("grid gap-3 md:grid-cols-2 xl:grid-cols-4", className)}>
			{systemSections.map((section) => {
				const Icon = section.icon;
				return (
					<Card key={section.href} size="sm">
						<CardHeader>
							<div className="flex items-start justify-between gap-3">
								<div className="rounded-md border bg-muted p-2 text-muted-foreground">
									<Icon className="size-4" />
								</div>
								<Badge variant="outline">{section.endpoint}</Badge>
							</div>
							<CardTitle>{section.title}</CardTitle>
							<CardDescription>{section.description}</CardDescription>
						</CardHeader>
						<CardContent>
							<Button asChild size="sm" variant="outline">
								<Link href={section.href}>
									进入
									<ArrowRightIcon className="size-4" />
								</Link>
							</Button>
						</CardContent>
					</Card>
				);
			})}
		</div>
	);
}

export function DataNotice({
	title,
	description,
	variant = "default",
}: {
	title: string;
	description: string;
	variant?: "default" | "error";
}) {
	return (
		<div
			className={cn(
				"rounded-lg border bg-card p-4 text-sm text-card-foreground",
				variant === "error" && "border-destructive/30 text-destructive"
			)}
		>
			<div className="flex items-start gap-3">
				<ActivityIcon className="mt-0.5 size-4 shrink-0" />
				<div>
					<p className="font-medium">{title}</p>
					<p className="mt-1 text-muted-foreground">{description}</p>
				</div>
			</div>
		</div>
	);
}

export function StatusBadge({ status }: { status?: string | null }) {
	const normalized = (status ?? "unknown").toLowerCase();
	const variant =
		normalized === "active" || normalized === "ok" || normalized === "success"
			? "default"
			: normalized === "inactive" ||
				  normalized === "locked" ||
				  normalized === "error" ||
				  normalized === "degraded"
				? "destructive"
				: "outline";

	return <Badge variant={variant}>{status ?? "unknown"}</Badge>;
}
