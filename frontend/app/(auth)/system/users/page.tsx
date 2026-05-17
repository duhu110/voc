import { SearchIcon, UsersRoundIcon } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
	Card,
	CardContent,
	CardHeader,
	CardTitle,
} from "@/components/ui/card";
import {
	Table,
	TableBody,
	TableCell,
	TableHead,
	TableHeader,
	TableRow,
} from "@/components/ui/table";
import { DataNotice, StatusBadge, SystemPageHeader } from "@/app/(auth)/system/_components/system-layout";
import { backendFetch, firstParam } from "@/app/(auth)/system/_lib/api";

type SearchParams = Record<string, string | string[] | undefined>;

type UserItem = {
	id: number;
	username: string;
	display_name?: string | null;
	role: string;
	status: string;
	token_version?: number;
	last_login_at?: string | null;
	created_at?: string | null;
	updated_at?: string | null;
};

type UsersResponse = {
	status: string;
	items?: UserItem[];
	page?: number;
	page_size?: number;
	total?: number;
};

const roleLabels: Record<string, string> = {
	admin: "系统管理员",
	operator: "运营人员",
	viewer: "只读用户",
};

const statusLabels: Record<string, string> = {
	active: "启用",
	inactive: "停用",
	locked: "锁定",
};

export default async function UsersPage({
	searchParams,
}: {
	searchParams?: Promise<SearchParams>;
}) {
	const params = (await searchParams) ?? {};
	const q = firstParam(params.q);
	const role = firstParam(params.role);
	const status = firstParam(params.status);
	const page = firstParam(params.page, "1");
	const query = new URLSearchParams({ page, page_size: "20" });

	if (q) query.set("q", q);
	if (role) query.set("role", role);
	if (status) query.set("status", status);

	const users = await backendFetch<UsersResponse>(`/users?${query}`);

	return (
		<main className="flex flex-col gap-4">
			<SystemPageHeader
				title="用户管理"
				description="数据来自 backend_api/routes/users.py，当前页面读取用户列表、角色、状态和登录时间。"
			/>

			<Card>
				<CardHeader>
					<CardTitle className="flex items-center gap-2">
						<UsersRoundIcon className="size-4" />
						筛选用户
					</CardTitle>
				</CardHeader>
				<CardContent>
					<form className="grid gap-3 md:grid-cols-[minmax(220px,1fr)_160px_160px_auto]">
						<div className="relative">
							<SearchIcon className="pointer-events-none absolute left-2.5 top-2.5 size-4 text-muted-foreground" />
							<Input
								className="pl-8"
								defaultValue={q}
								name="q"
								placeholder="用户名或显示名"
							/>
						</div>
						<select
							className="h-9 rounded-md border border-input bg-background px-2.5 text-sm shadow-xs"
							defaultValue={role}
							name="role"
						>
							<option value="">全部角色</option>
							<option value="admin">系统管理员</option>
							<option value="operator">运营人员</option>
							<option value="viewer">只读用户</option>
						</select>
						<select
							className="h-9 rounded-md border border-input bg-background px-2.5 text-sm shadow-xs"
							defaultValue={status}
							name="status"
						>
							<option value="">全部状态</option>
							<option value="active">启用</option>
							<option value="inactive">停用</option>
							<option value="locked">锁定</option>
						</select>
						<Button type="submit">查询</Button>
					</form>
				</CardContent>
			</Card>

			{!users.ok ? (
				<DataNotice
					title="用户列表读取失败"
					description={users.error}
					variant="error"
				/>
			) : (
				<Card>
					<CardHeader>
						<div className="flex items-center justify-between gap-3">
							<CardTitle>账号列表</CardTitle>
							<Badge variant="outline">共 {users.data.total ?? 0} 个账号</Badge>
						</div>
					</CardHeader>
					<CardContent>
						<Table>
							<TableHeader>
								<TableRow>
									<TableHead>账号</TableHead>
									<TableHead>显示名</TableHead>
									<TableHead>角色</TableHead>
									<TableHead>状态</TableHead>
									<TableHead>最后登录</TableHead>
									<TableHead>更新时间</TableHead>
								</TableRow>
							</TableHeader>
							<TableBody>
								{(users.data.items ?? []).map((user) => (
									<TableRow key={user.id}>
										<TableCell className="font-medium">{user.username}</TableCell>
										<TableCell>{user.display_name ?? "-"}</TableCell>
										<TableCell>{roleLabels[user.role] ?? user.role}</TableCell>
										<TableCell>
											<StatusBadge status={statusLabels[user.status] ?? user.status} />
										</TableCell>
										<TableCell>{formatDateTime(user.last_login_at)}</TableCell>
										<TableCell>{formatDateTime(user.updated_at)}</TableCell>
									</TableRow>
								))}
								{(users.data.items ?? []).length === 0 && (
									<TableRow>
										<TableCell
											className="h-24 text-center text-muted-foreground"
											colSpan={6}
										>
											暂无用户数据
										</TableCell>
									</TableRow>
								)}
							</TableBody>
						</Table>
					</CardContent>
				</Card>
			)}
		</main>
	);
}

function formatDateTime(value?: string | null) {
	if (!value) return "-";
	const date = new Date(value);
	if (Number.isNaN(date.getTime())) return value;
	return new Intl.DateTimeFormat("zh-CN", {
		month: "2-digit",
		day: "2-digit",
		hour: "2-digit",
		minute: "2-digit",
	}).format(date);
}
