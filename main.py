import random
import time
import streamlit as st

# ----------------- 기본 설정 -----------------
st.set_page_config(page_title="두더지 잡기 (Streamlit)", page_icon="🐹", layout="centered")

GAME_SEC_DEFAULT = 10   # 고정: 10초
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

# 난이도 자동 증가
DIFFICULTY_STEPS = [(5, 500), (2, 300)]

# ----------------- 헤더 -----------------
st.title("🐹 두더지 잡기 (10초 버전)")
st.caption("10초 동안 최대한 많이 잡아보세요!")

# ----------------- 컨트롤 버튼 -----------------
cols_top = st.columns([1, 1])
with cols_top[0]:
    if st.button("게임 시작/재시작", type="primary"):
        st.session_state.running = True
        st.session_state.score = 0
        st.session_state.started_at = time.time()
        st.session_state.time_left = GAME_SEC_DEFAULT
        st.session_state.mole_pos = None
        st.session_state.last_spawn = 0.0
        st.session_state.interval_ms = INTERVAL_MS_DEFAULT

with cols_top[1]:
    if st.button("일시정지/종료"):
        st.session_state.running = False
        st.session_state.mole_pos = None

# ----------------- 남은시간/점수 갱신 -----------------
if st.session_state.running and st.session_state.started_at:
    elapsed = time.time() - st.session_state.started_at
    st.session_state.time_left = max(0, int(GAME_SEC_DEFAULT - elapsed))

    # 난이도 자동 증가
    for limit, new_ms in DIFFICULTY_STEPS:
        if st.session_state.time_left <= limit:
            st.session_state.interval_ms = new_ms

# ----------------- 정보 표시 -----------------
info_col1, info_col2 = st.columns(2)
with info_col1:
    st.metric(label="점수", value=st.session_state.score)
with info_col2:
    st.metric(label="남은 시간(초)", value=st.session_state.time_left)

progress = st.progress(0)
pct = int(100 * (GAME_SEC_DEFAULT - st.session_state.time_left) / GAME_SEC_DEFAULT) if st.session_state.running else 0
progress.progress(min(max(pct, 0), 100))

st.divider()

# ----------------- 두더지 스폰 -----------------
now = time.time()
should_spawn = False
if st.session_state.running and st.session_state.time_left > 0:
    if (now - st.session_state.last_spawn) * 1000 >= st.session_state.interval_ms:
        should_spawn = True

if should_spawn:
    r, c = random.randint(0, 2), random.randint(0, 2)
    st.session_state.mole_pos = (r, c)
    st.session_state.last_spawn = now

# ----------------- 3x3 버튼 보드 -----------------
clicked_coords = None
for r in range(3):
    cols = st.columns(3, gap="small")
    for c in range(3):
        is_mole = (st.session_state.mole_pos == (r, c))
        label = "두더지!" if is_mole else " "
        clicked = cols[c].button(label=label, key=f"cell-{r}-{c}", use_container_width=True)
        if clicked and st.session_state.running and st.session_state.time_left > 0:
            clicked_coords = (r, c)

# ----------------- 클릭 처리 -----------------
if clicked_coords is not None:
    if st.session_state.mole_pos == clicked_coords:
        st.session_state.score += 1
        st.session_state.mole_pos = None

# ----------------- 게임 종료 -----------------
if st.session_state.running and st.session_state.time_left <= 0:
    st.session_state.running = False
    st.session_state.mole_pos = None
    st.success(f"게임 끝! 최종 점수: {st.session_state.score}")

# ----------------- 자동 새로고침 -----------------
if st.session_state.running and st.session_state.time_left > 0:
    tick_ms = min(250, max(80, st.session_state.interval_ms // 3))
    st.experimental_rerun() if False else st.autorefresh(interval=tick_ms, key="ticker")
