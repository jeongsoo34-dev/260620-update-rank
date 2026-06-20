import streamlit as st
import pandas as pd

# 1. 초기 데이터 세팅 (세션 상태 초기화)
if 'rankings' not in st.session_state:
    # 예시를 위한 초기 국가와 Elo 점수 (기본 1500점)
    st.session_state.rankings = {
        '대한민국': 1500,
        '일본': 1500,
        '브라질': 1500,
        '프랑스': 1500,
        '아르헨티나': 1500
    }

if 'history' not in st.session_state:
    st.session_state.history = []

# 2. Elo 레이팅 계산 함수
def update_elo(rating_a, rating_b, outcome, k=32):
    """
    outcome: 1.0 (A 승리), 0.5 (무승부), 0 (B 승리)
    k: 가중치 (값이 클수록 한 경기로 인한 점수 변동이 큼)
    """
    # 기대 승률 계산
    expected_a = 1 / (1 + 10 ** ((rating_b - rating_a) / 400))
    expected_b = 1 / (1 + 10 ** ((rating_a - rating_b) / 400))
    
    # 새로운 점수 계산
    new_rating_a = rating_a + k * (outcome - expected_a)
    new_rating_b = rating_b + k * ((1 - outcome) - expected_b)
    
    return round(new_rating_a), round(new_rating_b)

# --- UI 레이아웃 ---
st.title("🏆 실시간 스포츠 랭킹 산정 시스템")
st.markdown("경기 결과를 입력하면 Elo 알고리즘에 의해 실시간으로 랭킹이 업데이트됩니다.")

sidebar = st.sidebar
sidebar.header("⚽ 경기 결과 입력")

# 경기 결과 입력 폼
with sidebar.form(key='match_form', clear_on_submit=True):
    team_a = st.selectbox("팀 A (홈/선수1)", list(st.session_state.rankings.keys()))
    team_b = st.selectbox("팀 B (원정/선수2)", list(st.session_state.rankings.keys()))
    
    result = st.radio("경기 결과", [f"{team_a} 승리", "무승부", f"{team_b} 승리"])
    
    submit_button = st.form_submit_button(label='결과 반영하기')

# 3. 결과 반영 로직
if submit_button:
    if team_a == team_b:
        st.sidebar.error("서로 다른 두 팀을 선택해주세요!")
    else:
        # 현재 점수 가져오기
        elo_a = st.session_state.rankings[team_a]
        elo_b = st.session_state.rankings[team_b]
        
        # 승패 변환
        if result == f"{team_a} 승리":
            outcome = 1.0
        elif result == "무승부":
            outcome = 0.5
        else:
            outcome = 0.0
            
        # Elo 계산
        new_a, new_b = update_elo(elo_a, elo_b, outcome)
        
        # 세션 상태 업데이트
        st.session_state.rankings[team_a] = new_a
        st.session_state.rankings[team_b] = new_b
        
        # 경기 기록 저장
        st.session_state.history.append({
            "팀 A": team_a,
            "팀 B": team_b,
            "결과": result,
            "점수 변동": f"{team_a}({elo_a}➔{new_a}) | {team_b}({elo_b}➔{new_b})"
        })
        st.success(f"🔥 경기 결과가 반영되었습니다: {result}!")

# --- 메인 화면 출력 ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📊 현재 실시간 랭킹")
    # 딕셔너리를 데이터프레임으로 변환 후 정렬
    df_rank = pd.DataFrame(list(st.session_state.rankings.items()), columns=['팀/선수', 'Elo 점수'])
    df_rank = df_rank.sort_values(by='Elo 점수', ascending=False).reset_index(drop=True)
    df_rank.index = df_rank.index + 1 # 순위를 1부터 시작하도록
    
    st.dataframe(df_rank, use_container_width=True)

with col2:
    st.subheader("📜 최근 경기 기록")
    if st.session_state.history:
        df_hist = pd.DataFrame(st.session_state.history)
        st.dataframe(df_hist.iloc[::-1], use_container_width=True) # 최신 순으로 정렬
    else:
        st.info("아직 입력된 경기 결과가 없습니다.")
