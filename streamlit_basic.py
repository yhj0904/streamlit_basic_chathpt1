import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

# 페이지 설정
st.set_page_config(
    page_title="Garabu Chat",
    page_icon="💬",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 심플한 CSS 스타일
st.markdown("""
    <style>
    /* 전체 배경 */
    .stApp {
        background-color: #f8f9fa;
    }

    /* 제목 스타일 */
    h1 {
        color: #2c3e50;
        font-weight: 600;
        padding-bottom: 1rem;
        border-bottom: 2px solid #e9ecef;
        margin-bottom: 2rem;
    }

    /* 채팅 메시지 개선 */
    .stChatMessage {
        background-color: white;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }

    /* 버튼 스타일 */
    .stButton > button {
        background-color: #4a5568;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
        transition: background-color 0.2s;
    }

    .stButton > button:hover {
        background-color: #2d3748;
    }

    /* 사이드바 */
    .css-1d391kg {
        background-color: #ffffff;
        border-right: 1px solid #e9ecef;
    }

    /* 입력창 */
    .stChatInput {
        border: 1px solid #dee2e6;
        border-radius: 8px;
        background-color: white;
    }

    /* 메트릭 스타일 */
    [data-testid="metric-container"] {
        background-color: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# 사이드바
with st.sidebar:
    st.markdown("### ⚙️ 설정")

    # API Key
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key:
        openai_api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            placeholder="sk-..."
        )

    # 모델 선택
    model = st.selectbox(
        "모델",
        ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]
    )

    # Temperature
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1)

    st.divider()

    # 채팅 초기화
    if st.button("대화 초기화", use_container_width=True):
        st.session_state.messages = [
            {"role": "assistant", "content": "안녕하세요! 무엇을 도와드릴까요?"}
        ]
        st.rerun()

    # 통계
    if "messages" in st.session_state:
        st.divider()
        st.caption("📊 대화 통계")
        total = len(st.session_state.messages)
        user = sum(1 for m in st.session_state.messages if m["role"] == "user")
        st.text(f"전체: {total} | 사용자: {user}")

# 메인 제목
st.title("💬 Garabu Chat")

# 세션 초기화
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "안녕하세요! 무엇을 도와드릴까요?"}
    ]

# 대화 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 사용자 입력
if prompt := st.chat_input("메시지를 입력하세요..."):
    if not openai_api_key:
        st.error("⚠️ API Key를 입력해주세요")
        st.stop()

    # 사용자 메시지 추가
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # AI 응답
    with st.chat_message("assistant"):
        try:
            client = OpenAI(api_key=openai_api_key)

            # 스트리밍 응답
            stream = client.chat.completions.create(
                model=model,
                messages=st.session_state.messages,
                temperature=temperature,
                stream=True
            )

            response = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": response})

        except Exception as e:
            st.error(f"오류: {str(e)}")