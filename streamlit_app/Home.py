from __future__ import annotations

from pathlib import Path

import streamlit as st

from streamlit_app.app_services import (
    build_batch_result_rows,
    fetch_dashboard_snapshot,
)


st.set_page_config(page_title='VOC Agent Console', page_icon='📊', layout='wide')

st.title('VOC Agent Console')
st.caption('批量执行、结果查看、数据浏览和统计刷新统一放在这里。')

snapshot = fetch_dashboard_snapshot()
metric_columns = st.columns(4)
metric_columns[0].metric('待处理工单', snapshot['pending_tickets'])
metric_columns[1].metric('已处理工单', snapshot['processed_tickets'])
metric_columns[2].metric('分类结果行', snapshot['category_results'])
metric_columns[3].metric('标签结果行', snapshot['tag_results'])

metric_columns = st.columns(4)
metric_columns[0].metric('关键词结果行', snapshot['keyword_results'])
metric_columns[1].metric('命中明细行', snapshot['match_details'])
metric_columns[2].metric('分类统计行', snapshot['category_stats'])
metric_columns[3].metric('标签统计行', snapshot['tag_stats'])

st.subheader('页面说明')
st.markdown(
    '\n'.join(
        [
            '- `Batch Run`: 设定批次数量并执行验证落库。',
            '- `Single Ticket Run`: 执行单个工单，并流式观察上下文、Prompt、模型返回和落库结果。',
            '- `Data Browser`: 直接浏览待处理工单、结果表和统计表。',
            '- `Stats Center`: 手动刷新统计，并查看五张统计表的当前结果。',
        ]
    )
)

st.subheader('最近批次')
latest_summary = st.session_state.get('latest_batch_summary')
if not latest_summary:
    st.info('当前会话还没有执行过批次。先去 `Batch Run` 页面执行一次。')
else:
    latest_rows = build_batch_result_rows(latest_summary)

    top_columns = st.columns(5)
    top_columns[0].metric('样本数', latest_summary.get('sample_size', 0))
    top_columns[1].metric('成功', latest_summary.get('success_count', 0))
    top_columns[2].metric('失败', latest_summary.get('failure_count', 0))
    top_columns[3].metric('成功率', f"{latest_summary.get('success_rate', 0.0):.0%}")
    top_columns[4].metric('工单数', len(latest_summary.get('results', [])))

    st.caption(f"最近执行时间: `{latest_summary.get('timestamp', '-')}`")
    st.dataframe(latest_rows, use_container_width=True, hide_index=True)
