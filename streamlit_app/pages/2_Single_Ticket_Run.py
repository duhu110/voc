from __future__ import annotations

import json

import streamlit as st

from streamlit_app.app_services import dumps_for_ui, stream_single_ticket_job


st.set_page_config(page_title='Single Ticket Run', page_icon='🔎', layout='wide')

st.title('Single Ticket Run')
st.caption('执行单个工单，按阶段流式展示上下文、Prompt、模型输出、标准化结果和落库摘要。')


def _render_event(event: dict) -> None:
    stage = event.get('stage', 'unknown')
    if stage == 'start':
        st.info(f"{event['message']} | 模型: `{event.get('model_name', '-')}`")
        return
    if stage == 'context_loaded':
        metric_columns = st.columns(3)
        metric_columns[0].metric('分类数量', event.get('category_count', 0))
        metric_columns[1].metric('标签数量', event.get('tag_count', 0))
        metric_columns[2].metric('ticket_id', event.get('ticket_id', '-'))
        with st.expander('工单上下文', expanded=True):
            st.json(event.get('ticket', {}), expanded=True)
        with st.expander('分类上下文', expanded=False):
            st.json(event.get('categories', []), expanded=False)
        with st.expander('标签上下文', expanded=False):
            st.json(event.get('tags', []), expanded=False)
        return
    if stage == 'prompt_built':
        st.metric('Prompt 长度', event.get('prompt_length', 0))
        with st.expander('完整 Prompt', expanded=True):
            st.code(event.get('prompt', ''), language='text')
        return
    if stage == 'llm_response':
        with st.expander('原始 LLM 返回', expanded=True):
            st.code(event.get('raw_text', ''), language='json')
        return
    if stage == 'result_parsed':
        with st.expander('原始解析数据', expanded=False):
            st.json(event.get('raw_data', {}), expanded=True)
        with st.expander('标准化结果', expanded=True):
            st.json(event.get('result', {}), expanded=True)
        return
    if stage == 'persisted':
        write_summary = event.get('write_summary', {})
        metric_columns = st.columns(4)
        metric_columns[0].metric('分类写入', write_summary.get('category_results', 0))
        metric_columns[1].metric('标签写入', write_summary.get('tag_results', 0))
        metric_columns[2].metric('关键词写入', write_summary.get('keyword_results', 0))
        metric_columns[3].metric('命中明细写入', write_summary.get('match_details', 0))
        with st.expander('最终结果 JSON', expanded=False):
            st.json(event.get('result', {}), expanded=True)
        return
    if stage == 'database_rows_loaded':
        database_rows = event.get('database_rows', {})
        tabs = st.tabs(['分类结果行', '标签结果行', '关键词结果行', '命中明细行'])
        with tabs[0]:
            st.dataframe(database_rows.get('category_results', []), use_container_width=True, hide_index=True)
        with tabs[1]:
            st.dataframe(database_rows.get('tag_results', []), use_container_width=True, hide_index=True)
        with tabs[2]:
            st.dataframe(database_rows.get('keyword_results', []), use_container_width=True, hide_index=True)
        with tabs[3]:
            st.dataframe(database_rows.get('match_details', []), use_container_width=True, hide_index=True)
        return
    st.json(event, expanded=True)


with st.form('single-ticket-run-form'):
    ticket_id = st.text_input('工单 ID', placeholder='留空则随机挑一条未处理工单')
    submitted = st.form_submit_button('执行单工单')

if submitted:
    event_log: list[dict] = []
    timeline = st.empty()
    raw_dump = st.empty()
    try:
        for event in stream_single_ticket_job(ticket_id):
            event_log.append(event)
            with timeline.container():
                st.subheader('执行时间线')
                for idx, item in enumerate(event_log, start=1):
                    with st.container(border=True):
                        st.markdown(f"**Step {idx}: {item.get('stage', 'unknown')}**")
                        _render_event(item)
            raw_dump.code(dumps_for_ui(event_log), language='json')
        st.session_state['latest_single_ticket_events'] = event_log
        st.success('单工单执行完成。')
    except Exception as exc:  # noqa: BLE001
        failure = {
            'stage': 'failed',
            'ticket_id': ticket_id.strip() if ticket_id else None,
            'error_type': exc.__class__.__name__,
            'error_message': str(exc),
        }
        event_log.append(failure)
        with timeline.container():
            st.subheader('执行时间线')
            for idx, item in enumerate(event_log, start=1):
                with st.container(border=True):
                    st.markdown(f"**Step {idx}: {item.get('stage', 'unknown')}**")
                    _render_event(item)
        raw_dump.code(dumps_for_ui(event_log), language='json')
        st.error(f"{failure['error_type']}: {failure['error_message']}")
else:
    latest = st.session_state.get('latest_single_ticket_events')
    if latest:
        st.info('展示当前会话最近一次单工单执行记录。')
        for idx, item in enumerate(latest, start=1):
            with st.container(border=True):
                st.markdown(f"**Step {idx}: {item.get('stage', 'unknown')}**")
                _render_event(item)
    else:
        st.info('输入工单 ID 可指定执行；留空则随机挑一条未处理工单。页面会按阶段持续展示可观察信息。')
