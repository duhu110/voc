"use client";

import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { AppBreadcrumbs } from "@/app/(auth)/_components/app-breadcrumbs";
import { AppSidebarTrigger } from "@/app/(auth)/_components/app-sidebar-trigger";
import { navLinks } from "@/app/(auth)/_components/app-shared";
import { NavUser } from "@/app/(auth)/_components/nav-user";
import type { CurrentUser } from "@/app/(auth)/auth";
import { BellIcon } from "lucide-react";
import { usePathname } from "next/navigation";

export function AppHeader({ user }: { user: CurrentUser | null }) {
	const pathname = usePathname();
	const activeItem =
		navLinks.find((item) => {
			if (!item.path || item.path.startsWith("#")) {
				return false;
			}
			if (item.path === "/") {
				return pathname === "/";
			}
			return pathname === item.path || pathname.startsWith(`${item.path}/`);
		}) ?? navLinks[0];

	return (
		<header
			className={cn(
				"pxx-4 mb-6 flex items-center justify-between gap-2 md:px-2"
			)}
		>
			<div className="flex items-center gap-3">
				<AppSidebarTrigger />
				<Separator
					className="mr-2 h-4 data-[orientation=vertical]:self-center"
					orientation="vertical"
				/>
				<AppBreadcrumbs page={activeItem} />
			</div>
			<div className="flex items-center gap-3">
				<Button aria-label="Notifications" size="icon" variant="ghost">
					<BellIcon />
				</Button>
				<Separator
					className="h-4 data-[orientation=vertical]:self-center"
					orientation="vertical"
				/>
				<NavUser user={user} />
			</div>
		</header>
	);
}
