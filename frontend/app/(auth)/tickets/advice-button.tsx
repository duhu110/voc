"use client";

import { useActionState } from "react";
import { Loader2Icon, RefreshCwIcon } from "lucide-react";

import { regenerateTicketAdvice } from "@/app/(auth)/tickets/actions";
import type { AdviceActionState } from "@/app/(auth)/tickets/types";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

const initialState: AdviceActionState = { status: "idle" };

export function AdviceRegenerator({ ticketId }: { ticketId: string }) {
	const [state, formAction, pending] = useActionState(
		regenerateTicketAdvice,
		initialState
	);

	return (
		<div className="flex flex-col gap-4">
			<form action={formAction}>
				<input name="ticket_id" type="hidden" value={ticketId} />
				<Button disabled={pending} type="submit">
					{pending ? (
						<Loader2Icon className="animate-spin" />
					) : (
						<RefreshCwIcon />
					)}
					重新生成建议
				</Button>
			</form>

			{state.status === "error" && (
				<div className="rounded-md border border-destructive/30 bg-destructive/10 p-3 text-sm text-destructive">
					{state.error}
				</div>
			)}

			{state.status === "success" && state.result && (
				<div className="rounded-md border bg-muted/20 p-4">
					<div>
						<h2 className="flex items-center gap-2 text-sm font-medium">
							生成结果
							{state.result.confidence && (
								<Badge variant="secondary">
									置信度 {String(state.result.confidence)}
								</Badge>
							)}
							{state.result.needs_human_review && (
								<Badge variant="destructive">需人工复核</Badge>
							)}
						</h2>
						<p className="mt-1 text-sm text-muted-foreground">
							结果来自当前历史工单分类，处理上下文默认隐藏。
						</p>
					</div>
					<div className="mt-5 space-y-5">
						<ResultSection
							items={state.result.recommended_actions}
							title="推荐处理动作"
						/>
						<TextBlock title="最终行动计划" value={state.result.final_action_plan} />
						<TextBlock title="回单规范提醒" value={state.result.reply_standards} />
						{state.result.risk_notes?.length ? (
							<div>
								<h3 className="mb-2 text-sm font-medium">风险提醒</h3>
								<ul className="space-y-1 text-sm text-muted-foreground">
									{state.result.risk_notes.map((note) => (
										<li key={note}>{note}</li>
									))}
								</ul>
							</div>
						) : null}
					</div>
				</div>
			)}
		</div>
	);
}

function ResultSection({
	title,
	items,
}: {
	title: string;
	items?: Record<string, unknown>[];
}) {
	if (!items?.length) {
		return null;
	}

	return (
		<div>
			<h3 className="mb-2 text-sm font-medium">{title}</h3>
			<div className="space-y-3">
				{items.map((item, index) => (
					<div key={`${String(item.title ?? item.advice_title ?? index)}`} className="rounded-md border p-3">
						<div className="flex flex-wrap items-center gap-2">
							<p className="font-medium">
								{String(item.title ?? item.advice_title ?? `建议 ${index + 1}`)}
							</p>
							{item.match_level ? (
								<Badge variant="outline">{String(item.match_level)}</Badge>
							) : null}
						</div>
						{item.content || item.advice_content ? (
							<p className="mt-2 whitespace-pre-wrap text-sm leading-6 text-muted-foreground">
								{String(item.content ?? item.advice_content)}
							</p>
						) : null}
						{item.applicability_note ? (
							<p className="mt-2 text-xs text-muted-foreground">
								{String(item.applicability_note)}
							</p>
						) : null}
					</div>
				))}
			</div>
		</div>
	);
}

function TextBlock({
	title,
	value,
}: {
	title: string;
	value?: Record<string, unknown> | string | string[];
}) {
	if (!value) {
		return null;
	}

	const text =
		typeof value === "string"
			? value
			: Array.isArray(value)
				? value.join("\n")
				: JSON.stringify(value, null, 2);

	return (
		<div>
			<h3 className="mb-2 text-sm font-medium">{title}</h3>
			<pre className="max-h-72 overflow-auto rounded-md border bg-muted/40 p-3 text-xs leading-5 text-muted-foreground">
				{text}
			</pre>
		</div>
	);
}
