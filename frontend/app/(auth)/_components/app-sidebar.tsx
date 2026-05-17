"use client";

import { LogoIcon } from "@/components/logo";
import { Switch } from "@/components/ui/switch";
import {
	Sidebar,
	SidebarContent,
	SidebarFooter,
	SidebarHeader,
	SidebarMenu,
	SidebarMenuButton,
	SidebarMenuItem,
} from "@/components/ui/sidebar";
import { NavGroup } from "@/app/(auth)/_components/nav-group";
import { navGroups } from "@/app/(auth)/_components/app-shared";
import { MoonIcon, SunIcon } from "lucide-react";
import { useTheme } from "next-themes";

export function AppSidebar() {
	const { resolvedTheme, setTheme } = useTheme();
	const isDark = resolvedTheme === "dark";

	return (
		<Sidebar collapsible="icon" variant="floating">
			<SidebarHeader className="h-14 justify-center">
				<SidebarMenuButton asChild>
					<a href="#link">
						<LogoIcon />
						<span className="font-medium">Efferd</span>
					</a>
				</SidebarMenuButton>
			</SidebarHeader>
			<SidebarContent>
				{navGroups.map((group, index) => (
					<NavGroup key={`sidebar-group-${index}`} {...group} />
				))}
			</SidebarContent>
			<SidebarFooter>
				<SidebarMenu className="mt-2">
					<SidebarMenuItem className="flex h-12 items-center justify-center gap-3.5 rounded-md px-2 text-sidebar-foreground">
						<SunIcon className="size-6 shrink-0" />
						<Switch
							aria-label="切换深色模式"
							checked={isDark}
							className="h-6 w-11 [&_[data-slot=switch-thumb]]:size-5 [&_[data-slot=switch-thumb]]:data-checked:translate-x-5"
							onCheckedChange={(checked) =>
								setTheme(checked ? "dark" : "light")
							}
						/>
						<MoonIcon className="size-6 shrink-0" />
					</SidebarMenuItem>
				</SidebarMenu>
			</SidebarFooter>
		</Sidebar>
	);
}
