import { FolderTreeIcon, TagsIcon } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import {
	Card,
	CardContent,
	CardHeader,
	CardTitle,
} from "@/components/ui/card";
import { DataNotice, SystemPageHeader } from "@/app/(auth)/system/_components/system-layout";
import { backendFetch } from "@/app/(auth)/system/_lib/api";

type TaxonomyResponse = {
	status: string;
	data?: unknown;
};

const tagGroups = [
	{ key: "product", label: "产品标签" },
	{ key: "request", label: "诉求标签" },
	{ key: "emotion", label: "情绪标签" },
	{ key: "risk", label: "风险标签" },
] as const;

export default async function TaxonomyPage() {
	const [categories, ...tags] = await Promise.all([
		backendFetch<TaxonomyResponse>("/taxonomy/categories"),
		...tagGroups.map((group) =>
			backendFetch<TaxonomyResponse>(`/taxonomy/tags/${group.key}`)
		),
	]);

	const categoryItems = categories.ok ? flattenTaxonomy(categories.data.data) : [];

	return (
		<main className="flex flex-col gap-4">
			<SystemPageHeader
				title="分类标签"
				description="数据来自 backend_api/routes/taxonomy.py，用于核对分类树和各类标签 JSON。"
			/>

			{!categories.ok && (
				<DataNotice
					title="分类树读取失败"
					description={categories.error}
					variant="error"
				/>
			)}

			<section className="grid gap-4 xl:grid-cols-[1.1fr_0.9fr]">
				<Card>
					<CardHeader>
						<div className="flex items-center justify-between gap-3">
							<CardTitle className="flex items-center gap-2">
								<FolderTreeIcon className="size-4" />
								分类树
							</CardTitle>
							<Badge variant="outline">{categoryItems.length} 条节点</Badge>
						</div>
					</CardHeader>
					<CardContent>
						<div className="max-h-[640px] space-y-2 overflow-auto pr-2">
							{categoryItems.slice(0, 160).map((item, index) => (
								<div
									className="rounded-md border bg-muted/30 p-3 text-sm"
									key={`${item.code}-${index}`}
								>
									<div className="flex items-center justify-between gap-3">
										<span className="font-medium">{item.name}</span>
										<Badge variant="outline">{item.code || "no-code"}</Badge>
									</div>
									<p className="mt-1 text-xs text-muted-foreground">
										层级 {item.depth + 1}
									</p>
								</div>
							))}
							{categoryItems.length === 0 && (
								<EmptyBlock text="暂无分类树数据" />
							)}
						</div>
					</CardContent>
				</Card>

				<div className="grid gap-4">
					{tagGroups.map((group, index) => {
						const result = tags[index];
						const items = result?.ok ? flattenTaxonomy(result.data.data) : [];

						return (
							<Card key={group.key} size="sm">
								<CardHeader>
									<div className="flex items-center justify-between gap-3">
										<CardTitle className="flex items-center gap-2">
											<TagsIcon className="size-4" />
											{group.label}
										</CardTitle>
										<Badge variant="outline">{items.length} 条</Badge>
									</div>
								</CardHeader>
								<CardContent>
									{!result?.ok ? (
										<DataNotice
											title={`${group.label}读取失败`}
											description={result?.error ?? "接口未返回数据"}
											variant="error"
										/>
									) : (
										<div className="flex flex-wrap gap-2">
											{items.slice(0, 80).map((item, itemIndex) => (
												<Badge
													key={`${group.key}-${item.code}-${itemIndex}`}
													variant="secondary"
												>
													{item.name}
												</Badge>
											))}
											{items.length === 0 && <EmptyBlock text="暂无标签数据" />}
										</div>
									)}
								</CardContent>
							</Card>
						);
					})}
				</div>
			</section>
		</main>
	);
}

function flattenTaxonomy(
	value: unknown,
	depth = 0
): Array<{ code: string; name: string; depth: number }> {
	if (Array.isArray(value)) {
		return value.flatMap((item) => flattenTaxonomy(item, depth));
	}
	if (!value || typeof value !== "object") {
		return [];
	}

	const record = value as Record<string, unknown>;
	const name = String(
		record.name ??
			record.label ??
			record.title ??
			record.tag_name ??
			record.primary_leaf_name ??
			"未命名"
	);
	const code = String(
		record.code ??
			record.value ??
			record.id ??
			record.tag_code ??
			record.primary_leaf_code ??
			""
	);
	const children = [
		record.children,
		record.items,
		record.tags,
		record.options,
		record.sub_categories,
	].flatMap((child) => flattenTaxonomy(child, depth + 1));

	return [{ code, name, depth }, ...children];
}

function EmptyBlock({ text }: { text: string }) {
	return (
		<div className="w-full rounded-md border border-dashed p-6 text-center text-sm text-muted-foreground">
			{text}
		</div>
	);
}
