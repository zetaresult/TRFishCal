# %%writefile trlib.py

import streamlit as st
import numpy as np

import gspread
from google.oauth2.service_account import Credentials
import datetime

import base64 


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

def level_expected(current_level, goal_level, current_per, page_total):
    level_data = np.load('lvlExp.npy', allow_pickle=True)
    current_exp = level_data[current_level][2] + (level_data[current_level][1] * (current_per/100)) + page_total
    indices = np.where(level_data[:,2] <= current_exp)[0]
    if len(indices) == 0: expected_level = 0
    else: expected_level = indices[-1]

    if goal_level != -1: 
        exp_required = int(level_data[goal_level][2] - current_exp)
        if expected_level >= goal_level: exp_required = max(0, exp_required)
    else: #목표레벨 안쓸경우
        exp_required = -1 

    if expected_level >= len(level_data) - 1:
        now_per = 100.0
    else:
        now_per = (level_data[expected_level][1] - (level_data[expected_level+1][2] - current_exp)) * (100 / level_data[expected_level][1])
    return expected_level ,exp_required, now_per

def calc_bait(fish_time): return sum(fish_time) / 2

def format_time(total_seconds):
    days = int(total_seconds // (60 * 60 * 24))
    hours = int((total_seconds % (60 * 60 * 24)) // (60 * 60))
    minutes = int((total_seconds % (60 * 60)) // 60)

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
    
@st.dialog("업데이트 내역")
def update_info():
    st.markdown("""
### 테일즈런너 10월 1차 업데이트
1. 추석 이벤트에 추가된 **달토끼 낚싯대**, **달나라 지렁이** 추가.  
2. 낚시 프렌즈 시간 개선에 따라 수정완료.  
3. **테런 낚싯대** 및 **달토끼 낚싯대** **30분, 1시간** 획득량 추가.  

참고 : [테일즈런너 10월 1차 업데이트](https://tr.rhaon.co.kr/news/updates/76?page=1)

> 그 외 개선 사항은 피드백 버튼 이용 바랍니다!  
""")


@st.dialog("예약종료 사용법")
def schedule_info():
    st.markdown("""
1. 키보드에서 `윈도우키` + `R` 키를 동시에 눌러 `실행` 창을 엽니다.  
2. 입력 창에 명령어를 붙여넣고 `Enter` 키를 누르세요.  

> ℹ️ 평균적인 시간이므로 실제 어획물과 차이가 있을 수 있습니다.  
> 반드시 낚싯대와 낚시 프렌즈를 선택 후 예약 종료 명령어를 입력 바랍니다.  
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

def get_price(bait, isCash):
    return bait["cash"] if isCash else bait["tr"]
    
def get_total_text(count, price, isCash):
    if price == -1:
        return "[추석 이벤트] 구매 불가"
    elif price == -2:
        return "[획득 불가]"
    else:
        total = count * price
        currency = "캐시" if isCash else "TR"
        return f"{total:,} {currency}"

def render_bait_cards(baits, exp_required, fish_time, isCash=False):
    cols = st.columns(2)  # 2열 생성

    for i, bait in enumerate(baits):
        count = round(exp_required / bait["exp"])

        price = get_price(bait, isCash)

        total_print = get_total_text(count, price, isCash)
        total_seconds = count * calc_bait(fish_time)
        
        
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
                        <td style="padding:8px;">{total_print}</td>
                    </tr>
                    <tr>
                        <td style="padding:8px;"><b>예상 시간:</b></td>
                        <td style="padding:8px;">{format_time(total_seconds)}</td>
                    </tr>
                </tbody>
            </table>
            """, unsafe_allow_html=True)


def set_mode_xp_to_worms():
    st.session_state.mode = "xp_to_worms"
    st.session_state.selectCount = False

def set_mode_worms_to_xp():
    st.session_state.mode = "worms_to_xp"
    st.session_state.selectExp = False






