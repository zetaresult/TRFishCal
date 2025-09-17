# %%writefile app.py
import streamlit as st
import numpy as np
import pandas as pd
import math

import gspread
from google.oauth2.service_account import Credentials
import datetime


from streamlit_javascript import st_javascript
import base64 

st.set_page_config(
    page_title="테일즈런너 종합계산기",
    page_icon="🎣"
)

def connect_to_gsheet():
        
    SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=SCOPE)
    client = gspread.authorize(creds)
    
    SHEET_NAME = "trfish-feedback"
    sheet = client.open(SHEET_NAME).sheet1

    return sheet
    
def save_feedback(name, feedback):
    sheet = connect_to_gsheet()
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([name, feedback, now])
    
def levelExpected(currentLevel, goalLevel, currentPer, pageTotal):
    levelData = np.load('lvlExp.npy', allow_pickle=True)
    currentEXP = levelData[currentLevel][2] + (levelData[currentLevel][1] * (currentPer/100)) + pageTotal
    indices = np.where(levelData[:,2] <= currentEXP)[0]
    if len(indices) == 0: expectedLvl = 0
    else: expectedLvl = indices[-1]
        
    if goalLevel != -1: 
        expRequired = int(levelData[goalLevel][2] - currentEXP)
        if expectedLvl >= goalLevel: expRequired = max(0, expRequired)
    else: #목표레벨 안쓸경우
        expRequired = -1 

    if expectedLvl >= len(levelData) - 1:
        nowPer = 100.0
    else:
        nowPer = (levelData[expectedLvl][1] - (levelData[expectedLvl+1][2] - currentEXP)) * (100 / levelData[expectedLvl][1])
    return expectedLvl ,expRequired, nowPer
def calcBait(FTime): return sum(FTime) / 2
    
def formatTime(totalSeconds):
    days = int(totalSeconds // (60 * 60 * 24))
    hours = int((totalSeconds % (60 * 60 * 24)) // (60 * 60))
    minutes = int((totalSeconds % (60 * 60)) // 60)

    parts = []
    if days > 0:
        parts.append(f"{days}일")
    if hours > 0:
        parts.append(f"{hours}시간")
    if minutes > 0:
        parts.append(f"{minutes}분")

    if not parts:  # 전부 0인 경우
        return "0분"
    return " ".join(parts)
    
@st.dialog("예약종료 사용법")
def scheduleInfo():
    st.markdown("""
1. 키보드에서 `윈도우키` + `R` 키를 동시에 눌러 `실행` 창을 엽니다.  
2. 입력 창에 명령어를 붙여넣고 `Enter` 키를 누르세요.  

> ℹ️ 평균적인 시간이므로 실제 어획물과 차이가 있을 수 있습니다.  
> 반드시 낚싯대와 낚시 프렌즈를 선택 후 예약 종료 명령어를 입력 바랍니다.  
> (명령어 끝이 0일 경우, 컴퓨터가 강제 종료됩니다.)
""")

@st.dialog("피드백 작성")
def feedback_dialog():
    st.markdown("추가할 아이템이나 그 외 피드백 주시면 감사하겠습니다.😊")
    st.markdown("아이디어도 환영합니다!")
    st.markdown("> ℹ️본 피드백은 IP 등 사용자의 어떠한 정보도 수집하지 않습니다.")
    # name = st.text_input("닉네임 (적지 않으셔도 무방합니다.):") # 굳이 입력 받을 필요 없을 듯
    name = "익명"
    feedback = st.text_area("피드백을 작성해주세요.")
    
    if st.button("제출"):
        # if not name.strip():
        #     # st.warning("이름을 입력해주세요.")
        #     name = "익명" # 이름 입력받고 싶으면
        if not feedback.strip():
            st.warning("피드백을 입력해주세요.")
            return
        save_feedback(name, feedback)
        st.success("피드백 감사합니다! 🎉")
        st.session_state.feedback_submitted = True

def get_image_base64(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


Tbaits = [
    {"name": "삼각 주먹떡밥", "exp": 153, "tr": 20},
    {"name": "크릴 새우 필라프", "exp": 703, "tr": 100},
    {"name": "갯지렁이 훈제 구이", "exp": 2363, "tr": 500},
    {"name": "황금 갯지렁이", "exp": 5644, "tr": 1500},
    {"name": "다이아 갯지렁이", "exp": 10701, "tr": 5000},
    ]

Cbaits = [
    {"name": "황제 지렁이", "exp": 19562},
    {"name": "장군 지렁이", "exp": 21658},
    {"name": "여왕 지렁이", "exp": 22056},
    {"name": "승리의 지렁이", "exp": 21972},
    {"name": "선샤인 지렁이", "exp": 22124},
    {"name": "별빛 지렁이", "exp": 22223},
    {"name": "해왕강림 지렁이", "exp": 22189},
    ]

#### 낚싯대

fishing_rods = {
    "낚싯대 선택": (0, 0, 0),
    "죽도 낚싯대": (40, 80, 0),
    "천사의 낚싯대": (30, 90, 100),
    "악마의 낚싯대": (50, 70, 100),
    "매직 스타 낚싯대": (40, 70, 50),
    "푸른 장미검 낚싯대": (30, 80, 50),
    "테런 낚싯대": (15, 20, 150),
    "강태공의 낚싯대": (60, 100, 0),
    "대나무 낚싯대": (60, 120, 0),
}

sorted_rods_keys = sorted(k for k in fishing_rods if k != "낚싯대 선택")
ordered_rods_keys = ["낚싯대 선택"] + sorted_rods_keys

fishing_friends = {
    "낚시 프렌즈" : (0, 0, 0),
    "화이트 똑똑 쥐돌이": (0, 8, 60),
    "토집사와 아기토끼": (10, 0, 100),
    "미드나잇 쿠션냥": (4, 4, 80),
    "밀덕이는 낚시 중": (5, 0, 140),
    "쌀덕이는 낚시 중": (0, 10, 120),
    "낚시중": (2, 2, 15),
    "화이트 재롱둥이 물개": (2, 2, 40),
    "블랙 재롱둥이 물개": (0, 5, 30),
    "옐로우 헝그리베어": (0, 6, 20),
    "핑크 헝그리베어": (6, 0, 20),
    "화이트 헝그리베어": (3, 3, 20),
}

sorted_friends_keys = sorted(k for k in fishing_friends if k != "낚시 프렌즈")
ordered_friends_keys = ["낚시 프렌즈"] + sorted_friends_keys


st.sidebar.title("테일즈런너 유틸모음")
menu = st.sidebar.radio(
    "메뉴 선택 (추후 추가 예정)",
    ["경험치 및 낚시 계산기", "경험치 ↔ 지렁이"],
    index = 0 # 기본값
)
if menu == "경험치 및 낚시 계산기":
    col1, col2 = st.columns([3,1])
    with col1:
        st.markdown(f"<div style='font-size: 25px; font-weight: bold; margin-top: 12px;'>레벨 경험치 계산", unsafe_allow_html=True)
    with col2:
        if st.button("피드백"):
            feedback_dialog()
    if st.session_state.get("feedback_submitted", False):
            # st.success("피드백 감사합니다! 🎉")
            st.session_state.feedback_submitted = False
    
    st.write(" ")
    levelName = np.load("lvlExp.npy", allow_pickle=True)
    levelName = levelName[:,0]
    
    levelColor =  ["빨강 ", "주황 ", "노랑 ", "초록 ", "파랑 ", "남색 ", "보라 "]
    levelShoes = [' '.join(levelName[i].split()[1:]) for i in range(0,len(levelName), 7)]


    cols = st.columns([1,1.5,1])
    Ccolor = cols[0].selectbox("현재 레벨", levelColor, accept_new_options=False)
    Cshoes = cols[1].selectbox("", levelShoes, accept_new_options=False)
    currentPer_str = cols[2].text_input("경험치 ( % )", value="0.0")
    
    selectCLevel = Ccolor+Cshoes
    try:
        currentPer = float(currentPer_str)
        if currentPer >= 100:
                st.error("100 미만의 숫자를 입력해주세요.")
                currentPer = 0.0
        elif currentPer < 0:
                st.error("0 이상의 숫자를 입력해주세요.")
                currentPer = 0.0
    except ValueError:
        st.error("숫자를 입력해주세요.")
        currentPer = 0.0
    
    ClevelIndex = (np.where(levelName == selectCLevel)[0][0]) 
    
    
    # currentPer = st.number_input("현재 경험치(%) 입력", min_value=0.0, max_value=100.0, value=0.0, step=0.01) # 버전이 달라지고 에러 생김
    

    try:
        currentPer = float(currentPer_str)
        if currentPer >= 100:
                st.error("100 미만의 숫자를 입력해주세요.")
                currentPer = 0.0
        elif currentPer < 0:
                st.error("0 이상의 숫자를 입력해주세요.")
                currentPer = 0.0
    except ValueError:
        st.error("숫자를 입력해주세요.")
        currentPer = 0.0
    
    st.markdown("""
    <style>
        @media (max-width: 600px) {
            div[data-testid="stHorizontalBlock"] {
                overflow-x: auto;
                white-space: nowrap;
                -webkit-overflow-scrolling: touch;
            }
            div[data-testid="stHorizontalBlock"] > div {
                display: inline-block !important;
                vertical-align: top;
                float: none !important;
                white-space: normal;
                min-width: 150px;
            }
        }
    </style>
    """, unsafe_allow_html=True)
    
    # useGoalLevel = st.checkbox("목표 레벨 계산", value=True) # 체크해제하고 쓸 사람은 없을듯 하여 삭제
    useGoalLevel = True
    cols = st.columns([1,1.5,1])
    if useGoalLevel:
        
        Gcolor = cols[0].selectbox("목표 레벨", levelColor, key="goal_color", accept_new_options=False)
        Gshoes = cols[1].selectbox("", levelShoes, key="goal_shoes", accept_new_options=False)
        selectGLevel = Gcolor+Gshoes
        cols[2].markdown("")
        # selectGLevel = st.selectbox("목표 레벨", levelName)
        GlevelIndex = (np.where(levelName == selectGLevel)[0][0])
    else:
        st.write("목표 레벨을 통해 계산하려면 위 체크박스를 체크해주세요.")
        selectGLevel, GlevelIndex = -1, -1
    
    
    useFishPage = st.checkbox("낚시 페이지 계산", value=False)
    if useFishPage:
        st.write(" ")
        st.write("낚시 페이지 계산")
        cols = st.columns([1,1])
        page1 = cols[0].number_input("페이지1 입력", min_value=0, value=0, step=1)
        page2 = cols[1].number_input("페이지2 입력", min_value=0, value=0, step=1)
        cols2 = st.columns([1,1])
        page3 = cols2[0].number_input("페이지3 입력", min_value=0, value=0, step=1)
        page4 = cols2[1].number_input("페이지4 입력", min_value=0, value=0, step=1)
        cols3 = st.columns([1,1])
        page5 = cols2[0].number_input("페이지5 입력", min_value=0, value=0, step=1)
        page6 = cols2[1].number_input("페이지6 입력", min_value=0, value=0, step=1)
        totalPage = page1+page2+page3+page4+page5+page6
    else:
        totalPage = 0
        
    expectedLvl ,expRequired, nowPer = levelExpected(ClevelIndex, GlevelIndex, currentPer, totalPage)
    
    per = nowPer / 100 * 100  # 0~100%
    
    if expRequired != -1: 
        barText = f"{nowPer:.2f}% ({expRequired:,} EXP 남음)"
        if (useGoalLevel) and (expRequired == 0): barText = f"{nowPer:.2f}%"
    else: barText = f"{nowPer:.2f}%"
    
    bar_html = f"""
    <div style="width: 100%; background: linear-gradient(90deg, #ddd, #f5f5f5); border: 1px solid #ccc; border-radius: 12px; height: 32px; position: relative; margin-top: 16px; box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);">
        <div style="width: {per}%; background: linear-gradient(90deg, #4CAF50, #45a049); height: 100%;
                    border-radius: 12px 0 0 12px; transition: width 0.4s ease;"></div>
        <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;
                    display: flex; align-items: center; justify-content: center;
                    font-weight: 600; color: #222; font-size: 15px;">
            {barText}
        </div>
    </div>
    """

    #이미지 출력 위함

    image_path = f"./level/{expectedLvl}.png"
    img_base64 = get_image_base64(image_path)
    
    st.markdown(
        f"""
        <div style='font-size: 18px; font-weight: bold; margin-top: 12px; display: flex; align-items: center;'>
            현재 예상 레벨 :
            <img src='data:image/png;base64,{img_base64}' style='height: 1.1em; margin: 0 5px;'/>
            <span style='font-size: 14px; font-weight: bold;'>{levelName[expectedLvl]}</span>
        </div>
        """, 
        unsafe_allow_html=True
    )
    st.markdown(bar_html, unsafe_allow_html=True)
    
    ###### 지렁이 계산은 코인, 쓰레기 제외
    st.write(" ")
    
    
    st.write(" ")
    st.markdown(f"<div style='font-size: 25px; font-weight: bold; margin-top: 12px;'>낚시 시간 및 지렁이 계산", unsafe_allow_html=True)
    
    st.write(" ")
    premium_storage = st.checkbox("프리미엄 티켓", value=False)
    cols = st.columns(2)
    rod = cols[0].selectbox("낚싯대 종류 (가나다순)", ordered_rods_keys, index=0)
    if rod == "테런 낚싯대": 
        st.markdown(f"<div style='font-size: 15px; font-weight: bold; margin-top: 12px;'>테런 낚싯대 계산은 편차가 심합니다.</div>", unsafe_allow_html=True)
        st.write(" ")
    friend = cols[1].selectbox("낚시 프렌즈 (가나다순)", ordered_friends_keys, index=0)
    min_default, max_default, storage_default = fishing_rods[rod]
    f_min, f_max, f_storage = fishing_friends[friend]
    
    # min_default -= f_min
    # max_default -= f_max
    min_default = max(0, min_default - f_min) # 에러처리를 위함
    max_default = max(0, max_default - f_max) # 프렌즈를 먼저 고를 경우 음수로 에러남.
    storage_default += f_storage
    
    
    cols = st.columns(2)
    minFTime = cols[0].number_input("낚시 최소시간", min_value=0, value=min_default, step=1)
    maxFTime = cols[1].number_input("낚시 최대시간", min_value=0, value=max_default, step=1)
    
    if premium_storage: storage_default += 300
    else: storage_default += 150
    fishStorage = st.number_input("최대 살림망", min_value=0, value=storage_default, step=1)
    
    f_average_sec = (minFTime+maxFTime)/2
    if rod == '테런 낚싯대': f_average_sec /= 1.7 # 보정
    
    st.markdown(f"<div style='font-size: 20px; font-weight: bold; margin-top: 12px;'>한 마리 당 약 {f_average_sec:.1f}초</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size: 20px; font-weight: bold; margin-top: 12px;'>최대 살림망 까지 약 {formatTime(f_average_sec*fishStorage)}</div>", unsafe_allow_html=True)

    if round((f_average_sec*fishStorage)) != 0 : st.markdown(f"<div style='font-size: 15px; font-weight: bold; margin-top: 12px;'>컴퓨터 예약 종료 명령어 : shutdown -s -t {round((f_average_sec)*fishStorage)}</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size: 15px; font-weight: bold; margin-top: 12px;'>예약 취소 명령어 : shutdown -a</div>", unsafe_allow_html=True)
    
    st.write(" ")
    if st.button("[컴퓨터 예약 종료 설명 보기]"):
        scheduleInfo()
    
    st.write(" ")
    st.write(" ")
    
    def render_bait_cards(baits, expRequired, isCash=False):
        cols = st.columns(2)  # 2열 생성
    
        for i, bait in enumerate(baits):
            count = round(expRequired / bait["exp"])
            total = count * (49 if isCash else bait["tr"])
            totalSeconds = count * calcBait([minFTime, maxFTime])
    
            with cols[i % 2]:
                st.markdown(f"""
                <table style="width:100%; border-collapse: collapse; font-size:13px; line-height:1.6; margin-bottom:16px;">
                    <thead>
                        <tr>
                            <th style="text-align:left; padding:8px; font-size:16px;" colspan="2">{bait['name']}</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td style="padding:8px; width:50%;"><b>개수:</b></td>
                            <td style="padding:8px;">{count:,}개</td>
                        </tr>
                        <tr>
                            <td style="padding:8px;"><b>{'총 캐시:' if isCash else '총 TR:'}</b></td>
                            <td style="padding:8px;">{total:,} {'캐시' if isCash else 'TR'}</td>
                        </tr>
                        <tr>
                            <td style="padding:8px;"><b>예상 시간:</b></td>
                            <td style="padding:8px;">{formatTime(totalSeconds)}</td>
                        </tr>
                    </tbody>
                </table>
                """, unsafe_allow_html=True)


    if useGoalLevel:
        st.markdown("#### 목표 레벨에 필요한 지렁이 정보")
    
        st.markdown("##### 일반 지렁이")
        render_bait_cards(Tbaits, expRequired, isCash=False)
    
        st.markdown("##### 캐시 지렁이")
        render_bait_cards(Cbaits, expRequired, isCash=True)
        
elif menu == "경험치 ↔ 지렁이":

    def set_mode_xp_to_worms():
        st.session_state.mode = "xp_to_worms"
        st.session_state.selectCount = False

    def set_mode_worms_to_xp():
        st.session_state.mode = "worms_to_xp"
        st.session_state.selectExp = False

    
    all_baits = Tbaits + Cbaits
    bait_names = [bait["name"] for bait in all_baits]
    selected_name2 = st.selectbox("지렁이를 선택하세요", bait_names)
    
    selected_bait = next(b for b in all_baits if b["name"] == selected_name2)
    selected_exp = selected_bait["exp"]

    st.checkbox("얻고 싶은 경험치 → 필요한 지렁이 수 계산", key="selectExp", on_change=set_mode_xp_to_worms)
    st.checkbox("지렁이 수 → 얻는 경험치 계산", key="selectCount", on_change=set_mode_worms_to_xp)

    if not st.session_state.selectExp and not st.session_state.selectCount:    st.session_state.mode = None
    mode = st.session_state.get("mode", None)

    if mode == "xp_to_worms":
        st.subheader("목표 경험치 → 필요한 지렁이 수 계산")
    
        target_xp = st.number_input("목표 경험치 입력", min_value=0, value=0, step=1)

        if target_xp > 0:
            st.markdown(f"<div style='font-size: 20px; font-weight: bold; margin-top: 12px;'>{selected_name2} : 약 {math.ceil(target_xp/selected_exp):,}개가 필요합니다.</div>", unsafe_allow_html=True)
            

    elif mode == "worms_to_xp":
        st.subheader("지렁이 수 → 얻는 총 경험치 계산")
        
        target_count = st.number_input("지렁이 개수 입력", min_value=0, value=0, step=1)
        
        if target_count > 0:
            st.markdown(f"<div style='font-size: 20px; font-weight: bold; margin-top: 12px;'>{selected_name2}의 개수는 약 {round(selected_exp * target_count):,}EXP 입니다.</div>", unsafe_allow_html=True)

    
    else:
        st.info("계산 방식을 하나 선택해주세요.")
    

