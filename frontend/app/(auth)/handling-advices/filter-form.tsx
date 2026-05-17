"use client";

import { useState } from "react";
import { RotateCcwIcon, SearchIcon } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

const ALL_VALUE = "";

export type AdviceFilterOption = {
	code: string;
	name: string;
};

export type AdviceFilterValues = {
	query: string;
	status: string;
	primary_leaf_code: string;
	product_tag_code: string;
	request_tag_code: string;
};

type AdviceFilterFormProps = {
	filters: AdviceFilterValues;
	categoryOptions: AdviceFilterOption[];
	productOptions: AdviceFilterOption[];
	requestOptions: AdviceFilterOption[];
};

export function AdviceFilterForm({
	filters,
	categoryOptions,
	productOptions,
	requestOptions,
}: AdviceFilterFormProps) {
	const [query, setQuery] = useState(filters.query);
	const [status, setStatus] = useState(filters.status || "active");
	const [primaryLeafCode, setPrimaryLeafCode] = useState(
		filters.primary_leaf_code || ALL_VALUE
	);
	const [productTagCode, setProductTagCode] = useState(
		filters.product_tag_code || ALL_VALUE
	);
	const [requestTagCode, setRequestTagCode] = useState(
		filters.request_tag_code || ALL_VALUE
	);

	return (
		<form
			action="/handling-advices"
			className="grid gap-3 rounded-lg border bg-card p-4 text-card-foreground shadow-xs lg:grid-cols-[minmax(180px,1fr)_repeat(4,minmax(150px,180px))_auto]"
			method="get"
		>
			<div className="relative">
				<SearchIcon className="pointer-events-none absolute top-1/2 left-2.5 size-4 -translate-y-1/2 text-muted-foreground" />
				<Input
					aria-label="搜索建议标题、内容或适用条件"
					className="pl-8"
					name="query"
					onChange={(event) => setQuery(event.target.value)}
					placeholder="搜索建议"
					value={query}
				/>
			</div>

			<select
				aria-label="启用状态"
				className="h-9 w-full rounded-md border border-input bg-transparent px-2.5 py-1 text-sm shadow-xs outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50 dark:bg-input/30"
				name="status"
				onChange={(event) => setStatus(event.target.value)}
				value={status}
			>
				<option value="active">启用</option>
				<option value="inactive">停用</option>
				<option value={ALL_VALUE}>全部状态</option>
			</select>

			<FilterSelect
				name="primary_leaf_code"
				options={categoryOptions}
				placeholder="分类"
				value={primaryLeafCode}
				onValueChange={setPrimaryLeafCode}
			/>
			<FilterSelect
				name="product_tag_code"
				options={productOptions}
				placeholder="产品"
				value={productTagCode}
				onValueChange={setProductTagCode}
			/>
			<FilterSelect
				name="request_tag_code"
				options={requestOptions}
				placeholder="诉求"
				value={requestTagCode}
				onValueChange={setRequestTagCode}
			/>

			<div className="flex gap-2">
				<Button className="flex-1 lg:flex-none" type="submit">
					筛选
				</Button>
				<Button asChild size="icon" type="button" variant="outline">
					<a aria-label="重置筛选" href="/handling-advices">
						<RotateCcwIcon />
					</a>
				</Button>
			</div>
		</form>
	);
}

function FilterSelect({
	name,
	options,
	placeholder,
	value,
	onValueChange,
}: {
	name: string;
	options: AdviceFilterOption[];
	placeholder: string;
	value: string;
	onValueChange: (value: string) => void;
}) {
	return (
		<select
			aria-label={placeholder}
			className="h-9 w-full rounded-md border border-input bg-transparent px-2.5 py-1 text-sm shadow-xs outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50 dark:bg-input/30"
			name={name}
			onChange={(event) => onValueChange(event.target.value)}
			value={value}
		>
			<option value={ALL_VALUE}>全部{placeholder}</option>
			{options.map((option) => (
				<option key={option.code} value={option.code}>
					{option.name}
				</option>
			))}
		</select>
	);
}
