# %%writefile app.py

import trlib as tr
import trupdate as trU
from trdata import (
    T_BAITS, 
    C_BAITS, 
    FISHING_RODS, 
    FISHING_FRIENDS, 
    ORDERED_ROD_KEYS, 
    ORDERED_FRIENDS_KEYS,
)

import streamlit as st
import numpy as np
import math



st.set_page_config(
    page_title="테일즈런너 종합계산기",
    page_icon="🎣"
)

st.sidebar.title("테일즈런너 유틸모음")
MENU = st.sidebar.radio(
    "메뉴 선택 (추후 추가 예정)",
    ["경험치 및 낚시 계산기", "경험치 ↔ 지렁이"],
    index = 0 # 기본값
)
if MENU == "경험치 및 낚시 계산기":
    if st.button("[ 업데이트 내역 (26-03-27) ]"):
        trU.update_info()
        
    col1, col2 = st.columns([3,1])
    with col1:
        st.markdown(f"<div style='font-size: 25px; font-weight: bold; margin-top: 12px;'>레벨 경험치 계산", unsafe_allow_html=True)
    with col2:
        if st.button("피드백"):
            tr.feedback_dialog()
    if st.session_state.get("feedback_submitted", False):
            st.session_state.feedback_submitted = False
    
    st.write(" ")
    level_name = np.load("lvlExp.npy", allow_pickle=True)
    level_name = level_name[:,0]
    
    level_color =  ["빨강 ", "주황 ", "노랑 ", "초록 ", "파랑 ", "남색 ", "보라 "]
    level_shoe = [' '.join(level_name[i].split()[1:]) for i in range(0,len(level_name), 7)]


    cols = st.columns([1,1.5,1])
    cur_color = cols[0].selectbox("현재 레벨", level_color, accept_new_options=False)
    cur_shoe = cols[1].selectbox("", level_shoe, accept_new_options=False)
    cur_per_str = cols[2].text_input("경험치 ( % )", value="0.0")
    
    select_cur_level = cur_color+cur_shoe

    cur_level_index = (np.where(level_name == select_cur_level)[0][0]) 

    if cur_per_str.strip() == "":
        current_per = 0.0
    else:
        try:
            current_per = float(cur_per_str)
            if current_per >= 100:
                    st.error("100 미만의 숫자를 입력해주세요.")
                    current_per = 0.0
            elif current_per < 0:
                    st.error("0 이상의 숫자를 입력해주세요.")
                    current_per = 0.0
        except ValueError:
            st.error("숫자를 입력해주세요.")
            current_per = 0.0
    
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
    
    cols = st.columns([1,1.5,1])
    
    goal_color = cols[0].selectbox("목표 레벨", level_color, key="goal_color", accept_new_options=False)
    goal_shoe = cols[1].selectbox("", level_shoe, key="goal_shoes", accept_new_options=False)
    select_goal_level = goal_color+goal_shoe
    cols[2].markdown("")
    goal_level_index = (np.where(level_name == select_goal_level)[0][0])
    
    
    use_fish_page = st.checkbox("낚시 페이지 계산", value=False)
    if use_fish_page:
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
        total_page = page1+page2+page3+page4+page5+page6
    else:
        total_page = 0
        
    expected_level ,exp_required, now_per, use_goal_level, extra_exp = tr.level_expected(cur_level_index, goal_level_index, current_per, total_page)
    
    per = now_per / 100 * 100  # 0~100%

    if extra_exp != -1:
        barText = f"({extra_exp:,} EXP)"
    elif exp_required != -1: 
        barText = f"{now_per:.2f}% ({exp_required:,} EXP 남음)"
        if (use_goal_level) and (exp_required == 0): barText = f"{now_per:.2f}%"
    else: barText = f"{now_per:.2f}%"
    
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

    image_path = f"./level/{expected_level}.png"
    img_base64 = tr.get_image_base64(image_path)
    
    st.markdown(
        f"""
        <div style='font-size: 18px; font-weight: bold; margin-top: 12px; display: flex; align-items: center;'>
            예상 레벨 :
            <img src='data:image/png;base64,{img_base64}' style='height: 1.1em; margin: 0 5px;'/>
            <span style='font-size: 14px; font-weight: bold;'>{level_name[expected_level]}</span>
        </div>
        """, 
        unsafe_allow_html=True
    )
    st.markdown(bar_html, unsafe_allow_html=True)
    st.markdown("---")

    st.markdown(f"<div style='font-size: 25px; font-weight: bold; margin-top: 12px;'>낚시 시간 계산", unsafe_allow_html=True)
    
    st.write(" ")
    premium_storage = st.checkbox("프리미엄 티켓", value=False)
    ability_storage = st.checkbox("[어빌리티] 휴대용 살림망", value=False)
    cols = st.columns(2)
    rod = cols[0].selectbox("낚싯대 종류 (가나다순)", ORDERED_ROD_KEYS, index=0)

    friend = cols[1].selectbox("낚시 프렌즈 (가나다순)", ORDERED_FRIENDS_KEYS, index=0)
    min_default, max_default, storage_default = FISHING_RODS[rod]
    f_min, f_max, f_storage = FISHING_FRIENDS[friend]
    
    min_default = max(0, min_default - f_min) 
    max_default = max(0, max_default - f_max) 
    storage_default += f_storage
    
    
    cols = st.columns(2)
    min_fish_time = cols[0].number_input("낚시 최소시간", min_value=0, value=min_default, step=1)
    max_fish_time = cols[1].number_input("낚시 최대시간", min_value=0, value=max_default, step=1)
    fish_time = [min_fish_time, max_fish_time]
    if premium_storage: storage_default += 300
    else: storage_default += 150

    if ability_storage: storage_default += 5


    fish_storage = st.number_input("최대 살림망", min_value=0, value=storage_default, step=1)
    
    f_average_sec = (min_fish_time+max_fish_time)/2

    st.markdown(f"<div style='font-size: 20px; font-weight: bold; margin-top: 12px;'>한 마리 당 약 {f_average_sec:.1f}초</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size: 20px; font-weight: bold; margin-top: 12px;'>최대 살림망 까지 약 {tr.format_time(f_average_sec*fish_storage)}</div>", unsafe_allow_html=True)


    if rod == '테런 낚싯대' or rod == "달토끼 낚싯대":
        st.markdown(f"""
            <div style="font-size: 15px; font-weight: bold; margin-top: 12px; margin-bottom: 8px;">
                {rod} 시간별 정보
            </div>
            <table style="width:100%; border-collapse: collapse; font-size:13px; line-height:1.6; margin-bottom:16px; border: 1px solid #ccc;">
                <thead>
                    <tr>
                        <th style="text-align:left; padding:8px;">시간</th>
                        <th style="text-align:left; padding:8px;">예상 획득량</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td style="padding:8px;">30분</td>
                        <td style="padding:8px;">약 {int((30*60)//f_average_sec)}마리</td>
                    </tr>
                    <tr>
                        <td style="padding:8px;">1시간</td>
                        <td style="padding:8px;">약 {int((60*60)//f_average_sec)}마리</td>
                    </tr>
                </tbody>
            </table>
        """, unsafe_allow_html=True)
        
    
    if round((f_average_sec*fish_storage)) != 0 : 
        st.markdown(f"<div style='font-size: 15px; font-weight: bold; margin-top: 12px;'>컴퓨터 예약 종료 명령어 : shutdown -s -t {round((f_average_sec)*fish_storage)}</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size: 15px; font-weight: bold; margin-top: 12px;'>예약 취소 명령어 : shutdown -a</div>", unsafe_allow_html=True)
    
    st.write(" ")
    if st.button("[컴퓨터 예약 종료 설명 보기]"):
        tr.schedule_info()
    
    st.markdown("---")
    
    if use_goal_level:
        st.markdown("#### 목표 레벨에 필요한 지렁이 정보")
    
        st.markdown("##### 일반 지렁이")
        tr.render_bait_cards(T_BAITS, exp_required, fish_time, isCash=False)
    
        st.markdown("##### 캐시 지렁이")
        tr.render_bait_cards(C_BAITS, exp_required, fish_time, isCash=True)
        
elif MENU == "경험치 ↔ 지렁이":

    
    all_baits = T_BAITS + C_BAITS
    bait_names = [bait["name"] for bait in all_baits]
    selected_name2 = st.selectbox("지렁이를 선택하세요", bait_names)
    
    selected_bait = next(b for b in all_baits if b["name"] == selected_name2)
    selected_exp = selected_bait["exp"]

    st.checkbox("얻고 싶은 경험치 → 필요한 지렁이", key="selectExp", on_change=tr.set_mode_xp_to_worms)
    st.checkbox("지렁이 수 → 얻는 경험치 계산", key="selectCount", on_change=tr.set_mode_worms_to_xp)

    if not st.session_state.selectExp and not st.session_state.selectCount:    st.session_state.mode = None
    mode = st.session_state.get("mode", None)

    if mode == "xp_to_worms":
        st.subheader("경험치 입력 → 필요한 지렁이 수 계산")
    
        target_xp = st.number_input("목표 경험치 입력", min_value=0, value=0, step=1)

        if target_xp > 0:
            st.markdown(f"<div style='font-size: 20px; font-weight: bold; margin-top: 12px;'>{selected_name2} : 약 {math.ceil(target_xp/selected_exp):,}개가 필요합니다.</div>", unsafe_allow_html=True)
            

    elif mode == "worms_to_xp":
        st.subheader("지렁이 수 → 얻는 총 경험치 계산")
        
        target_count = st.number_input("지렁이 개수 입력", min_value=0, value=0, step=1)
        
        if target_count > 0:
            st.markdown(f"<div style='font-size: 20px; font-weight: bold; margin-top: 12px;'>{selected_name2} {target_count}개는 약 {round(selected_exp * target_count):,}EXP 입니다.</div>", unsafe_allow_html=True)

    
    else:
        st.info("계산 방식을 하나 선택해주세요.")
    
































