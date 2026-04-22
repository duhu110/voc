from __future__ import annotations

import json

import streamlit as st

from streamlit_app.app_services import build_batch_result_rows, run_batch_job


st.set_page_config(page_title='Batch Run', page_icon='🚀', layout='wide')

st.title('Batch Run')
st.caption('执行未处理工单的批量验证落库。')

with st.form('batch-run-form'):
    sample_size = st.number_input('执行批次数量', min_value=1, max_value=200, value=20, step=1)
    submitted = st.form_submit_button('开始执行')

if submitted:
    with st.spinner('正在执行批量验证和落库，请等待...'):
        summary = run_batch_job(int(sample_size))
        st.session_state['latest_batch_summary'] = summary

    st.success('批量执行完成。')
    metric_columns = st.columns(4)
    metric_columns[0].metric('样本数', summary.get('sample_size', 0))
    metric_columns[1].metric('成功', summary.get('success_count', 0))
    metric_columns[2].metric('失败', summary.get('failure_count', 0))
    metric_columns[3].metric('成功率', f"{summary.get('success_rate', 0.0):.0%}")

    st.caption(f"执行时间: `{summary.get('timestamp', '-')}`")
    st.caption('本页面直接调用 `complaint_taxonomy_validator` 执行分析和落库，不会额外写 batch summary JSON 文件。')

    st.subheader('逐条执行结果')
    st.dataframe(build_batch_result_rows(summary), use_container_width=True, hide_index=True)

    st.subheader('失败分布')
    failures_by_stage = summary.get('failures_by_stage') or {}
    if failures_by_stage:
        st.json(failures_by_stage, expanded=True)
    else:
        st.write('无失败记录。')

    st.subheader('完整 summary')
    st.code(json.dumps(summary, ensure_ascii=False, indent=2), language='json')
else:
    st.info('设置批次数量后点击“开始执行”。页面会阻塞到本轮批次完成，然后展示每条工单的处理结果。')
