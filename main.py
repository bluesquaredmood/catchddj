import random
import time
import streamlit as st

# ----------------- 기본 설정 -----------------
st.set_page_config(page_title="두더지 잡기 (Streamlit)", page_icon="🐹", layout="centered")

GAME_SEC_DEFAULT = 30
INTERVAL_MS_DEFAULT = 800  # 두더지 등장 주기(ms)

# ----------------- 상태 초기화 -----------------
if "running" not in st.session_state:
    st.session_state.running = False
if "score" not in st.session_state:
    st.session_state.score = 0
if "time_left" not in st.session_state:
    st.session_state.time_left = GAME_SEC_DEFAULT
if "started_at" not in st.session_state:
    st.session_state.started_at = None
if "mole_pos" not in st.session_state:
    st.session_state.mole_pos = None  # (r, c)
if "last_spawn" not in st.session_state:
    st.session_state.last_spawn = 0.0
if "interval_ms" not in st.session_state:
    st.session_state.interval_ms = INTERVAL_MS_DEFAULT

# 난이도 자동 증가를 켜면 남은 시간에 따라 인터벌이 빨라짐
DIFFICULTY_STEPS = [(20, 650), (10, 450), (5, 300)]  # (남은시간<=x, interval_ms)

# ----------------- 헤더/설명 -----------------
st.title("🐹 두더지 잡기 (Whac-A-Mole)")
st.caption("버튼을 눌러 두더지를 잡아요! Streamlit 버전")

# 사이드바 설정
with st.sidebar:
    st.header("설정")
    game_sec = st.number_input("게임 시간(초)", min_value=10, max_value=120, step=5, value=GAME_SEC_DEFAULT)
    base_interval = st.number_input("초기 등장 주기(ms)", min_value=150, max_value=2000, step=50, value=INTERVAL_MS_DEFAULT)
    auto_difficulty = st.toggle("난이도 자동 증가", value=True)
    show_feedback = st.toggle("빗맞음 색상 피드백", value=True)

# ----------------- 컨트롤 버튼 -----------------
cols_top = st.columns([1, 1, 1])
with cols_top[0]:
    if st.button("게임 시작/재시작", type="primary"):
        st.session_state.running = True
        st.session_state.score = 0
        st.session_state.started_at = time.time()
        st.session_state.time_left = game_sec
        st.session_state.mole_pos = None
        st.session_state.last_spawn = 0.0
        st.session_state.interval_ms = base_interval

with cols_top[1]:
    if st.button("일시정지/종료"):
        st.session_state.running = False
        st.session_state.mole_pos = None

with cols_top[2]:
    st.write("")  # spacer

# ----------------- 남은시간/점수 갱신 -----------------
if st.session_state.running and st.session_state.started_at:
    elapsed = time.time() - st.session_state.started_at
    st.session_state.time_left = max(0, int(game_sec - elapsed))

    # 난이도 자동 증가 (남은 시간이 줄수록 빨라짐)
    if auto_difficulty:
        st.session_state.interval_ms = base_interval
        for limit, new_ms in DIFFICULTY_STEPS:
            if st.session_state.time_left <= limit:
                st.session_state.interval_ms = new_ms

# ----------------- 정보 표시 (점수/타이머/진행바) -----------------
info_col1, info_col2 = st.columns(2)
with info_col1:
    st.metric(label="점수", val
