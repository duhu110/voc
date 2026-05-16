from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import altair as alt
import pandas as pd
import streamlit as st

from db import query_df
from queries import (
    ADVICE_BUCKET_COVERAGE_SQL,
    ADVICE_QUALITY_SAMPLE_SQL,
    ADVICE_SUMMARY_SCOPE_COVERAGE_SQL,
    ADVICE_TOTAL_SQL,
    ADVICE_UNCOVERED_HIGH_VALUE_SQL,
)


st.set_page_config(
    page_title="第二阶段建议构建",
    page_icon="VOC",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown(
    """
    <style>
    .block-container { padding-top: 1.5rem; }
    [data-testid="stMetricValue"] { font-size: 1.75rem; }
    [data-testid="stMetricLabel"] { color: #475569; }
    .section-note { color: #64748b; font-size: 0.92rem; margin-top: -0.35rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


def fmt_int(value: object) -> str:
    if pd.isna(value):
        return "-"
    return f"{int(value):,}"


def fmt_percent(value: object) -> str:
    if pd.isna(value):
        return "-"
    return f"{float(value):.2f}%"


def first_row(df: pd.DataFrame) -> pd.Series:
    if df.empty:
        return pd.Series(dtype="object")
    return df.iloc[0]


def metric_row(items: list[tuple[str, object, str | None]]) -> None:
    columns = st.columns(len(items))
    for column, (label, value, help_text) in zip(columns, items):
        column.metric(label, value, help=help_text)


def bar_chart(df: pd.DataFrame, x: str, y: str, tooltip: list[str], height: int = 360) -> None:
    if df.empty:
        st.info("暂无可展示数据。")
        return
    chart = (
        alt.Chart(df)
        .mark_bar(color="#0f766e")
        .encode(
            x=alt.X(x, sort="-y", title=None),
            y=alt.Y(y, title=None),
            tooltip=tooltip,
        )
        .properties(height=height)
    )
    st.altair_chart(chart, use_container_width=True)


def add_bucket_status(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    status_df = df.copy()

    def status(row: pd.Series) -> str:
        target = row.get("target_percent")
        covered = row.get("covered_percent")
        if pd.isna(target):
            return "暂不强求"
        if pd.isna(covered):
            return "无数据"
        if float(covered) >= float(target):
            return "达标"
        return "待补齐"

    status_df["判断标准"] = status_df.apply(status, axis=1)
    return status_df


def main() -> None:
    st.title("第二阶段：建议构建 AGENT")
    now = datetime.now(ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M:%S")
    st.caption(f"advice_builder_agent 运行结果统计。数据每 60 秒缓存刷新。更新时间：{now}")

    with st.sidebar:
        st.header("统计范围")
        st.write("第二阶段 advice_builder_agent")
        if st.button("刷新数据", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    try:
        total = first_row(query_df(ADVICE_TOTAL_SQL))
        coverage = first_row(query_df(ADVICE_SUMMARY_SCOPE_COVERAGE_SQL))
        metric_row(
            [
                ("活跃建议数", fmt_int(total.get("active_advice_rows")), "converger_handling_advice 中 status = active 的行数"),
                ("覆盖叶子分类", fmt_int(total.get("covered_leaf_count")), "已生成建议的 primary_leaf_code 去重数量"),
                ("覆盖场景数", fmt_int(total.get("covered_scope_count")), "叶子分类 + 产品标签 + 诉求标签的去重场景数"),
                ("历史摘要场景", fmt_int(coverage.get("total_summary_scopes")), "可用于生成建议的历史摘要场景"),
                ("场景覆盖率", fmt_percent(coverage.get("covered_percent")), "已生成处理建议的历史摘要场景占比"),
            ]
        )
        metric_row(
            [
                ("已覆盖场景", fmt_int(coverage.get("covered_scopes")), None),
                ("未覆盖场景", fmt_int(coverage.get("uncovered_scopes")), None),
                ("引用摘要样本", fmt_int(total.get("source_summary_count")), "active 建议累计 source_summary_count"),
                ("首次生成时间", str(total.get("first_created_at") or "-"), None),
                ("最近更新时间", str(total.get("latest_updated_at") or "-"), None),
            ]
        )

        tabs = st.tabs(["分层覆盖", "未覆盖高价值场景", "质量抽样"])

        with tabs[0]:
            st.subheader("按样本量分层覆盖")
            st.markdown(
                '<div class="section-note">>=200 场景应接近 100%，>=100 尽量 95%+，>=50 尽量 80%+，<20 暂时不强求。</div>',
                unsafe_allow_html=True,
            )
            bucket_df = add_bucket_status(query_df(ADVICE_BUCKET_COVERAGE_SQL))
            if not bucket_df.empty:
                chart = (
                    alt.Chart(bucket_df)
                    .mark_bar(color="#0f766e")
                    .encode(
                        x=alt.X("bucket:N", title=None, sort=[">=200", "100-199", "50-99", "20-49", "<20"]),
                        y=alt.Y("covered_percent:Q", title="覆盖率", scale=alt.Scale(domain=[0, 100])),
                        tooltip=["bucket", "scope_count", "covered_count", "covered_percent", "target_percent", "判断标准"],
                    )
                    .properties(height=320)
                )
                st.altair_chart(chart, use_container_width=True)
            st.dataframe(bucket_df, use_container_width=True, hide_index=True)

        with tabs[1]:
            st.subheader("还没覆盖的高价值场景")
            st.markdown(
                '<div class="section-note">按历史摘要样本数倒序，优先补跑 summary_count 高的场景；后台 failed_scopes 中失败场景也建议单独补跑。</div>',
                unsafe_allow_html=True,
            )
            uncovered_df = query_df(ADVICE_UNCOVERED_HIGH_VALUE_SQL)
            if not uncovered_df.empty:
                display_df = uncovered_df.head(20).copy()
                display_df["scope"] = (
                    display_df["primary_leaf_name"].fillna("")
                    + " / "
                    + display_df["product_tag_name"].fillna("未标产品")
                    + " / "
                    + display_df["request_tag_name"].fillna("未标诉求")
                )
                bar_chart(display_df, "scope:N", "summary_count:Q", ["scope", "summary_count"], height=420)
            st.dataframe(uncovered_df, use_container_width=True, hide_index=True)

        with tabs[2]:
            st.subheader("建议质量抽样")
            st.markdown(
                '<div class="section-note">优先查看样本量最高的建议文本，确认建议是否可直接支撑新工单处理。</div>',
                unsafe_allow_html=True,
            )
            st.dataframe(query_df(ADVICE_QUALITY_SAMPLE_SQL), use_container_width=True, hide_index=True)
    except Exception as exc:
        st.error("统计查询失败，请检查数据库连接和表结构。")
        st.exception(exc)


if __name__ == "__main__":
    main()
