"use client";

import { useActionState, useEffect } from "react";
import { LockIcon, LogInIcon, UserIcon } from "lucide-react";
import { toast } from "sonner";

import { login } from "@/app/auth/actions";
import { Button } from "@/components/ui/button";
import {
	InputGroup,
	InputGroupAddon,
	InputGroupInput,
} from "@/components/ui/input-group";

const initialState = {
	error: undefined,
	errorId: undefined,
};

export function LoginForm() {
	const [state, formAction, pending] = useActionState(login, initialState);

	useEffect(() => {
		if (state.error) {
			toast.error(state.error);
		}
	}, [state.error, state.errorId]);

	return (
		<form action={formAction} className="space-y-3">
			<InputGroup>
				<InputGroupInput
					aria-label="用户名"
					autoComplete="username"
					name="username"
					placeholder="用户名"
					required
					type="text"
				/>
				<InputGroupAddon align="inline-start">
					<UserIcon />
				</InputGroupAddon>
			</InputGroup>

			<InputGroup>
				<InputGroupInput
					aria-label="密码"
					autoComplete="current-password"
					name="password"
					placeholder="密码"
					required
					type="password"
				/>
				<InputGroupAddon align="inline-start">
					<LockIcon />
				</InputGroupAddon>
			</InputGroup>

			<Button className="w-full" disabled={pending} size="sm" type="submit">
				<LogInIcon data-icon="inline-start" />
				{pending ? "登录中..." : "登录"}
			</Button>
		</form>
	);
}
