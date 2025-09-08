import streamlit as st
import altair as alt
import pandas as pd
import time
from translations import translations
from core import (
    validate_input,
    generate_random_phrase,
    reproduce,
    select_best
)


if 'lang' not in st.session_state:
    st.session_state.lang = 'pt'

with st.sidebar:
    selected_lang_name = st.selectbox(
        label="Idioma / Language",
        options=[
            '🇧🇷 Português',
            '🇺🇸 English'
        ],
        index=0 if st.session_state.lang == 'pt' else 1
    )
    st.session_state.lang = 'pt' if selected_lang_name.startswith('🇧🇷') else 'en'

T = translations[st.session_state.lang]
st.markdown(
    """
    <style>
        body, .main, .block-container {
            background-color: #1a1a1a !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.set_page_config(layout="wide", page_title=T['page_title'])
st.title(T['main_title'])
st.markdown(T['description'])

with st.sidebar:
    st.header(T['sidebar_header'])

    target_phrase_input = st.text_input(
        T['target_phrase_label'],
        "hello world" if st.session_state.lang == 'en' else "ola mundo",
        help=T['target_phrase_help']
    ).lower()

    mutation_rate_input = st.slider(
        T['mutation_rate_label'],
        min_value=0.01,
        max_value=1.0,
        value=0.05,
        step=0.01,
        help=T['mutation_rate_help']
    )

    population_size_input = st.number_input(
        T['population_size_label'],
        min_value=10,
        max_value=1000,
        value=100,
        step=10,
        help=T['population_size_help']
    )

    col1, col2 = st.columns(2)
    start_button = col1.button(
        T['start_button'],
        type="primary",
        use_container_width=True
    )
    stop_button = col2.button(T['stop_button'], use_container_width=True)

if 'running' not in st.session_state:
    st.session_state.running = False
if 'best_candidate' not in st.session_state:
    st.session_state.best_candidate = ""
if 'generation' not in st.session_state:
    st.session_state.generation = 0
if 'history' not in st.session_state:
    st.session_state.history = []
if 'accuracy_history' not in st.session_state:
    st.session_state.accuracy_history = []

if start_button:
    if not target_phrase_input:
        st.sidebar.error(T['empty_target_error'])
    elif not validate_input(target_phrase_input):
        st.sidebar.error(T['invalid_target_error'])
    else:
        st.session_state.running = True
        st.session_state.target_phrase = target_phrase_input
        st.session_state.best_candidate = generate_random_phrase(
            len(target_phrase_input)
        )
        st.session_state.generation = 0
        st.session_state.mutation_rate = mutation_rate_input
        st.session_state.population_size = population_size_input
    st.session_state.history = []
    st.session_state.accuracy_history = []
    st.rerun()

if stop_button:
    st.session_state.running = False
    st.rerun()

if st.session_state.running:
    st.header(T['simulation_progress_header'])
    metrics_placeholder = st.empty()
    chart_placeholder = st.empty()
    progress_placeholder = st.empty()
    output_placeholder = st.empty()
    history_placeholder = st.empty()

    target_len = len(st.session_state.target_phrase)

    while st.session_state.running:
        if st.session_state.best_candidate == st.session_state.target_phrase:
            st.session_state.running = False
            break

        st.session_state.generation += 1
        population = reproduce(
            st.session_state.best_candidate,
            st.session_state.population_size,
            st.session_state.mutation_rate
        )
        st.session_state.best_candidate, best_score = select_best(
            population,
            st.session_state.target_phrase
        )

        highlighted_candidate = ""
        for i, char in enumerate(st.session_state.best_candidate):
            if char == st.session_state.target_phrase[i]:
                highlighted_candidate += char
            else:
                highlighted_candidate += f'<span style="color: #dc3545;">{char}</span>'

        history_entry = "<div style='background-color: #23272b; padding: 8px; border-radius: 4px;'>" + \
            T['history_entry'].format(
                generation=st.session_state.generation,
                candidate=highlighted_candidate
            ) + "</div>"
        st.session_state.history.append(history_entry)
        if len(st.session_state.history) > 15:
            st.session_state.history.pop(0)

        accuracy = (best_score / target_len) * 100
        st.session_state.accuracy_history.append(accuracy)
        if len(st.session_state.accuracy_history) > 100:
            st.session_state.accuracy_history.pop(0)

        with metrics_placeholder.container():
            col1, col2, col3 = st.columns(3)
            col1.metric(
                T['generation_metric'],
                f"{st.session_state.generation}"
            )
            col2.metric(
                T['score_metric'],
                f"{best_score} / {target_len}"
            )
            col3.metric(
                T['accuracy_metric'],
                f"{accuracy:.2f}%"
            )

        with chart_placeholder.container():
            df_chart = pd.DataFrame({
                'Geração': list(range(1, len(st.session_state.accuracy_history)+1)),
                'Precisão (%)': st.session_state.accuracy_history
            })
            chart = alt.Chart(df_chart).mark_line().encode(
                x=alt.X('Geração', title='Geração'),
                y=alt.Y('Precisão (%)', title='Precisão (%)')
            ).properties(width='container', height=250)
            st.altair_chart(chart, use_container_width=True)

        progress_bar_text = T['progress_bar_text'].format(accuracy=accuracy)
        progress_placeholder.progress(int(accuracy), text=progress_bar_text)

        styled_output = ""
        for i, char in enumerate(st.session_state.best_candidate):
            if char == st.session_state.target_phrase[i]:
                styled_output += f'<span style="color: #28a745; font-weight: bold;">{char}</span>'
            else:
                styled_output += f'<span style="color: #dc3545;">{char}</span>'

        output_placeholder.markdown(
        f"""<div style="font-family: 'Courier New', monospace; font-size: 24px; letter-spacing: 2px; border: 1px solid #444; padding: 15px; border-radius: 5px; background-color: #1a1a1a;">
    {styled_output}</div>""",
        unsafe_allow_html=True
    )

        with history_placeholder.container():
            st.markdown("---")
            st.subheader(T['history_header'])
            for entry in reversed(st.session_state.history):
                st.markdown(entry, unsafe_allow_html=True)

        time.sleep(0.01)

    if not st.session_state.running and st.session_state.best_candidate:
        if st.session_state.best_candidate == st.session_state.target_phrase:
            st.success(T['success_message'].format(
                generation=st.session_state.generation)
            )
        else:
            st.warning(T['stop_message'])
else:
    st.info(T['info_message'])
