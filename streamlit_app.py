import streamlit as st
import time
from datetime import datetime
from db_manager import DatabaseManager
import engine

# 페이지 설정 (모바일 최적화)
st.set_page_config(page_title="ScoreLess Web", page_icon="📝", layout="centered")

# CSS로 모바일 카드 디자인 적용
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #3498DB; color: white; }
    .concept-card { padding: 20px; border-radius: 15px; background-color: white; border: 1px solid #E1E4E8;
      margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# DB 초기화 (캐시 처리하여 효율성 높임)
if 'db' not in st.session_state:
    st.session_state.db = DatabaseManager()
    st.session_state.user_id = st.session_state.db.get_user_id("WebUser")

db = st.session_state.db
user_id = st.session_state.user_id

# 메뉴 선택 (사이드바)
menu = st.sidebar.selectbox("메뉴", ["대시보드", "새 주제 등록"])

# --- 대시보드 화면 ---
if menu == "대시보드":
    st.title("🚀 학습 대시보드")
    concepts = db.get_all_concepts(user_id)

    if not concepts:
        st.info("공부할 주제를 먼저 등록해 주세요!")

    for cid, name, dom, score, sessions in concepts:
        with st.container():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.subheader(f"{name}")
                st.caption(f"분야: {dom} | 학습 횟수: {sessions}회")
            with col2:
                st.metric("CS 점수", f"{score}점")

            # 학습 시작 버튼 (Expandable로 학습/평가 창 열기)
            with st.expander(f"📖 '{name}' 학습하기"):
                # 타이머 시뮬레이션
                if st.button(f"학습 종료 및 평가하기", key=f"btn_{cid}"):
                    st.write("학습을 완료했습니다! 이해도를 선택하세요:")

                    # 평가 버튼들
                    cols = st.columns(3)
                    ratings = [
                        (0, "전혀 모름"), (1, "조금 암"), (2, "절반 이해"),
                        (3, "대체로 이해"), (4, "잘 이해"), (5, "완벽함")
                    ]
                    for i, (val, text) in enumerate(ratings):
                        if cols[i % 3].button(f"{text}", key=f"rate_{cid}_{val}"):
                            new_s = engine.calculate_cs(val, (sessions or 0) + 1, score)
                            db.upsert_cs(user_id, cid, new_s, engine.get_next_review(new_s))
                            st.success(f"점수 업데이트 완료: {new_s}점!")
                            time.sleep(1)
                            st.rerun()

# --- 주제 등록 화면 ---
elif menu == "새 주제 등록":
    st.title("➕ 새 주제 등록")
    with st.form("add_form"):
        new_name = st.text_input("개념 이름")
        new_dom = st.text_input("분야 (예: 파이썬)")
        submit = st.form_submit_button("등록하기")

        if submit and new_name:
            db.add_concept(user_id, new_name, new_dom or "일반")
            st.success(f"'{new_name}' 주제가 등록되었습니다!")
            time.sleep(1)
            st.rerun()
