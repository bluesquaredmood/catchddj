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
    st.metric(label="점수", value=st.session_state.score)
with info_col2:
    st.metric(label="남은 시간(초)", value=st.session_state.time_left)

progress = st.progress(0)
if game_sec > 0:
    pct = int(100 * (game_sec - st.session_state.time_left) / game_sec) if st.session_state.running else 0
    progress.progress(min(max(pct, 0), 100))

st.divider()

# ----------------- 두더지 스폰(등장 주기 제어) -----------------
now = time.time()
should_spawn = False
if st.session_state.running and st.session_state.time_left > 0:
    if (now - st.session_state.last_spawn) * 1000 >= st.session_state.interval_ms:
        should_spawn = True

if should_spawn:
    # 이전 두더지 지우고 새 위치
    r = random.randint(0, 2)
    c = random.randint(0, 2)
    st.session_state.mole_pos = (r, c)
    st.session_state.last_spawn = now

# ----------------- 3x3 버튼 보드 -----------------
clicked_coords = None
for r in range(3):
    cols = st.columns(3, gap="small")
    for c in range(3):
        is_mole = (st.session_state.mole_pos == (r, c))
        label = "두더지!" if is_mole else " "
        # 버튼 스타일 약간 키우기
        clicked = cols[c].button(
            label=label,
            key=f"cell-{r}-{c}",
            use_container_width=True
        )
        if clicked and st.session_state.running and st.session_state.time_left > 0:
            clicked_coords = (r, c)

# ----------------- 클릭 처리 -----------------
if clicked_coords is not None:
    if st.session_state.mole_pos == clicked_coords:
        st.session_state.score += 1
        st.session_state.mole_pos = None  # 맞추면 숨김
    elif show_feedback:
        # 피드백: 클릭 시 살짝 흔들기/리런만으로 충분(별도 색상은 버튼 재랜더링 한계)
        pass

# ----------------- 게임 종료 처리 -----------------
if st.session_state.running and st.session_state.time_left <= 0:
    st.session_state.running = False
    st.session_state.mole_pos = None
    st.success(f"게임 끝! 최종 점수: {st.session_state.score}")

# ----------------- 자동 새로고침(게임 중일 때만) -----------------
# Streamlit은 이벤트 루프가 없으므로 주기적으로 전체 스크립트를 재실행해 상태 업데이트
if st.session_state.running and st.session_state.time_left > 0:
    # UI 갱신 주기: 두더지 등장 주기보다 짧게(부드러운 화면)
    tick_ms = min(250, max(80, st.session_state.interval_ms // 3))
    st.experimental_rerun() if False else st.autorefresh(interval=tick_ms, key="ticker")
