from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import altair as alt
import pandas as pd
import streamlit as st

from db import query_df
from queries import (
    ADVICE_READINESS_SQL,
    CATEGORY_DISTRIBUTION_SQL,
    CONSISTENCY_SQL,
    MISSING_ADVICE_SQL,
    OVERALL_COVERAGE_SQL,
    RECENT_SAMPLES_SQL,
    RESULT_COVERAGE_SQL,
    SUMMARY_OUTLIERS_SQL,
    SUMMARY_QUALITY_SQL,
    TAG_COVERAGE_SQL,
    TAG_DISTRIBUTION_SQL,
    VERSION_DISTRIBUTION_SQL,
)


st.set_page_config(
    page_title="VOC 项目进度统计",
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


def bar_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    tooltip: list[str],
    height: int = 360,
) -> None:
    if df.empty:
        st.info("暂无可展示数据。")
        return
    chart = (
        alt.Chart(df)
        .mark_bar(color="#2563eb")
        .encode(
            x=alt.X(x, sort="-y", title=None),
            y=alt.Y(y, title=None),
            tooltip=tooltip,
        )
        .properties(height=height)
    )
    st.altair_chart(chart, use_container_width=True)


def render_overview() -> None:
    coverage = first_row(query_df(OVERALL_COVERAGE_SQL))
    result_coverage = first_row(query_df(RESULT_COVERAGE_SQL))

    processed_percent = coverage.get("processed_percent")
    result_distinct = result_coverage.get("result_distinct_tickets")
    summary_distinct = result_coverage.get("summary_distinct_tickets")
    total_tickets = coverage.get("total_tickets")

    result_percent = None
    summary_percent = None
    if total_tickets and not pd.isna(total_tickets):
        result_percent = float(result_distinct or 0) * 100 / float(total_tickets)
        summary_percent = float(summary_distinct or 0) * 100 / float(total_tickets)

    metric_row(
        [
            ("总工单数", fmt_int(total_tickets), "raw_complaint_tickets 总量"),
            ("已标记处理", fmt_int(coverage.get("marked_processed")), "converger_agent_status = true"),
            ("处理进度", fmt_percent(processed_percent), "已标记处理 / 总工单"),
            ("分类结果覆盖", fmt_percent(result_percent), "去重 ticket_id 后的分类结果覆盖率"),
            ("摘要覆盖", fmt_percent(summary_percent), "去重 source_ticket_id 后的摘要覆盖率"),
        ]
    )

    metric_row(
        [
            ("分类结果行", fmt_int(result_coverage.get("result_rows")), None),
            ("分类结果工单", fmt_int(result_distinct), None),
            ("摘要行", fmt_int(result_coverage.get("summary_rows")), None),
            ("摘要工单", fmt_int(summary_distinct), None),
            ("活跃处理建议", fmt_int(result_coverage.get("active_advice_rows")), None),
        ]
    )


def render_consistency() -> None:
    df = query_df(CONSISTENCY_SQL)
    problem_count = int(df["row_count"].sum()) if not df.empty else 0
    st.subheader("结果一致性")
    st.markdown('<div class="section-note">用于发现状态位、分类结果、摘要沉淀之间是否有断层。</div>', unsafe_allow_html=True)
    st.metric("待处理异常数", fmt_int(problem_count))
    bar_chart(df, "check_name:N", "row_count:Q", ["check_name", "row_count"], height=260)
    st.dataframe(df, use_container_width=True, hide_index=True)


def render_versions() -> None:
    df = query_df(VERSION_DISTRIBUTION_SQL)
    st.subheader("版本与模型分布")
    st.markdown('<div class="section-note">确认分类体系版本、AGENT 版本、模型和结果状态是否集中在预期版本。</div>', unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True, hide_index=True)


def render_categories() -> None:
    df = query_df(CATEGORY_DISTRIBUTION_SQL)
    st.subheader("分类结果分布")
    st.markdown('<div class="section-note">观察一级、二级和叶子分类是否过度集中，便于定位分类体系或提示词偏差。</div>', unsafe_allow_html=True)
    bar_df = df.head(30).copy()
    bar_df["category"] = bar_df["primary_leaf_name"].fillna(bar_df["primary_leaf_code"])
    bar_chart(bar_df, "category:N", "row_count:Q", ["category", "row_count", "percent_of_results"], height=420)
    st.dataframe(df, use_container_width=True, hide_index=True)


def render_tags() -> None:
    coverage = first_row(query_df(TAG_COVERAGE_SQL))
    result_rows = float(coverage.get("result_rows") or 0)

    def coverage_percent(column: str) -> str:
        if result_rows == 0:
            return "-"
        return fmt_percent(float(coverage.get(column) or 0) * 100 / result_rows)

    st.subheader("受控标签覆盖")
    metric_row(
        [
            ("诉求标签", coverage_percent("has_request_tag"), None),
            ("情绪标签", coverage_percent("has_emotion_tag"), None),
            ("风险标签", coverage_percent("has_risk_tag"), None),
            ("产品标签", coverage_percent("has_product_tag"), None),
            ("线路分类", coverage_percent("has_line_category"), None),
        ]
    )

    df = query_df(TAG_DISTRIBUTION_SQL)
    selected_group = st.segmented_control(
        "标签组",
        options=["诉求标签", "情绪标签", "风险标签", "产品标签"],
        default="诉求标签",
    )
    group_df = df[df["tag_group"] == selected_group].head(40)
    display_df = group_df.copy()
    display_df["tag_label"] = display_df["tag_name"].fillna("未打标")
    bar_chart(display_df, "tag_label:N", "row_count:Q", ["tag_code", "tag_name", "row_count"], height=360)
    st.dataframe(group_df, use_container_width=True, hide_index=True)


def render_summary_quality() -> None:
    quality = first_row(query_df(SUMMARY_QUALITY_SQL))
    st.subheader("摘要质量信号")
    metric_row(
        [
            ("摘要行数", fmt_int(quality.get("summary_rows")), None),
            ("空摘要", fmt_int(quality.get("empty_summary_rows")), None),
            ("最短长度", fmt_int(quality.get("min_summary_length")), None),
            ("中位长度", fmt_int(quality.get("p50_summary_length")), None),
            ("最长长度", fmt_int(quality.get("max_summary_length")), None),
        ]
    )
    length_df = pd.DataFrame(
        [
            {"quantile": "P25", "length": quality.get("p25_summary_length")},
            {"quantile": "P50", "length": quality.get("p50_summary_length")},
            {"quantile": "P75", "length": quality.get("p75_summary_length")},
        ]
    )
    bar_chart(length_df, "quantile:N", "length:Q", ["quantile", "length"], height=240)
    st.subheader("摘要异常样本")
    st.dataframe(query_df(SUMMARY_OUTLIERS_SQL), use_container_width=True, hide_index=True)


def render_advice() -> None:
    st.subheader("处理建议准备度")
    readiness = query_df(ADVICE_READINESS_SQL)
    st.markdown('<div class="section-note">按叶子分类、产品标签、诉求标签聚合，观察可用于新工单 AGENT 的建议沉淀范围。</div>', unsafe_allow_html=True)
    st.dataframe(readiness, use_container_width=True, hide_index=True)

    st.subheader("缺少处理建议的高频范围")
    missing = query_df(MISSING_ADVICE_SQL)
    st.dataframe(missing, use_container_width=True, hide_index=True)


def render_samples() -> None:
    st.subheader("近期人工复核样本")
    st.dataframe(query_df(RECENT_SAMPLES_SQL), use_container_width=True, hide_index=True)


def main() -> None:
    st.title("VOC 项目进度统计")
    now = datetime.now(ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M:%S")
    st.caption(f"当前页面：第一阶段分类 AGENT 运行结果统计。数据每 60 秒缓存刷新。更新时间：{now}")

    with st.sidebar:
        st.header("统计范围")
        st.write("第一阶段分类 AGENT")
        if st.button("刷新数据", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    try:
        render_overview()
        tabs = st.tabs(["一致性", "版本", "分类", "标签", "摘要", "处理建议", "样本"])
        with tabs[0]:
            render_consistency()
        with tabs[1]:
            render_versions()
        with tabs[2]:
            render_categories()
        with tabs[3]:
            render_tags()
        with tabs[4]:
            render_summary_quality()
        with tabs[5]:
            render_advice()
        with tabs[6]:
            render_samples()
    except Exception as exc:
        st.error("统计查询失败，请检查数据库连接和表结构。")
        st.exception(exc)


if __name__ == "__main__":
    main()
