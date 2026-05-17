import Link from "next/link";

import { Logo } from "@/components/logo";
import { FullWidthDivider } from "@/components/ui/full-width-divider";
import { LoginForm } from "@/app/auth/_components/login-form";

export default function AuthPage() {
	return (
		<div className="relative w-full overflow-hidden px-4 md:h-screen">
			<div className="relative mx-auto flex min-h-screen w-full max-w-sm flex-col justify-center border-x *:px-6">
				<div className="flex flex-col space-y-6">
					<Link aria-label="Home" href="/">
						<Logo className="h-4.5" />
					</Link>
					<div className="space-y-1">
						<h1 className="font-semibold text-xl tracking-wide">
							VOC 后台登录
						</h1>
						<p className="text-base text-muted-foreground">
							使用后台账号进入工单运营系统。
						</p>
					</div>
				</div>

				<div className="relative my-6 flex size-full flex-col gap-4 py-8">
					<FullWidthDivider position="top" />
					<LoginForm />
					<FullWidthDivider position="bottom" />
				</div>

				<p className="text-center text-muted-foreground text-sm">
					登录状态将用于访问后台受保护页面。
				</p>
			</div>
		</div>
	);
}
