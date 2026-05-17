import { SidebarInset, SidebarProvider } from "@/components/ui/sidebar";
import { AppHeader } from "@/app/(auth)/_components/app-header";
import { AppSidebar } from "@/app/(auth)/_components/app-sidebar";
import { getCurrentUser } from "@/app/(auth)/auth";

export default async function AuthLayout({
	children,
}: {
	children: React.ReactNode;
}) {
	const user = await getCurrentUser();

	return (
		<SidebarProvider>
			<AppSidebar />
			<SidebarInset className="p-4 md:p-6">
				<AppHeader user={user} />
				<div className="flex flex-1 flex-col gap-4 overflow-y-auto">
					{children}
				</div>
			</SidebarInset>
		</SidebarProvider>
	);
}
