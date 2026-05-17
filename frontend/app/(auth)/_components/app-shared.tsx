import type { ReactNode } from "react";
import {
	BookOpenTextIcon,
	DatabaseIcon,
	FileClockIcon,
	FolderTreeIcon,
	HomeIcon,
	LightbulbIcon,
	SettingsIcon,
	SlidersHorizontalIcon,
	TagsIcon,
	UsersRoundIcon,
	TicketIcon,
} from "lucide-react";

export type SidebarNavItem = {
	title: string;
	path?: string;
	icon?: ReactNode;
	isActive?: boolean;
	subItems?: SidebarNavItem[];
};

export type SidebarNavGroup = {
	label: string;
	items: SidebarNavItem[];
};

export const navGroups: SidebarNavGroup[] = [
	{
		label: "VOC 运营",
		items: [
			{
				title: "首页总览",
				path: "/",
				icon: <HomeIcon />,
			},
			{
				title: "工单中心",
				path: "/tickets",
				icon: <TicketIcon />,
			},
			{
				title: "建议生成",
				path: "#/advice",
				icon: <LightbulbIcon />,
			},
			{
				title: "专家经验库",
				path: "/expert-playbooks",
				icon: <BookOpenTextIcon />,
			},
			{
				title: "历史建议库",
				path: "/handling-advices",
				icon: <FileClockIcon />,
			},
			{
				title: "知识库 / RAG",
				path: "/rag",
				icon: <DatabaseIcon />,
			},
			{
				title: "系统管理",
				path: "/system",
				icon: <SettingsIcon />,
				subItems: [
					{
						title: "用户管理",
						path: "/system/users",
						icon: <UsersRoundIcon />,
					},
					{
						title: "分类标签",
						path: "/system/taxonomy",
						icon: <TagsIcon />,
					},
					{
						title: "任务中心",
						path: "/system/tasks",
						icon: <FolderTreeIcon />,
					},
					{
						title: "系统配置",
						path: "/system/config",
						icon: <SlidersHorizontalIcon />,
					},
				],
			},
		],
	},
];

export const navLinks: SidebarNavItem[] = [
	...navGroups.flatMap((group) =>
		group.items.flatMap((item) =>
			item.subItems?.length ? [item, ...item.subItems] : [item]
		)
	),
];
