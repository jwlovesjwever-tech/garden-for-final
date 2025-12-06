import streamlit as st
from openai import OpenAI

# 페이지 설정
st.set_page_config(
    page_title="감정 챗봇",
    page_icon="💭",
    layout="wide"
)

# 제목과 설명
st.title("💭 감정 상담 챗봇")
st.write("당신의 감정을 공유해주세요. 함께 고민해보겠습니다.")

# OpenAI API 키 로드 (secrets.toml에서 자동으로 로드)
try:
    openai_api_key = st.secrets["OPENAI_API_KEY"]
except KeyError:
    st.error("❌ OpenAI API 키가 설정되지 않았습니다. `.streamlit/secrets.toml` 파일을 확인해주세요.")
    st.stop()

# OpenAI 클라이언트 생성
client = OpenAI(api_key=openai_api_key)

# 감정 메뉴판
emotions = [
    "기쁘다", "감동적이다", "흥미롭다", "뿌듯하다", "설레다", 
    "궁금하다", "슬프다", "서운하다", "불안하다", "걱정스럽다", 
    "두렵다", "불편하다", "황당하다", "짜증나다", "무섭다", 
    "괘씸하다", "답답하다", "못마땅하다", "힘들다", "부끄럽다(수치심)", 
    "당황하다", "곤란하다", "부담스럽다", "불쾌하다", "속상하다", "기타"
]

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []
if "selected_emotions" not in st.session_state:
    st.session_state.selected_emotions = []
if "custom_emotion" not in st.session_state:
    st.session_state.custom_emotion = ""
if "stage" not in st.session_state:
    st.session_state.stage = "emotions"  # 상태: emotions, q1, q2, chatting
if "answer_q1" not in st.session_state:
    st.session_state.answer_q1 = ""
if "answer_q2" not in st.session_state:
    st.session_state.answer_q2 = ""

# 레이아웃: 2개 칼럼
col1, col2 = st.columns([1, 2])

# 왼쪽 칼럼: 감정 선택
with col1:
    st.subheader("📋 감정 선택")
    
    # 여러 개의 감정 선택 (기타 제외)
    emotions_without_other = [e for e in emotions if e != "기타"]
    selected_emotions = st.multiselect(
        "어떤 감정을 느끼고 계신가요? (여러 개 선택 가능)",
        options=emotions_without_other,
        default=st.session_state.selected_emotions,
        label_visibility="collapsed"
    )
    st.session_state.selected_emotions = selected_emotions
    
    # 기타 선택 시 커스텀 입력
    custom_emotion = st.text_input(
        "다른 감정을 입력해주세요 (선택사항):",
        value=st.session_state.custom_emotion
    )
    st.session_state.custom_emotion = custom_emotion
    
    # 최종 감정 리스트 구성
    final_emotions = st.session_state.selected_emotions.copy()
    if custom_emotion:
        final_emotions.append(custom_emotion)
    
    emotion_display = ", ".join(final_emotions) if final_emotions else "감정 선택 필요"

# 오른쪽 칼럼: 챗봇
with col2:
    st.subheader("💬 상담 대화")
    
    if not final_emotions:
        st.info("👈 왼쪽에서 감정을 선택해주세요.")
    else:
        # 현재 단계별 화면 표시
        if st.session_state.stage == "q1":
            st.write(f"**선택한 감정:** {emotion_display}")
            st.write("---")
            st.write("### 첫 번째 질문:")
            st.write("**어떤 일이 있었어? 너가 선택한 감정을 중심으로 이야기해줘.**")
            
            answer_q1 = st.text_area(
                "답변:",
                key="input_q1",
                height=120,
                label_visibility="collapsed"
            )
            
            if answer_q1:
                if st.button("✅ 답변 제출", key="submit_q1"):
                    st.session_state.answer_q1 = answer_q1
                    st.session_state.messages.append({
                        "role": "user",
                        "content": f"질문 1. 어떤 일이 있었어? 너가 선택한 감정을 중심으로 이야기해줘.\n\n답변: {answer_q1}"
                    })
                    st.session_state.stage = "q2"
                    st.rerun()
        
        elif st.session_state.stage == "q2":
            st.write(f"**선택한 감정:** {emotion_display}")
            st.write("---")
            st.write("### 첫 번째 질문")
            st.write(f"**어떤 일이 있었어? 너가 선택한 감정을 중심으로 이야기해줘.**")
            st.info(st.session_state.answer_q1)
            
            st.write("---")
            st.write("### 두 번째 질문:")
            st.write("**어떤 도움이 필요해? 어떤 조언을 구하고 싶은지 이야기해줘.**")
            
            answer_q2 = st.text_area(
                "답변:",
                key="input_q2",
                height=120,
                label_visibility="collapsed"
            )
            
            if answer_q2:
                if st.button("✅ 답변 제출 & 조언 받기", key="submit_q2"):
                    st.session_state.answer_q2 = answer_q2
                    st.session_state.messages.append({
                        "role": "user",
                        "content": f"질문 2. 어떤 도움이 필요해? 어떤 조언을 구하고 싶은지 이야기해줘.\n\n답변: {answer_q2}"
                    })
                    st.session_state.stage = "chatting"
                    st.rerun()
        
        elif st.session_state.stage == "chatting":
            # 채팅 메시지 표시
            chat_container = st.container(height=400)
            with chat_container:
                for message in st.session_state.messages:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])
            
            # 시스템 프롬프트 구성 (청각장애인, 중학생 고려)
            emotions_str = ", ".join(final_emotions)
            system_prompt = f"""당신은 감정을 이해하고 공감해주는 따뜻한 상담 챗봇입니다.

중요한 규칙:
1. 사용자는 청각장애인입니다. "듣는다", "말한다"의 표현을 절대 사용하지 마세요.
2. 사용자는 중학생입니다. 짧고 명확하고 이해하기 쉬운 말을 사용하세요.
3. 한 번에 한두 가지만 조언하세요.
4. 사용자의 상황이 모호하면, 조언하기 전에 더 구체적으로 물어보세요.
5. 항상 공감하고 격려하는 태도를 유지하세요.
6. 조언은 3-5문장 정도로 짧고 명확하게 제시하세요.

사용자의 감정: {emotions_str}"""
            
            # 첫 챗봇 메시지가 없으면 생성
            if len(st.session_state.messages) == 2:  # Q1, Q2 답변만 있는 상태
                try:
                    with st.chat_message("assistant"):
                        message_placeholder = st.empty()
                        full_response = ""
                        
                        stream = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[
                                {"role": "system", "content": system_prompt}
                            ] + st.session_state.messages,
                            stream=True,
                            temperature=0.7,
                            max_tokens=500
                        )
                        
                        for chunk in stream:
                            if chunk.choices[0].delta.content:
                                full_response += chunk.choices[0].delta.content
                                message_placeholder.markdown(full_response + "▌")
                        
                        message_placeholder.markdown(full_response)
                    
                    # 어시스턴트 응답 저장
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": full_response
                    })
                    
                    st.rerun()
                
                except Exception as e:
                    st.error(f"❌ 오류 발생: {str(e)}")
            
            else:
                # 추가 대화 입력
                user_input = st.chat_input("더 묻고 싶은 것이 있으면 이야기해주세요...")
                
                if user_input:
                    # 사용자 메시지 저장
                    st.session_state.messages.append({
                        "role": "user",
                        "content": user_input
                    })
                    
                    st.rerun()
                
                # 어시스턴트 응답이 필요하면 생성
                if st.session_state.messages[-1]["role"] == "user":
                    try:
                        with st.chat_message("assistant"):
                            message_placeholder = st.empty()
                            full_response = ""
                            
                            stream = client.chat.completions.create(
                                model="gpt-4o-mini",
                                messages=[
                                    {"role": "system", "content": system_prompt}
                                ] + st.session_state.messages,
                                stream=True,
                                temperature=0.7,
                                max_tokens=500
                            )
                            
                            for chunk in stream:
                                if chunk.choices[0].delta.content:
                                    full_response += chunk.choices[0].delta.content
                                    message_placeholder.markdown(full_response + "▌")
                            
                            message_placeholder.markdown(full_response)
                        
                        # 어시스턴트 응답 저장
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": full_response
                        })
                        
                        st.rerun()
                    
                    except Exception as e:
                        st.error(f"❌ 오류 발생: {str(e)}")
        
        else:  # stage == "emotions"
            if st.button("🚀 시작하기", key="start_button"):
                st.session_state.stage = "q1"
                st.session_state.messages = []
                st.rerun()
        
        # 대화 초기화 버튼
        if st.session_state.stage != "emotions":
            st.divider()
            if st.button("🔄 처음부터 시작", key="reset_button"):
                st.session_state.stage = "emotions"
                st.session_state.messages = []
                st.session_state.answer_q1 = ""
                st.session_state.answer_q2 = ""
                st.rerun()
