import streamlit as st
import pandas as pd

# 1. 통합 데이터 초기화 (UFC + 축구)
if 'ufc_data' not in st.session_state:
    st.session_state.ufc_data = {
        '헤비급 (Heavyweight)': {
            '존 존스': {'elo': 1650, 'record': '27-1-0', 'status': '🏆 챔피언'},
            '톰 아스피날': {'elo': 1620, 'record': '14-3-0', 'status': '잠정 챔피언'},
            '시릴 간': {'elo': 1550, 'record': '12-2-0', 'status': '랭커 (#1)'}
        },
        '라이트헤비급 (Light Heavyweight)': {
            '알렉스 페레이라': {'elo': 1640, 'record': '10-2-0', 'status': '🏆 챔피언'},
            '이리 프로하즈카': {'elo': 1560, 'record': '30-4-1', 'status': '랭커 (#1)'}
        }
    }

if 'soccer_data' not in st.session_state:
    st.session_state.soccer_data = {
        '아르헨티나': 2150, '프랑스': 2115, '스페인': 2108, '잉글랜드': 2055, 
        '브라질': 2040, '벨기에': 1995, '네덜란드': 1980, '포르투갈': 1970,
        '대한민국': 1780, '일본': 1810, '호주': 1750, '이란': 1795
    }

if 'match_logs' not in st.session_state:
    st.session_state.match_logs = []

# --- 유틸리티 함수 ---
def get_expected_score(r_a, r_b):
    """팀 A의 기대 승률 계산"""
    return 1 / (1 + 10 ** ((r_b - r_a) / 400))

def update_elo(r_a, r_b, actual_score, k=30):
    expected = get_expected_score(r_a, r_b)
    new_r_a = r_a + k * (actual_score - expected)
    new_r_b = r_b + k * ((1 - actual_score) - (1 - expected))
    return round(new_r_a), round(new_r_b)

# --- UI 레이아웃 구성 ---
st.set_page_config(layout="wide", page_title="Sports Data Hub")
st.title("🏆 통합 스포츠 랭킹 및 예측 플랫폼")

# 상단 탭 구분
main_tab1, main_tab2 = st.tabs(["⚽ 국가별 축구 랭킹", "🥊 UFC 체급별 랭킹"])

# --- 탭 1: 국가 간 축구 랭킹 ---
with main_tab1:
    col_l, col_r = st.columns([1, 1])
    
    with col_l:
        st.subheader("📊 실시간 글로벌 축구 랭킹")
        df_soccer = pd.DataFrame(list(st.session_state.soccer_data.items()), columns=['국가', 'Elo Rating'])
        df_soccer = df_soccer.sort_values(by='Elo Rating', ascending=False).reset_index(drop=True)
        df_soccer.index += 1
        st.table(df_soccer)

        # 새로운 국가 추가 기능
        with st.expander("➕ 새로운 국가 추가"):
            new_country = st.text_input("국가 이름")
            if st.button("등록"):
                if new_country and new_country not in st.session_state.soccer_data:
                    st.session_state.soccer_data[new_country] = 1500
                    st.success(f"{new_country}가 등록되었습니다 (기본 1500점)")
                    st.rerun()

    with col_r:
        st.subheader("🔮 매치 결과 분석 및 예측")
        st.info("두 국가를 선택하면 수학적 기대 승률과 예상 스코어를 산출합니다.")
        
        predict_a = st.selectbox("팀 A (홈)", list(st.session_state.soccer_data.keys()), key="pa")
        predict_b = st.selectbox("팀 B (원정)", list(st.session_state.soccer_data.keys()), key="pb")
        
        if predict_a != predict_b:
            elo_a = st.session_state.soccer_data[predict_a]
            elo_b = st.session_state.soccer_data[predict_b]
            
            prob_a = get_expected_score(elo_a, elo_b)
            prob_b = 1 - prob_a
            
            c1, c2, c3 = st.columns(3)
            c1.metric(f"{predict_a} 승률", f"{prob_a*100:.1f}%")
            c2.metric("무승부 확률", f"{(1 - abs(prob_a - prob_b)) * 25:.1f}%")
            c3.metric(f"{predict_b} 승률", f"{prob_b*100:.1f}%")
            
            st.progress(prob_a)
            st.write(f"현재 전력 차이: **{abs(elo_a - elo_b)} Elo 포인트**")
            
            # 🌟 오타 수정 완료: el_b에서 elo_b로 변경되었습니다.
            goal_diff = (elo_a - elo_b) / 250
            st.write(f"💡 **AI 분석:** {predict_a}가 약 {max(0, round(1.5 + goal_diff, 1))}골 내외를 기록할 것으로 예상됩니다.")

        st.divider()
        
        st.subheader("📝 실제 경기 결과 입력")
        with st.form(key="soccer_form", clear_on_submit=True):
            team_a = st.selectbox("홈 팀", list(st.session_state.soccer_data.keys()), key="ta")
            team_b = st.selectbox("원정 팀", list(st.session_state.soccer_data.keys()), key="tb")
            score_a = st.number_input(f"{team_a} 득점", min_value=0, step=1, key="sa")
            score_b =
