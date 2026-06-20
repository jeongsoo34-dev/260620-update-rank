import streamlit as st
import pandas as pd
import io

# --- 1. UFC 7대 체급 핵심 선수 대거 초기화 ---
# 초기 Elo는 1500점을 기준으로 현역 서열에 맞춰 소폭 보정해 두었습니다.
if 'ufc_data' not in st.session_state:
    st.session_state.ufc_data = {
        '헤비급 (Heavyweight)': {
            '존 존스': {'elo': 1650, 'record': '27-1-0', 'status': '🏆 챔피언'},
            '톰 아스피날': {'elo': 1630, 'record': '14-3-0', 'status': '잠정 챔피언'},
            '시릴 간': {'elo': 1550, 'record': '12-2-0', 'status': '랭커 (#1)'},
            '세르게이 파블로비치': {'elo': 1510, 'record': '18-2-0', 'status': '랭커 (#2)'},
            '커티스 블레이즈': {'elo': 1490, 'record': '18-5-0', 'status': '랭커 (#3)'}
        },
        '라이트헤비급 (Light Heavyweight)': {
            '알렉스 페레이라': {'elo': 1640, 'record': '10-2-0', 'status': '🏆 챔피언'},
            '이리 프로하즈카': {'elo': 1560, 'record': '30-4-1', 'status': '랭커 (#1)'},
            '자마할 힐': {'elo': 1520, 'record': '12-2-0', 'status': '랭커 (#2)'},
            '마고메드 안칼라에프': {'elo': 1570, 'record': '19-1-1', 'status': '랭커 (#3)'},
            '얀 블라코비치': {'elo': 1480, 'record': '29-10-1', 'status': '랭커 (#4)'}
        },
        '미들급 (Middleweight)': {
            '드리쿠스 뒤 플레시스': {'elo': 1620, 'record': '21-2-0', 'status': '🏆 챔피언'},
            '이스라엘 아데산야': {'elo': 1580, 'record': '24-4-0', 'status': '랭커 (#1)'},
            '숀 스트릭랜드': {'elo': 1590, 'record': '28-6-0', 'status': '랭커 (#2)'},
            '로버트 휘태커': {'elo': 1550, 'record': '26-7-0', 'status': '랭커 (#3)'},
            '함자트 치마에프': {'elo': 1565, 'record': '13-0-0', 'status': '랭커 (#4)'}
        },
        '웰터급 (Welterweight)': {
            '벨랄 무하마드': {'elo': 1610, 'record': '24-3-0', 'status': '🏆 챔피언'},
            '리온 에드워즈': {'elo': 1570, 'record': '22-4-0', 'status': '랭커 (#1)'},
            '카마루 우스만': {'elo': 1540, 'record': '20-4-0', 'status': '랭커 (#2)'},
            '샤브카트 라흐모노프': {'elo': 1600, 'record': '18-0-0', 'status': '랭커 (#3)'},
            '이언 마샤도 개리': {'elo': 1520, 'record': '14-0-0', 'status': '랭커 (#4)'}
        },
        '라이트급 (Lightweight)': {
            '이슬람 마카체프': {'elo': 1680, 'record': '25-1-0', 'status': '🏆 챔피언'},
            '아르만 사루키안': {'elo': 1590, 'record': '22-3-0', 'status': '랭커 (#1)'},
            '찰스 올리베이라': {'elo': 1570, 'record': '34-10-0', 'status': '랭커 (#2)'},
            '저스틴 게이치': {'elo': 1510, 'record': '25-5-0', 'status': '랭커 (#3)'},
            '더스틴 포이리에': {'elo': 1520, 'record': '30-9-0', 'status': '랭커 (#4)'}
        },
        '페더급 (Featherweight)': {
            '일리아 토푸리아': {'elo': 1660, 'record': '15-0-0', 'status': '🏆 챔피언'},
            '알렉산더 볼카노프스키': {'elo': 1580, 'record': '26-4-0', 'status': '랭커 (#1)'},
            '맥스 할로웨이': {'elo': 1600, 'record': '26-7-0', 'status': '랭커 (#2)'},
            '브라이언 오르테가': {'elo': 1490, 'record': '16-3-0', 'status': '랭커 (#3)'},
            '야이르 로드리게스': {'elo': 1480, 'record': '19-5-0', 'status': '랭커 (#4)'}
        },
        '밴텀급 (Bantamweight)': {
            '메랍 드발리쉬빌리': {'elo': 1630, 'record': '18-4-0', 'status': '🏆 챔피언'},
            '션 오말리': {'elo': 1570, 'record': '17-2-0', 'status': '랭커 (#1)'},
            '말론 베라': {'elo': 1480, 'record': '23-9-1', 'status': '랭커 (#2)'},
            '헨리 세후도': {'elo': 1470, 'record': '16-4-0', 'status': '랭커 (#3)'},
            '코리 샌드헤이건': {'elo': 1530, 'record': '17-5-0', 'status': '랭커 (#4)'}
        }
    }

# 축구 국가 및 점수 저장소 초기화 (CSV 업로드 전에는 공백 혹은 기본값 수렴)
if 'soccer_data' not in st.session_state:
    st.session_state.soccer_data = {}

if 'match_logs' not in st.session_state:
    st.session_state.match_logs = []

# --- 2. 알고리즘 함수 정의 ---
def get_expected_score(r_a, r_b):
    return 1 / (1 + 10 ** ((r_b - r_a) / 400))

def update_elo(r_a, r_b, actual_score, k=30):
    expected = get_expected_score(r_a, r_b)
    new_r_a = r_a + k * (actual_score - expected)
    new_r_b = r_b + k * ((1 - actual_score) - (1 - expected))
    return round(new_r_a), round(new_r_b)

# --- UI 세팅 ---
st.set_page_config(layout="wide", page_title="Sports Elo Core")
st.title("🏆 전적 기반 실시간 스포츠 랭킹 인큐베이터")

main_tab1, main_tab2 = st.tabs(["⚽ 축구 (CSV 빌드 및 라이브 매치)", "🥊 UFC 7대 체급 센터"])

# ==========================================
# 탭 1: 축구 (CSV 업로드 기반 역사적 적산 시스템)
# ==========================================
with main_tab1:
    st.subheader("📁 과거 전적 데이터 통합 (CSV 업로드)")
    
    # 가이드 샘플 다운로드 기능 제공
    sample_csv = "홈팀,원정팀,홈팀득점,원정팀득점,중요도\n대한민국,일본,2,1,30\n아르헨티나,브라질,1,1,40\n프랑스,잉글랜드,0,2,30"
    st.download_button("예시 CSV 포맷 다운로드", data=sample_csv, file_name="soccer_sample.csv", mime="text/csv")
    
    uploaded_file = st.file_uploader("과거 경기 결과 CSV 파일을 업로드 하세요 (EUC-KR 또는 UTF-8)", type=["csv"])
    
    if uploaded_file is not None:
        try:
            # 파일 읽기 및 평탄화
            df_uploaded = pd.read_csv(uploaded_file, encoding='utf-8')
        except UnicodeDecodeError:
            uploaded_file.seek(0)
            df_uploaded = pd.read_csv(uploaded_file, encoding='euc-kr')
            
        if st.button("🚀 업로드된 전적 데이터 반영하여 초기 랭킹 계산"):
            # 임시 초기화 후 순차 적산
            temp_soccer = {}
            
            # 모든 등장 국가의 기본 점수를 1500으로 바인딩
            all_teams = set(df_uploaded['홈팀'].unique()).union(set(df_uploaded['원정팀'].unique()))
            for t in all_teams:
                temp_soccer[t] = 1500
                
            # 경기 한 건 한 건 순차적으로 Elo 포인트 교환 시뮬레이션 시행
            for idx, row in df_uploaded.iterrows():
                t_a, t_b = row['홈팀'], row['원정팀']
                s_a, s_b = int(row['홈팀득점']), int(row['원정팀득점'])
                k_val = int(row['중요도']) if '중요도' in df_uploaded.columns else 30
                
                r_a, r_b = temp_soccer[t_a], temp_soccer[t_b]
                actual = 1.0 if s_a > s_b else (0.5 if s_a == s_b else 0.0)
                
                new_a, new_b = update_elo(r_a, r_b, actual, k=k_val)
                temp_soccer[t_a], temp_soccer[t_b] = new_a, new_b
                
            st.session_state.soccer_data = temp_soccer
            st.success(f"총 {len(df_uploaded)}경기의 전적 연산이 완료되어 실시간 반영되었습니다!")

    st.divider()
    
    # 메인 축구 스케줄 및 인풋 영역
    col_l, col_r = st.columns([1, 1])
    
    with col_l:
        st.subheader("📊 축구 현재 실시간 랭킹")
        if st.session_state.soccer_data:
            df_s = pd.DataFrame(list(st.session_state.soccer_data.items()), columns=['국가', 'Elo Rating'])
            df_s = df_s.sort_values(by='Elo Rating', ascending=False).reset_index(drop=True)
            df_s.index += 1
            st.dataframe(df_s, use_container_width=True)
        else:
            st.warning("과거 전적 CSV를 업로드하거나 새로운 국가를 아래에서 추가하여 랭킹을 활성화해 주세요.")
            
        with st.expander("➕ 단일 국가 수동 추가"):
            c_input = st.text_input("추가할 국가명")
            if st.button("수동 등록") and c_input:
                st.session_state.soccer_data[c_input] = 1500
                st.rerun()

    with col_r:
        st.subheader("🔮 라이브 경기 매치업 & 실시간 반영")
        if len(st.session_state.soccer_data) >= 2:
            soccer_teams = list(st.session_state.soccer_data.keys())
            
            p_a = st.selectbox("팀 A (홈)", soccer_teams, key="p_a")
            p_b = st.selectbox("팀 B (원정)", soccer_teams, key="p_b")
            
            if p_a != p_b:
                el_a, el_b = st.session_state.soccer_data[p_a], st.session_state.soccer_data[p_b]
                prob_a = get_expected_score(el_a, el_b)
                
                c1, c2 = st.columns(2)
                c1.metric(f"{p_a} 기대 승률", f"{prob_a*100:.1f}%")
                c2.metric(f"{p_b} 기대 승률", f"{(1-prob_a)*100:.1f}%")
                st.progress(prob_a)
                
            st.write("---")
            st.markdown("##### 📝 실제 경기 결과 직접 입력 수렴")
            with st.form(key="live_soccer", clear_on_submit=True):
                team_a = st.selectbox("홈 팀", soccer_teams, key="t_a")
                team_b = st.selectbox("원정 팀", soccer_teams, key="t_b")
                sc_a = st.number_input("홈팀 득점", min_value=0, step=1, key="sc_a")
                sc_b = st.number_input("원정팀 득점", min_value=0, step=1, key="sc_b")
                k_factor = st.slider("경기 가중치", 10, 60, 30)
                
                if st.form_submit_button("라이트 랭킹 스코어 즉시 반영"):
                    if team_a == team_b:
                        st.error("동일한 팀을 매치할 수 없습니다.")
                    else:
                        cur_a, cur_b = st.session_state.soccer_data[team_a], st.session_state.soccer_data[team_b]
                        act = 1.0 if sc_a > sc_b else (0.5 if sc_a == sc_b else 0.0)
                        na, nb = update_elo(cur_a, cur_b, act, k=k_factor)
                        
                        st.session_state.soccer_data[team_a] = na
                        st.session_state.soccer_data[team_b] = nb
                        st.session_state.match_logs.append({"종목": "축구", "내용": f"{team_a} {sc_a}:{sc_b} {team_b} (Elo 갱신)"})
                        st.success("실시간 매치 결과가 가산되었습니다.")
                        st.rerun()
        else:
            st.info("실시간 경기 결과를 매칭하려면 최소 2개 이상의 국가 데이터가 상단 랭킹 테이블에 존재해야 합니다.")

# ==========================================
# 탭 2: UFC (7대 체급 대거 탑재 및 사이드바 연동)
# ==========================================
with main_tab2:
    st.info("왼쪽 사이드바에서 제어할 UFC 체급을 선택한 후 경기 승패 기록을 연동하세요.")
    
    # 사이드바 연동 제어부
    ufc_class = st.sidebar.selectbox("UFC 체급 선택 컨트롤러", list(st.session_state.ufc_data.keys()))
    fighters_list = list(st.session_state.ufc_data[ufc_class].keys())
    
    st.subheader(f"🥊 UFC {ufc_class} 공식 랭킹 및 로스터")
    
    # 랭킹 테이블 가시화
    ufc_rows = []
    for f_name, stats in st.session_state.ufc_data[ufc_class].items():
        ufc_rows.append({"파이터": f_name, "Elo Rating": stats['elo'], "공식전적": stats['record'], "타이틀 현황": stats['status']})
    df_ufc = pd.DataFrame(ufc_rows).sort_values(by="Elo Rating", ascending=False).reset_index(drop=True)
    df_ufc.index += 1
    st.dataframe(df_ufc, use_container_width=True)
    
    # 사이드바 폼 구축
    with st.sidebar.form(key="ufc_live_form", clear_on_submit=True):
        st.markdown(f"### ⚔️ {ufc_class} 매치 메이킹")
        fighter_a = st.selectbox("블루 코너", fighters_list)
        fighter_b = st.selectbox("레드 코너", fighters_list, index=1 if len(fighters_list)>1 else 0)
        outcome = st.radio("경기 승패 결과", [f"{fighter_a} 승리", f"{fighter_b} 승리"])
        submit_u = st.form_submit_button("UFC 대결 결과 확정")
        
    if submit_u:
        if fighter_a == fighter_b:
            st.sidebar.error("동일 인물 대결은 불가합니다.")
        else:
            elo_u_a = st.session_state.ufc_data[ufc_class][fighter_a]['elo']
            elo_u_b = st.session_state.ufc_data[ufc_class][fighter_b]['elo']
            
            score_u_a = 1.0 if fighter_a in outcome else 0.0
            new_ua, new_ub = update_elo(elo_u_a, elo_u_b, score_u_a, k=40)
            
            st.session_state.ufc_data[ufc_class][fighter_a]['elo'] = new_ua
            st.session_state.ufc_data[ufc_class][fighter_b]['elo'] = new_ub
            
            st.session_state.match_logs.append({"종목": f"UFC {ufc_class}", "내용": f"{outcome} ({fighter_a} vs {fighter_b})"})
            st.sidebar.success("파이터 실시간 서열이 재조정되었습니다.")
            st.rerun()

    # 통합 매치 히스토리
    if st.session_state.match_logs:
        st.divider()
        st.subheader("📜 실시간 매치 이력 로그 (종합)")
        st.dataframe(pd.DataFrame(st.session_state.match_logs).iloc[::-1], use_container_width=True)
