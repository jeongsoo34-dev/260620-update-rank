import streamlit as st
import pandas as pd

# 1. UFC 맞춤형 초기 데이터 세팅
if 'ufc_data' not in st.session_state:
    st.session_state.ufc_data = {
        '헤비급 (Heavyweight)': {
            '존 존스': {'elo': 1650, 'record': '27-1-0', 'status': '🏆 챔피언'},
            '톰 아스피날': {'elo': 1620, 'record': '14-3-0', 'status': '잠정 챔피언'},
            '시릴 간': {'elo': 1550, 'record': '12-2-0', 'status': '랭커 (#1)'},
            '세르게이 파블로비치': {'elo': 1510, 'record': '18-2-0', 'status': '랭커 (#2)'}
        },
        '라이트헤비급 (Light Heavyweight)': {
            '알렉스 페레이라': {'elo': 1640, 'record': '10-2-0', 'status': '🏆 챔피언'},
            '이리 프로하즈카': {'elo': 1560, 'record': '30-4-1', 'status': '랭커 (#1)'},
            '자마할 힐': {'elo': 1530, 'record': '12-2-0', 'status': '랭커 (#2)'},
            '마고메드 안칼라에프': {'elo': 1555, 'record': '19-1-1', 'status': '랭커 (#3)'}
        },
        '라이트급 (Lightweight)': {
            '이슬람 마카체프': {'elo': 1680, 'record': '25-1-0', 'status': '🏆 챔피언'},
            '아르만 사루키안': {'elo': 1580, 'record': '22-3-0', 'status': '랭커 (#1)'},
            '찰스 올리베이라': {'elo': 1570, 'record': '34-10-0', 'status': '랭커 (#2)'},
            '저스틴 게이치': {'elo': 1520, 'record': '25-5-0', 'status': '랭커 (#3)'}
        }
    }

if 'match_history' not in st.session_state:
    st.session_state.match_history = []

# 2. Elo 공식 정의
def calculate_elo(rating_a, rating_b, outcome, k=40):
    expected_a = 1 / (1 + 10 ** ((rating_b - rating_a) / 400))
    expected_b = 1 / (1 + 10 ** ((rating_a - rating_b) / 400))
    new_a = rating_a + k * (outcome - expected_a)
    new_b = rating_b + k * ((1 - outcome) - expected_b)
    return round(new_a), round(new_b)

# --- UI 레이아웃 구성 ---
st.set_page_config(layout="wide", page_title="UFC 실시간 체급별 랭킹")
st.title("🥊 UFC 실시간 체급별 랭킹 및 프로필 센터")
st.markdown("체급별 랭킹 현황 확인과 가상 경기 입력에 따른 실시간 랭킹 시스템입니다.")

# 사이드바: 매치 결과 입력 및 랭킹 갱신
st.sidebar.header("⚔️ 경기 결과 등록 (Match Update)")
weight_class_input = st.sidebar.selectbox("대상 체급 선택", list(st.session_state.ufc_data.keys()))
fighters_in_class = list(st.session_state.ufc_data[weight_class_input].keys())

# 코드 수정 부분: `with` 블록 내부에서 서브밋 버튼을 호출해야 안전합니다.
with st.sidebar.form(key='ufc_match_form', clear_on_submit=True):
    fighter_a = st.selectbox("블루 코너 (Fighter A)", fighters_in_class, index=0)
    fighter_b = st.selectbox("레드 코너 (Fighter B)", fighters_in_class, index=1 if len(fighters_in_class) > 1 else 0)
    
    result = st.radio("경기 결과", [f"{fighter_a} 승리 (피니시)", f"{fighter_a} 판정승", f"{fighter_b} 판정승", f"{fighter_b} 승리 (피니시)"])
    
    # 🌟 수정 완료: st.sidebar.form_submit_button이 아닌 st.form_submit_button을 사용합니다.
    submit_btn = st.form_submit_button("체급 랭킹 즉시 반영")

if submit_btn:
    if fighter_a == fighter_b:
        st.sidebar.error("서로 다른 선수를 매칭해 주세요!")
    else:
        # 가중치 분기 (KO, 서브미션 피니시 승리 시 추가 가중치 부여)
        k_factor = 50 if "피니시" in result else 32
        outcome_a = 1.0 if fighter_a in result else 0.0
        
        old_elo_a = st.session_state.ufc_data[weight_class_input][fighter_a]['elo']
        old_elo_b = st.session_state.ufc_data[weight_class_input][fighter_b]['elo']
        
        new_elo_a, new_elo_b = calculate_elo(old_elo_a, old_elo_b, outcome_a, k=k_factor)
        
        # 전적 파싱 및 업데이트
        def update_wld(record, is_winner):
            w, l, d = map(int, record.split('-'))
            if is_winner:
                w += 1
            else:
                l += 1
            return f"{w}-{l}-{d}"
            
        st.session_state.ufc_data[weight_class_input][fighter_a]['elo'] = new_elo_a
        st.session_state.ufc_data[weight_class_input][fighter_b]['elo'] = new_elo_b
        
        st.session_state.ufc_data[weight_class_input][fighter_a]['record'] = update_wld(st.session_state.ufc_data[weight_class_input][fighter_a]['record'], outcome_a == 1.0)
        st.session_state.ufc_data[weight_class_input][fighter_b]['record'] = update_wld(st.session_state.ufc_data[weight_class_input][fighter_b]['record'], outcome_a == 0.0)
        
        st.session_state.match_history.append({
            '체급': weight_class_input,
            '매치내용': f"{fighter_a} vs {fighter_b}",
            '결과': result,
            '점수변동': f"{fighter_a}({old_elo_a}➔{new_elo_a}) | {fighter_b}({old_elo_b}➔{new_elo_b})"
        })
        st.success(f"🔥 경기 결과가 정상 수렴되었습니다: {result}!")

# --- 메인 영역: 레이아웃 배분 ---
col1, col2 = st.columns([1.2, 1])

with col1:
    st.subheader(f"📊 {weight_class_input} 실시간 공식 랭킹")
    raw_dict = st.session_state.ufc_data[weight_class_input]
    
    # 데이터프레임 빌드 및 Elo 랭킹 정렬
    df_data = []
    for f_name, stats in raw_dict.items():
        df_data.append({'선수명': f_name, 'Elo 점수': stats['elo'], '전적': stats['record'], '타이틀/상태': stats['status']})
    
    df = pd.DataFrame(df_data).sort_values(by='Elo 점수', ascending=False).reset_index(drop=True)
    df.index = df.index + 1
    st.dataframe(df, use_container_width=True)

with col2:
    st.subheader("🔍 파이터 정보 & 상세 프로필 동적 센터")
    selected_fighter = st.selectbox("조회할 파이터를 선택하세요", fighters_in_class)
    
    # 사람을 선택하면 하단 탭 내용이 동적으로 변화하는 코어 로직
    f_info = st.session_state.ufc_data[weight_class_input][selected_fighter]
    
    tab1, tab2, tab3 = st.tabs(["👤 기본 프로필", "📈 실시간 Elo 지표", "📜 전적 로그"])
    
    with tab1:
        st.write(f"### **{selected_fighter}**")
        st.write(f"- **소속 체급:** {weight_class_input}")
        st.write(f"- **현재 지위:** {f_info['status']}")
        st.write(f"- **종합 전적:** {f_info['record']}")
        
    with tab2:
        st.metric(label="현재 Elo Rating", value=f"{f_info['elo']} 점수", delta=f"{f_info['elo'] - 1500} (초기값 대비)")
        st.info("Elo 점수가 1600점 이상인 선수는 타이틀 컨텐더 급 기량을 지닌 것으로 분류됩니다.")
        
    with tab3:
        fighter_matches = [m for m in st.session_state.match_history if selected_fighter in m['매치내용']]
        if fighter_matches:
            st.dataframe(pd.DataFrame(fighter_matches), use_container_width=True)
        else:
            st.warning("등록된 최근 경기 기록이 존재하지 않습니다.")
