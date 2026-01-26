import streamlit as st

UPDATES = [
    {
        "title": "피드백 업데이트(26-01-26)",
        "items": [
            "최고 레벨일 때 경험치(EXP)로 표기 (기존 사항: 100% 고정)",
        ],
        "link": "",
        "note": "누락된 사항이 있으면 피드백 버튼 이용 바랍니다.",
    },
    {
        "title": "피드백 업데이트(26-01-23)",
        "items": [
            "**달토끼 낚싯대** 추가",
            "**낚시 프렌즈**(장사꾼 수달 등 7개) 추가",
        ],
        "link": "",
        "note": "누락된 사항이 있으면 피드백 버튼 이용 바랍니다.",
    },
    
    {
        "title": "피드백 업데이트(26-01-05)",
        "items": [
            "**무지개 왕관 지렁이** 추가",
        ],
        "link": "",
        "note": "그 외 누락된 사항이 있으면 피드백 버튼 이용 바랍니다!",
    },
    {
        "title": "테일즈런너 10월 2차 업데이트",
        "items": [
            "달토끼 낚싯대 삭제",
            "업데이트로 추가된 **영혼 낚싯대**, **지렁베로스의 원혼**, **[어빌리티]휴대용 살림망** 추가",
            "**황금 갯갯갯지렁이**, **다이아 갯갯갯지렁이** 추가",
        ],
        "link": "https://tr.rhaon.co.kr/news/updates/77?page=1",
        "note": "그 외 누락된 사항이 있으면 피드백 버튼 이용 바랍니다!",
    },
    {
        "title": "테일즈런너 10월 1차 업데이트",
        "items": [
            "추석 이벤트에 추가된 **달토끼 낚싯대**, **달나라 지렁이** 추가.",
            "낚시 프렌즈 시간 개선에 따라 수정완료.",
            "**테런 낚싯대** 및 **달토끼 낚싯대** **30분, 1시간** 획득량 추가.",
        ],
        "link": "https://tr.rhaon.co.kr/news/updates/76?page=1",
        "note": "그 외 개선 사항은 피드백 버튼 이용 바랍니다!",
    },
  
]


@st.dialog("업데이트 내역")
def update_info():
    for i, update in enumerate(UPDATES):
        with st.expander(update['title'], expanded=(i == 0)):
            for idx, item in enumerate(update["items"], start=1):
                st.markdown(f"{idx}. {item}  ")
            check_link = f"""
참고 : [{update['title']}]({update['link']})  
> {update['note']}  
""" if update['link'] != '' else f"""
> {update['note']}  
"""
            st.markdown(check_link)
