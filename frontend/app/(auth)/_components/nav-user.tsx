"use client";

import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import {
	DropdownMenu,
	DropdownMenuContent,
	DropdownMenuGroup,
	DropdownMenuItem,
	DropdownMenuLabel,
	DropdownMenuSeparator,
	DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { logout } from "@/app/(auth)/actions";
import type { CurrentUser } from "@/app/(auth)/auth";
import { LogOutIcon, ShieldUserIcon, UserRoundIcon } from "lucide-react";

const roleLabels: Record<string, string> = {
	admin: "系统管理员",
	operator: "运营人员",
	viewer: "只读用户",
};

export function NavUser({ user }: { user: CurrentUser | null }) {
	const name = user?.display_name || user?.username || "未登录用户";
	const username = user?.username || "unknown";
	const role = user?.role ? roleLabels[user.role] ?? user.role : "未登录";

	return (
		<DropdownMenu>
			<DropdownMenuTrigger asChild>
				<Avatar aria-label="用户菜单" className="size-8">
					<AvatarFallback>
						<UserRoundIcon className="size-4" />
					</AvatarFallback>
				</Avatar>
			</DropdownMenuTrigger>
			<DropdownMenuContent align="end" className="w-60">
				<DropdownMenuItem className="flex items-center justify-start gap-2">
					<DropdownMenuLabel className="flex items-center gap-3">
						<Avatar className="size-10">
							<AvatarFallback>
								<ShieldUserIcon className="size-5" />
							</AvatarFallback>
						</Avatar>
						<div>
							<span className="font-medium text-foreground">{name}</span>{" "}
							<br />
							<div className="max-w-full overflow-hidden overflow-ellipsis whitespace-nowrap text-muted-foreground text-xs">
								{username}
							</div>
							<div className="mt-0.5 text-[10px] text-muted-foreground">
								{role}
							</div>
						</div>
					</DropdownMenuLabel>
				</DropdownMenuItem>
				<DropdownMenuSeparator />
				<DropdownMenuGroup>
					<form action={logout}>
						<DropdownMenuItem
							asChild
							className="w-full cursor-pointer"
							variant="destructive"
						>
							<button type="submit">
								<LogOutIcon />
								退出登录
							</button>
						</DropdownMenuItem>
					</form>
				</DropdownMenuGroup>
			</DropdownMenuContent>
		</DropdownMenu>
	);
}
