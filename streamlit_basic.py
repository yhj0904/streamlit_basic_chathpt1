import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os
import time

load_dotenv()

# 페이지 설정
st.set_page_config(
    page_title="Garabu's AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS 스타일
st.markdown("""
    <style>
    /* 전체 배경 그라데이션 */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }

    /* 메인 컨테이너 스타일 */
    .main {
        padding: 2rem;
        border-radius: 20px;
        backdrop-filter: blur(10px);
    }

    /* 제목 스타일 */
    .main-title {
        text-align: center;
        background: linear-gradient(90deg, #FF6B6B, #4ECDC4, #45B7D1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        animation: glow 2s ease-in-out infinite alternate;
    }

    @keyframes glow {
        from { filter: brightness(1); }
        to { filter: brightness(1.2); }
    }

    .subtitle {
        text-align: center;
        color: #ffffff;
        font-size: 1.2rem;
        margin-bottom: 2rem;
        opacity: 0.9;
    }

    /* 채팅 메시지 스타일 */
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.3);
        backdrop-filter: blur(10px);
    }

    /* 사용자 메시지 스타일 */
    .stChatMessage[data-testid="user-message"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-left: 20%;
    }

    /* AI 메시지 스타일 */
    .stChatMessage[data-testid="assistant-message"] {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        margin-right: 20%;
    }

    /* 입력창 스타일 */
    .stChatInput {
        border-radius: 25px;
        border: 2px solid #667eea;
        padding: 0.5rem 1rem;
        background-color: rgba(255, 255, 255, 0.9);
    }

    /* 사이드바 스타일 */
    .css-1d391kg {
        background: linear-gradient(180deg, #2D3748 0%, #1A202C 100%);
    }

    .sidebar-content {
        padding: 1rem;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        margin-bottom: 1rem;
    }

    /* 버튼 스타일 */
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }

    /* 정보 박스 스타일 */
    .info-box {
        background: rgba(255, 255, 255, 0.1);
        border-left: 4px solid #4ECDC4;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        color: white;
    }

    /* 링크 스타일 */
    a {
        color: #4ECDC4 !important;
        text-decoration: none;
        font-weight: 600;
        transition: color 0.3s ease;
    }

    a:hover {
        color: #45B7D1 !important;
        text-decoration: underline;
    }

    /* 스크롤바 스타일 */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }

    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }

    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    </style>
    """, unsafe_allow_html=True)

# 사이드바 설정
with st.sidebar:
    st.markdown("## ⚙️ Settings")

    # API Key 설정
    with st.expander("🔑 API Configuration", expanded=True):
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if openai_api_key:
            st.success("✅ API Key Loaded")
        else:
            openai_api_key = st.text_input(
                "OpenAI API Key",
                key="chatbot_api_key",
                type="password",
                placeholder="sk-..."
            )

    st.markdown("---")

    # 모델 선택
    st.markdown("### 🤖 Model Selection")
    model_option = st.selectbox(
        "Choose AI Model",
        ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"],
        index=0
    )

    # 온도 설정
    temperature = st.slider(
        "Temperature (Creativity)",
        min_value=0.0,
        max_value=2.0,
        value=0.7,
        step=0.1,
        help="Higher values make output more random"
    )

    st.markdown("---")

    # 채팅 히스토리 관리
    st.markdown("### 💬 Chat Management")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = [
                {"role": "assistant", "content": "안녕하세요! 윤형주님의 AI 어시스턴트입니다. 무엇을 도와드릴까요? 😊"}
            ]
            st.rerun()

    with col2:
        if st.button("💾 Save Chat", use_container_width=True):
            st.info("Chat saved! (Feature coming soon)")

    st.markdown("---")

    # 유용한 링크
    st.markdown("### 🔗 Useful Links")
    st.markdown('<div class="info-box">', unsafe_allow_html=True)
    st.markdown("📚 [OpenAI Documentation](https://platform.openai.com/docs)")
    st.markdown("🔑 [Get API Key](https://platform.openai.com/account/api-keys)")
    st.markdown("💻 [Source Code](https://github.com/streamlit/llm-examples/blob/main/Chatbot.py)")
    st.markdown("🚀 [Open in GitHub Codespaces](https://codespaces.new/streamlit/llm-examples?quickstart=1)")
    st.markdown('</div>', unsafe_allow_html=True)

    # 통계 정보
    st.markdown("---")
    st.markdown("### 📊 Chat Statistics")
    if "messages" in st.session_state:
        total_messages = len(st.session_state.messages)
        user_messages = sum(1 for msg in st.session_state.messages if msg["role"] == "user")
        st.metric("Total Messages", total_messages)
        st.metric("Your Messages", user_messages)

# 메인 헤더
st.markdown('<h1 class="main-title">🤖 윤형주\'s AI Chat Assistant</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Powered by OpenAI GPT • Ask me anything!</p>', unsafe_allow_html=True)

# 환영 메시지 컨테이너
if "first_visit" not in st.session_state:
    st.session_state.first_visit = True
    with st.container():
        cols = st.columns(3)
        with cols[0]:
            st.info("💡 **Tip**: You can adjust the creativity level in the sidebar")
        with cols[1]:
            st.info("🎯 **Pro tip**: Try different models for various tasks")
        with cols[2]:
            st.info("⚡ **Fast**: Get instant responses to your questions")

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "안녕하세요! 윤형주님의 AI 어시스턴트입니다. 무엇을 도와드릴까요? 😊"}
    ]

# 채팅 기록 표시 (컨테이너 사용)
chat_container = st.container()
with chat_container:
    for idx, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            if msg["role"] == "assistant":
                st.markdown(f'<div style="color: #2D3748;">{msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(msg["content"])

# 사용자 입력 처리
if prompt := st.chat_input("메시지를 입력하세요... 💭"):
    if not openai_api_key:
        st.error("⚠️ OpenAI API key를 입력해주세요!")
        st.stop()

    # 사용자 메시지 추가
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI 응답 생성
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            client = OpenAI(api_key=openai_api_key)

            # 스트리밍 효과를 위한 타이핑 애니메이션
            with st.spinner("생각 중..."):
                response = client.chat.completions.create(
                    model=model_option,
                    messages=st.session_state.messages,
                    temperature=temperature,
                    stream=True
                )

                for chunk in response:
                    if chunk.choices[0].delta.content is not None:
                        full_response += chunk.choices[0].delta.content
                        message_placeholder.markdown(full_response + "▌")

                message_placeholder.markdown(full_response)

            # 응답을 세션 상태에 저장
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(f"❌ 오류가 발생했습니다: {str(e)}")
            st.info("API 키를 확인하거나 잠시 후 다시 시도해주세요.")

# 푸터 추가
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: rgba(255,255,255,0.7); padding: 1rem;">
        Made by Garabu
    </div>
    """,
    unsafe_allow_html=True
)