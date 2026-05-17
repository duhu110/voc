"use client";

import {
    Collapsible,
    CollapsibleContent,
    CollapsibleTrigger,
} from "@/components/ui/collapsible";
import {
    SidebarGroup,
    SidebarGroupLabel,
    SidebarMenu,
    SidebarMenuButton,
    SidebarMenuItem,
    SidebarMenuSub,
    SidebarMenuSubButton,
    SidebarMenuSubItem,
} from "@/components/ui/sidebar";
import type { SidebarNavGroup } from "@/app/(auth)/_components/app-shared";
import { ChevronRightIcon } from "lucide-react";
import { usePathname } from "next/navigation";

export function NavGroup({ label, items }: SidebarNavGroup) {
    const pathname = usePathname();

    const isItemActive = (path?: string) => {
        if (!path || path.startsWith("#")) {
            return false;
        }
        if (path === "/") {
            return pathname === "/";
        }
        return pathname === path || pathname.startsWith(`${path}/`);
    };

    return (
        <SidebarGroup>
            {label && <SidebarGroupLabel>{label}</SidebarGroupLabel>}
            <SidebarMenu>
                {items.map((item) => {
                    const itemActive = isItemActive(item.path);
                    const subItemActive = item.subItems?.some((subItem) =>
                        isItemActive(subItem.path)
                    );

                    return (
                        <Collapsible
                            asChild
                            className="group/collapsible"
                            defaultOpen={itemActive || subItemActive}
                            key={item.title}
                        >
                            <SidebarMenuItem>
                                {item.subItems?.length ? (
                                    <>
                                        <CollapsibleTrigger asChild>
                                            <SidebarMenuButton isActive={itemActive}>
                                                {item.icon}
                                                <span>{item.title}</span>
                                                <ChevronRightIcon className="ml-auto transition-transform duration-200 group-data-[state=open]/collapsible:rotate-90" />
                                            </SidebarMenuButton>
                                        </CollapsibleTrigger>
                                        <CollapsibleContent>
                                            <SidebarMenuSub>
                                                {item.subItems?.map((subItem) => (
                                                    <SidebarMenuSubItem key={subItem.title}>
                                                        <SidebarMenuSubButton
                                                            asChild
                                                            isActive={isItemActive(subItem.path)}
                                                        >
                                                            <a href={subItem.path}>
                                                                {subItem.icon}
                                                                <span>{subItem.title}</span>
                                                            </a>
                                                        </SidebarMenuSubButton>
                                                    </SidebarMenuSubItem>
                                                ))}
                                            </SidebarMenuSub>
                                        </CollapsibleContent>
                                    </>
                                ) : (
                                    <SidebarMenuButton asChild isActive={itemActive}>
                                        <a href={item.path}>
                                            {item.icon}
                                            <span>{item.title}</span>
                                        </a>
                                    </SidebarMenuButton>
                                )}
                            </SidebarMenuItem>
                        </Collapsible>
                    );
                })}
            </SidebarMenu>
        </SidebarGroup>
    );
}
