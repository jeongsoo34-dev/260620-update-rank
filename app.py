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
            
            goal_diff = (elo_a - elo_b) / 250
            st.write(f"💡 **AI 분석:** {predict_a}가 약 {max(0, round(1.5 + goal_diff, 1))}골 내외를 기록할 것으로 예상됩니다.")

        st.divider()
        
        st.subheader("📝 실제 경기 결과 입력")
        with st.form(key="soccer_form", clear_on_submit=True):
            team_a = st.selectbox("홈 팀", list(st.session_state.soccer_data.keys()), key="ta")
            team_b = st.selectbox("원정 팀", list(st.session_state.soccer_data.keys()), key="tb")
            
            # 🌟 수정 및 보완 완료: 누락되었던 득점 입력 코드를 정상적으로 채워 넣었습니다.
            score_a = st.number_input(f"{team_a} 득점", min_value=0, step=1, key="sa")
            score_b = st.number_input(f"{team_b} 득점", min_value=0, step=1, key="sb")
            
            importance = st.select_slider("대회 중요도 (K-Factor)", options=[20, 30, 40, 60], value=30, 
                                        help="친선경기: 20, 일반A매치: 30, 월드컵예선: 40, 월드컵본선: 60")
            
            submit_soccer = st.form_submit_button("랭킹 반영하기")
            
            if submit_soccer:
                if team_a == team_b:
                    st.error("서로 다른 국가를 선택하세요.")
                else:
                    r_a = st.session_state.soccer_data[team_a]
                    r_b = st.session_state.soccer_data[team_b]
                    
                    actual = 1.0 if score_a > score_b else (0.5 if score_a == score_b else 0.0)
                    new_a, new_b = update_elo(r_a, r_b, actual, k=importance)
                    
                    st.session_state.soccer_data[team_a] = new_a
                    st.session_state.soccer_data[team_b] = new_b
                    
                    st.session_state.match_logs.append({
                        "종목": "축구",
                        "매치": f"{team_a} {score_a}:{score_b} {team_b}",
                        "Elo 변동": f"{team_a}({r_a}➔{new_a}) | {team_b}({r_b}➔{new_b})"
                    })
                    st.success("데이터가 성공적으로 업데이트되었습니다!")
                    st.rerun()

# --- 탭 2: UFC 체급별 랭킹 ---
with main_tab2:
    st.info("왼쪽 사이드바에서 대결하려는 UFC 체급을 선택하고 경기 결과를 등록해 주세요.")
    
    # 사이드바 연동을 위한 체급 선택
    ufc_class = st.sidebar.selectbox("UFC 체급 선택", list(st.session_state.ufc_data.keys()), key="ufc_sidebar_select")
    fighters = list(st.session_state.ufc_data[ufc_class].keys())
    
    with st.sidebar.form(key='ufc_match_form', clear_on_submit=True):
        f_a = st.selectbox("블루 코너", fighters, index=0, key="fa")
        f_b = st.selectbox("레드 코너", fighters, index=1 if len(fighters) > 1 else 0, key="fb")
        res = st.radio("경기 결과", [f"{f_a} 승리 (피니시)", f"{f_a} 판정승", f"{f_b} 판정승", f"{f_b} 승리 (피니시)"])
        submit_ufc = st.form_submit_button("체급 랭킹 즉시 반영")
        
    if submit_ufc:
        if f_a == f_b:
            st.sidebar.error("서로 다른 선수를 선택하세요.")
        else:
            k_factor = 50 if "피니시" in res else 32
            outcome_a = 1.0 if f_a in res else 0.0
            
            old_a = st.session_state.ufc_data[ufc_class][f_a]['elo']
            old_b = st.session_state.ufc_data[ufc_class][f_b]['elo']
            
            new_a, new_b = update_elo(old_a, old_b, outcome_a, k=k_factor)
            
            st.session_state.ufc_data[ufc_class][f_a]['elo'] = new_a
            st.session_state.ufc_data[ufc_class][f_b]['elo'] = new_b
            
            st.session_state.match_logs.append({
                "종목": f"UFC ({ufc_class})",
                "매치": f"{f_a} vs {f_b}",
                "Elo 변동": f"{f_a}({old_a}➔{new_a}) | {f_b}({old_b}➔{new_b})"
            })
            st.success("UFC 랭킹이 업데이트되었습니다.")
            st.rerun()

    # UFC 메인 화면 렌더링
    st.subheader(f"📊 {ufc_class} 실시간 순위")
    ufc_list = []
    for name, info in st.session_state.ufc_data[ufc_class].items():
        ufc_list.append({"선수명": name, "Elo 점수": info['elo'], "전적": info['record'], "상태": info['status']})
    df_ufc = pd.DataFrame(ufc_list).sort_values(by="Elo 점수", ascending=False).reset_index(drop=True)
    df_ufc.index += 1
    st.dataframe(df_ufc, use_container_width=True)
    
    # 전적 로그 통합 출력
    if st.session_state.match_logs:
        st.subheader("📜 최근 전체 매치 히스토리 (축구/UFC 통합)")
        st.dataframe(pd.DataFrame(st.session_state.match_logs).iloc[::-1], use_container_width=True)
