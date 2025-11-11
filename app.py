import streamlit as st
import openai

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="미술사 챗봇")
st.title("🎨 미술사학자 챗봇")

# --- 2. (수정됨) 사용자로부터 API 키 받기 ---
# 사이드바에 텍스트 입력 칸을 만듭니다.
# type="password"로 설정하면 키가 가려져 보입니다.
api_key = st.sidebar.text_input("OpenAI API Key", type="password")

if not api_key:
    # 키가 입력되지 않았으면 안내 메시지를 띄웁니다.
    st.info("👈 사이드바에 OpenAI API 키를 입력하고 시작하세요.")
    st.stop() # 앱 실행 중지

# 입력받은 키로 OpenAI 클라이언트 설정
try:
    openai.api_key = api_key
except Exception as e:
    st.error(f"API 키 설정 오류: {e}")
    st.stop()


# --- 3. 역할 정의 (이전과 동일) ---
SYSTEM_PROMPT = """
당신은 이탈리아 르네상스 전문 미술사학자입니다. 
당신의 어조는 학술적이고, 통찰력 있으며, 상세합니다. 사용자가 작품에 대해 물어보면, 
역사적 배경, 작가의 생애, 그리고 기술과 상징성에 대한 간단한 분석을 제공해야 합니다. 
현대적인 속어를 사용하지 마세요.
"""

# --- 4. 대화 기록 (이전과 동일) ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "assistant", "content": "안녕하세요. 미술사 관련 질문에 답변해 드립니다."}
    ]

# 이전 대화 내용 화면에 표시
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# --- 5. 챗봇 입력 및 API 호출 (이전과 동일) ---
if prompt := st.chat_input("르네상스 작품에 대해 질문해보세요..."):
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    try:
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            response_stream = openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            )
            
            for chunk in response_stream:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
        
        st.session_state.messages.append({"role": "assistant", "content": full_response})

    except openai.RateLimitError:
        st.error("API 할당량을 초과했거나 키가 유효하지 않습니다. 키를 확인해주세요.")
    except Exception as e:
        st.error(f"오류가 발생했습니다: {e}")
