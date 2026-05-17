"use client";

import { useEffect, useMemo, useState, useTransition } from "react";
import {
	BookOpenTextIcon,
	CheckCircle2Icon,
	CircleDotIcon,
	Edit3Icon,
	FileTextIcon,
	ListChecksIcon,
	PlusIcon,
	RefreshCwIcon,
	SaveIcon,
	SearchIcon,
	XIcon,
} from "lucide-react";

import {
	createExpertPlaybook,
	getExpertPlaybook,
	listExpertPlaybooks,
	updateExpertPlaybook,
	type ExpertPlaybook,
	type ExpertPlaybookListItem,
	type ExpertPlaybookPayload,
	type PlaybookStatus,
	type ReviewStatus,
} from "@/app/(auth)/expert-playbooks/actions";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";

type FormState = {
	scenario_key: string;
	title: string;
	case_description: string;
	source_file: string;
	source_case_no: string;
	source_case_title: string;
	trigger_keywords: string;
	primary_leaf_code: string;
	primary_leaf_name: string;
	product_tag_code: string;
	product_tag_name: string;
	request_tag_code: string;
	request_tag_name: string;
	verify_steps: string;
	judgment_rules: string;
	execution_steps: string;
	callback_requirements: string;
	communication_tips: string;
	raw_case_text: string;
	review_status: ReviewStatus;
	priority: string;
	status: PlaybookStatus;
};

const emptyForm: FormState = {
	scenario_key: "",
	title: "",
	case_description: "",
	source_file: "manual",
	source_case_no: "",
	source_case_title: "",
	trigger_keywords: "",
	primary_leaf_code: "",
	primary_leaf_name: "",
	product_tag_code: "",
	product_tag_name: "",
	request_tag_code: "",
	request_tag_name: "",
	verify_steps: "",
	judgment_rules: "",
	execution_steps: "",
	callback_requirements: "",
	communication_tips: "",
	raw_case_text: "",
	review_status: "draft",
	priority: "100",
	status: "active",
};

const reviewStatusLabels: Record<string, string> = {
	draft: "草稿",
	reviewed: "已审核",
};

const statusLabels: Record<string, string> = {
	active: "启用",
	inactive: "停用",
};

export default function ExpertPlaybooksPage() {
	const [items, setItems] = useState<ExpertPlaybookListItem[]>([]);
	const [total, setTotal] = useState(0);
	const [query, setQuery] = useState("");
	const [status, setStatus] = useState("");
	const [reviewStatus, setReviewStatus] = useState("");
	const [leafCode, setLeafCode] = useState("");
	const [selected, setSelected] = useState<ExpertPlaybook | null>(null);
	const [form, setForm] = useState<FormState>(emptyForm);
	const [mode, setMode] = useState<"create" | "edit">("create");
	const [message, setMessage] = useState<string | null>(null);
	const [error, setError] = useState<string | null>(null);
	const [isPending, startTransition] = useTransition();

	const reviewedCount = useMemo(
		() => items.filter((item) => item.review_status === "reviewed").length,
		[items]
	);

	function refresh(nextSelectedId?: number) {
		setError(null);
		startTransition(async () => {
			try {
				const data = await listExpertPlaybooks({
					query,
					status,
					review_status: reviewStatus,
					primary_leaf_code: leafCode,
					page_size: 50,
				});
				setItems(data.items);
				setTotal(data.total);
				const id = nextSelectedId ?? selected?.id ?? data.items[0]?.id;
				if (id) {
					await selectPlaybook(id);
				} else {
					setSelected(null);
					setMode("create");
					setForm(emptyForm);
				}
			} catch (err) {
				setError(err instanceof Error ? err.message : "列表加载失败");
			}
		});
	}

	async function selectPlaybook(id: number) {
		const detail = await getExpertPlaybook(id);
		setSelected(detail);
		setMode("edit");
		setForm(playbookToForm(detail));
	}

	useEffect(() => {
		const timer = window.setTimeout(() => refresh(), 0);
		return () => window.clearTimeout(timer);
		// eslint-disable-next-line react-hooks/exhaustive-deps
	}, []);

	function runSearch() {
		refresh();
	}

	function startCreate() {
		setSelected(null);
		setMode("create");
		setForm(emptyForm);
		setMessage(null);
		setError(null);
	}

	function setField<K extends keyof FormState>(key: K, value: FormState[K]) {
		setForm((current) => ({ ...current, [key]: value }));
	}

	function savePlaybook() {
		setError(null);
		setMessage(null);

		let payload: ExpertPlaybookPayload;
		try {
			payload = formToPayload(form, mode);
		} catch (err) {
			setError(err instanceof Error ? err.message : "表单校验失败");
			return;
		}

		startTransition(async () => {
			try {
				const saved =
					mode === "create"
						? await createExpertPlaybook(payload)
						: await updateExpertPlaybook(selected?.id ?? 0, payload);
				setSelected(saved);
				setMode("edit");
				setForm(playbookToForm(saved));
				setMessage(mode === "create" ? "专家剧本已新增" : "专家剧本已保存");
				await refresh(saved.id);
			} catch (err) {
				setError(err instanceof Error ? err.message : "保存失败");
			}
		});
	}

	return (
		<main className="flex flex-col gap-4">
			<section className="flex flex-col gap-3 rounded-lg border bg-card p-4 text-card-foreground shadow-xs xl:flex-row xl:items-center xl:justify-between">
				<div className="min-w-0">
					<div className="flex items-center gap-2">
						<BookOpenTextIcon className="size-5 text-primary" />
						<h1 className="text-xl font-semibold tracking-normal">专家经验库</h1>
					</div>
					<p className="mt-1 text-sm text-muted-foreground">
						维护核实步骤、判断规则、执行动作、回访要求和沟通技巧。
					</p>
				</div>
				<div className="grid grid-cols-3 gap-2 text-sm sm:w-auto sm:min-w-80">
					<Metric label="当前列表" value={total} />
					<Metric label="本页已审核" value={reviewedCount} />
					<Metric
						label="本页启用"
						value={items.filter((item) => item.status === "active").length}
					/>
				</div>
			</section>

			<section className="grid gap-4 xl:grid-cols-[minmax(0,1.15fr)_minmax(420px,0.85fr)]">
				<div className="flex min-w-0 flex-col gap-4">
					<div className="rounded-lg border bg-card p-4 shadow-xs">
						<div className="grid gap-3 md:grid-cols-[minmax(220px,1fr)_140px_140px_minmax(160px,0.6fr)_auto]">
							<div className="relative">
								<SearchIcon className="pointer-events-none absolute top-2.5 left-2.5 size-4 text-muted-foreground" />
								<Input
									aria-label="搜索专家剧本"
									className="pl-8"
									onChange={(event) => setQuery(event.target.value)}
									onKeyDown={(event) => {
										if (event.key === "Enter") runSearch();
									}}
									placeholder="搜索标题、场景、案例"
									value={query}
								/>
							</div>
							<NativeSelect
								ariaLabel="审核状态"
								onChange={setReviewStatus}
								options={[
									["", "全部审核"],
									["draft", "草稿"],
									["reviewed", "已审核"],
								]}
								value={reviewStatus}
							/>
							<NativeSelect
								ariaLabel="启用状态"
								onChange={setStatus}
								options={[
									["", "全部状态"],
									["active", "启用"],
									["inactive", "停用"],
								]}
								value={status}
							/>
							<Input
								aria-label="叶子分类编码"
								onChange={(event) => setLeafCode(event.target.value)}
								onKeyDown={(event) => {
									if (event.key === "Enter") runSearch();
								}}
								placeholder="叶子分类编码"
								value={leafCode}
							/>
							<div className="flex gap-2">
								<Button
									aria-label="刷新"
									onClick={runSearch}
									size="icon"
									type="button"
									variant="outline"
								>
									<RefreshCwIcon className={cn(isPending && "animate-spin")} />
								</Button>
								<Button onClick={startCreate} type="button">
									<PlusIcon />
									新增
								</Button>
							</div>
						</div>
					</div>

					<div className="overflow-hidden rounded-lg border bg-card shadow-xs">
						<div className="grid grid-cols-[minmax(260px,1.5fr)_110px_110px_90px] border-b bg-muted/40 px-4 py-2 text-xs font-medium text-muted-foreground max-md:hidden">
							<span>剧本</span>
							<span>审核</span>
							<span>启用</span>
							<span className="text-right">优先级</span>
						</div>
						<div className="divide-y">
							{items.length === 0 ? (
								<div className="flex h-48 items-center justify-center text-sm text-muted-foreground">
									暂无专家剧本
								</div>
							) : (
								items.map((item) => (
									<button
										className={cn(
											"grid w-full gap-3 px-4 py-3 text-left transition-colors hover:bg-muted/50 md:grid-cols-[minmax(260px,1.5fr)_110px_110px_90px] md:items-center",
											selected?.id === item.id && "bg-muted"
										)}
										key={item.id}
										onClick={() => {
											setError(null);
											startTransition(async () => {
												try {
													await selectPlaybook(item.id);
												} catch (err) {
													setError(
														err instanceof Error
															? err.message
															: "详情加载失败"
													);
												}
											});
										}}
										type="button"
									>
										<div className="min-w-0">
											<div className="flex items-center gap-2">
												<span className="truncate text-sm font-medium">
													{item.title}
												</span>
												<span className="shrink-0 rounded-sm bg-secondary px-1.5 py-0.5 text-xs text-secondary-foreground">
													{item.scenario_key}
												</span>
											</div>
											<p className="mt-1 line-clamp-1 text-xs text-muted-foreground">
												{item.primary_leaf_name ||
													item.case_description ||
													"未填写分类或案例描述"}
											</p>
										</div>
										<StatusBadge value={item.review_status} kind="review" />
										<StatusBadge value={item.status} kind="status" />
										<span className="text-right text-sm tabular-nums text-muted-foreground max-md:text-left">
											{item.priority}
										</span>
									</button>
								))
							)}
						</div>
					</div>
				</div>

				<div className="min-w-0 rounded-lg border bg-card shadow-xs">
					<div className="flex items-start justify-between gap-3 border-b p-4">
						<div>
							<h2 className="flex items-center gap-2 text-base font-semibold">
								{mode === "create" ? <PlusIcon className="size-4" /> : <Edit3Icon className="size-4" />}
								{mode === "create" ? "新增专家剧本" : "编辑专家剧本"}
							</h2>
							<p className="mt-1 text-sm text-muted-foreground">
								{mode === "create"
									? "场景键、标题和维护步骤为必填核心信息。"
									: selected
										? `#${selected.id} · ${selected.scenario_key}`
										: "选择左侧剧本后编辑。"}
							</p>
						</div>
						{mode === "edit" && (
							<Button onClick={startCreate} size="sm" type="button" variant="outline">
								<XIcon />
								清空
							</Button>
						)}
					</div>

					<div className="max-h-[calc(100vh-16rem)] overflow-y-auto p-4">
						{message && (
							<div className="mb-4 rounded-md border border-chart-2/40 bg-chart-2/10 px-3 py-2 text-sm">
								{message}
							</div>
						)}
						{error && (
							<div className="mb-4 rounded-md border border-destructive/40 bg-destructive/10 px-3 py-2 text-sm text-destructive">
								{error}
							</div>
						)}

						<div className="grid gap-4">
							<div className="grid gap-3 sm:grid-cols-2">
								<Field label="场景键">
									<Input
										disabled={mode === "edit"}
										onChange={(event) =>
											setField("scenario_key", event.target.value)
										}
										placeholder="manual-network-refund"
										value={form.scenario_key}
									/>
								</Field>
								<Field label="标题">
									<Input
										onChange={(event) => setField("title", event.target.value)}
										placeholder="输入专家剧本标题"
										value={form.title}
									/>
								</Field>
							</div>

							<div className="grid gap-3 sm:grid-cols-3">
								<Field label="审核状态">
									<NativeSelect
										ariaLabel="编辑审核状态"
										onChange={(value) =>
											setField("review_status", value as ReviewStatus)
										}
										options={[
											["draft", "草稿"],
											["reviewed", "已审核"],
										]}
										value={form.review_status}
									/>
								</Field>
								<Field label="启用状态">
									<NativeSelect
										ariaLabel="编辑启用状态"
										onChange={(value) =>
											setField("status", value as PlaybookStatus)
										}
										options={[
											["active", "启用"],
											["inactive", "停用"],
										]}
										value={form.status}
									/>
								</Field>
								<Field label="优先级">
									<Input
										max={999}
										min={1}
										onChange={(event) =>
											setField("priority", event.target.value)
										}
										type="number"
										value={form.priority}
									/>
								</Field>
							</div>

							<Field label="案例描述">
								<Textarea
									onChange={(event) =>
										setField("case_description", event.target.value)
									}
									placeholder="说明适用场景、客户诉求或问题背景"
									value={form.case_description}
								/>
							</Field>

							<div className="grid gap-3 sm:grid-cols-2">
								<Field label="分类编码">
									<Input
										onChange={(event) =>
											setField("primary_leaf_code", event.target.value)
										}
										placeholder="primary_leaf_code"
										value={form.primary_leaf_code}
									/>
								</Field>
								<Field label="分类名称">
									<Input
										onChange={(event) =>
											setField("primary_leaf_name", event.target.value)
										}
										placeholder="primary_leaf_name"
										value={form.primary_leaf_name}
									/>
								</Field>
								<Field label="产品标签编码">
									<Input
										onChange={(event) =>
											setField("product_tag_code", event.target.value)
										}
										value={form.product_tag_code}
									/>
								</Field>
								<Field label="产品标签名称">
									<Input
										onChange={(event) =>
											setField("product_tag_name", event.target.value)
										}
										value={form.product_tag_name}
									/>
								</Field>
								<Field label="诉求标签编码">
									<Input
										onChange={(event) =>
											setField("request_tag_code", event.target.value)
										}
										value={form.request_tag_code}
									/>
								</Field>
								<Field label="诉求标签名称">
									<Input
										onChange={(event) =>
											setField("request_tag_name", event.target.value)
										}
										value={form.request_tag_name}
									/>
								</Field>
							</div>

							<Field label="触发关键词">
								<Textarea
									onChange={(event) =>
										setField("trigger_keywords", event.target.value)
									}
									placeholder="每行或逗号分隔一个关键词"
									value={form.trigger_keywords}
								/>
							</Field>

							<FormSection icon={<ListChecksIcon />} title="维护核实步骤">
								<MultiLineField
									onChange={(value) => setField("verify_steps", value)}
									value={form.verify_steps}
								/>
							</FormSection>
							<FormSection icon={<CircleDotIcon />} title="判断规则">
								<MultiLineField
									onChange={(value) => setField("judgment_rules", value)}
									value={form.judgment_rules}
								/>
							</FormSection>
							<FormSection icon={<CheckCircle2Icon />} title="执行动作">
								<MultiLineField
									onChange={(value) => setField("execution_steps", value)}
									value={form.execution_steps}
								/>
							</FormSection>
							<FormSection icon={<RefreshCwIcon />} title="回访要求">
								<MultiLineField
									onChange={(value) =>
										setField("callback_requirements", value)
									}
									value={form.callback_requirements}
								/>
							</FormSection>
							<FormSection icon={<FileTextIcon />} title="沟通技巧">
								<MultiLineField
									onChange={(value) => setField("communication_tips", value)}
									value={form.communication_tips}
								/>
							</FormSection>

							<Field label="原始案例文本">
								<Textarea
									className="min-h-28"
									onChange={(event) =>
										setField("raw_case_text", event.target.value)
									}
									value={form.raw_case_text}
								/>
							</Field>

							<div className="grid gap-3 sm:grid-cols-3">
								<Field label="来源文件">
									<Input
										disabled={mode === "edit"}
										onChange={(event) =>
											setField("source_file", event.target.value)
										}
										value={form.source_file}
									/>
								</Field>
								<Field label="来源案例号">
									<Input
										disabled={mode === "edit"}
										onChange={(event) =>
											setField("source_case_no", event.target.value)
										}
										type="number"
										value={form.source_case_no}
									/>
								</Field>
								<Field label="来源案例标题">
									<Input
										disabled={mode === "edit"}
										onChange={(event) =>
											setField("source_case_title", event.target.value)
										}
										value={form.source_case_title}
									/>
								</Field>
							</div>
						</div>
					</div>

					<div className="flex items-center justify-end gap-2 border-t p-4">
						<Button
							disabled={isPending}
							onClick={savePlaybook}
							type="button"
						>
							<SaveIcon />
							{mode === "create" ? "新增剧本" : "保存修改"}
						</Button>
					</div>
				</div>
			</section>
		</main>
	);
}

function Metric({ label, value }: { label: string; value: number }) {
	return (
		<div className="rounded-md border bg-background px-3 py-2">
			<div className="text-xs text-muted-foreground">{label}</div>
			<div className="mt-1 text-lg font-semibold tabular-nums">{value}</div>
		</div>
	);
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
	return (
		<label className="grid gap-1.5 text-sm">
			<span className="font-medium">{label}</span>
			{children}
		</label>
	);
}

function FormSection({
	title,
	icon,
	children,
}: {
	title: string;
	icon: React.ReactNode;
	children: React.ReactNode;
}) {
	return (
		<div className="grid gap-2 rounded-md border p-3">
			<div className="flex items-center gap-2 text-sm font-medium [&>svg]:size-4 [&>svg]:text-primary">
				{icon}
				{title}
			</div>
			{children}
		</div>
	);
}

function MultiLineField({
	value,
	onChange,
}: {
	value: string;
	onChange: (value: string) => void;
}) {
	return (
		<Textarea
			className="min-h-24"
			onChange={(event) => onChange(event.target.value)}
			placeholder="每行填写一条"
			value={value}
		/>
	);
}

function NativeSelect({
	ariaLabel,
	value,
	options,
	onChange,
}: {
	ariaLabel: string;
	value: string;
	options: [string, string][];
	onChange: (value: string) => void;
}) {
	return (
		<select
			aria-label={ariaLabel}
			className="h-9 w-full rounded-md border border-input bg-background px-2.5 text-sm shadow-xs outline-none transition-[color,box-shadow] focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
			onChange={(event) => onChange(event.target.value)}
			value={value}
		>
			{options.map(([optionValue, label]) => (
				<option key={optionValue || "all"} value={optionValue}>
					{label}
				</option>
			))}
		</select>
	);
}

function StatusBadge({ value, kind }: { value: string; kind: "review" | "status" }) {
	const label =
		kind === "review"
			? reviewStatusLabels[value] ?? value
			: statusLabels[value] ?? value;
	const active = value === "reviewed" || value === "active";

	return (
		<span
			className={cn(
				"inline-flex w-fit items-center rounded-sm px-2 py-1 text-xs font-medium",
				active
					? "bg-chart-2/15 text-foreground"
					: "bg-muted text-muted-foreground"
			)}
		>
			{label}
		</span>
	);
}

function playbookToForm(playbook: ExpertPlaybook): FormState {
	return {
		scenario_key: playbook.scenario_key ?? "",
		title: playbook.title ?? "",
		case_description: playbook.case_description ?? "",
		source_file: playbook.source_file ?? "manual",
		source_case_no: stringifyNullable(playbook.source_case_no),
		source_case_title: playbook.source_case_title ?? "",
		trigger_keywords: (playbook.trigger_keywords ?? []).join("\n"),
		primary_leaf_code: playbook.primary_leaf_code ?? "",
		primary_leaf_name: playbook.primary_leaf_name ?? "",
		product_tag_code: playbook.product_tag_code ?? "",
		product_tag_name: playbook.product_tag_name ?? "",
		request_tag_code: playbook.request_tag_code ?? "",
		request_tag_name: playbook.request_tag_name ?? "",
		verify_steps: (playbook.verify_steps ?? []).join("\n"),
		judgment_rules: (playbook.judgment_rules ?? []).join("\n"),
		execution_steps: (playbook.execution_steps ?? []).join("\n"),
		callback_requirements: (playbook.callback_requirements ?? []).join("\n"),
		communication_tips: (playbook.communication_tips ?? []).join("\n"),
		raw_case_text: playbook.raw_case_text ?? "",
		review_status:
			playbook.review_status === "reviewed" ? "reviewed" : "draft",
		priority: String(playbook.priority ?? 100),
		status: playbook.status === "inactive" ? "inactive" : "active",
	};
}

function formToPayload(form: FormState, mode: "create" | "edit"): ExpertPlaybookPayload {
	const priority = Number(form.priority);
	const sourceCaseNo = form.source_case_no ? Number(form.source_case_no) : null;

	if (mode === "create" && !form.scenario_key.trim()) {
		throw new Error("请填写场景键");
	}
	if (!form.title.trim()) {
		throw new Error("请填写标题");
	}
	if (!Number.isInteger(priority) || priority < 1 || priority > 999) {
		throw new Error("优先级必须是 1 到 999 之间的整数");
	}
	if (
		form.source_case_no &&
		(!Number.isInteger(sourceCaseNo) || Number.isNaN(sourceCaseNo))
	) {
		throw new Error("来源案例号必须是整数");
	}

	return {
		scenario_key: form.scenario_key.trim() || undefined,
		title: form.title.trim(),
		case_description: clean(form.case_description),
		source_file: clean(form.source_file) ?? "manual",
		source_case_no: sourceCaseNo,
		source_case_title: clean(form.source_case_title),
		trigger_keywords: splitTokens(form.trigger_keywords),
		primary_leaf_code: clean(form.primary_leaf_code),
		primary_leaf_name: clean(form.primary_leaf_name),
		product_tag_code: clean(form.product_tag_code),
		product_tag_name: clean(form.product_tag_name),
		request_tag_code: clean(form.request_tag_code),
		request_tag_name: clean(form.request_tag_name),
		verify_steps: splitLines(form.verify_steps),
		judgment_rules: splitLines(form.judgment_rules),
		execution_steps: splitLines(form.execution_steps),
		callback_requirements: splitLines(form.callback_requirements),
		communication_tips: splitLines(form.communication_tips),
		raw_case_text: clean(form.raw_case_text),
		review_status: form.review_status,
		priority,
		status: form.status,
	};
}

function splitLines(value: string) {
	return value
		.split(/\r?\n/)
		.map((item) => item.trim())
		.filter(Boolean);
}

function splitTokens(value: string) {
	return value
		.split(/[\n,，]/)
		.map((item) => item.trim())
		.filter(Boolean);
}

function clean(value: string) {
	const trimmed = value.trim();
	return trimmed ? trimmed : null;
}

function stringifyNullable(value?: number | null) {
	return value === null || value === undefined ? "" : String(value);
}
