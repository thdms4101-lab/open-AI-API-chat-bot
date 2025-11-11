import streamlit as st
import openai

# Set the page title
st.set_page_config(page_title="Art Historian Chatbot")
st.title("🎨 Art Historian Chatbot")

# --- THE CRITICAL SECURITY STEP ---
# Load the API key from Streamlit's secrets manager
try:
    openai.api_key = st.secrets["OPENAI_API_KEY"]
except KeyError:
    st.error("OpenAI API key not found. Please add it to your Streamlit secrets.")
    st.stop()

# --- THE ROLE DEFINITION ---
# This is the "persona" we discussed
SYSTEM_PROMPT = """
You are a professional art historian specializing in the Italian Renaissance. 
Your tone is academic, insightful, and detailed. When a user asks about a 
piece of art, provide its historical context, the artist's biography, and 
a brief analysis of its technique and symbolism.
"""

# --- CONVERSATION MEMORY ---
# Initialize the chat history in Streamlit's session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "assistant", "content": "Greetings. How may I assist you with your art history query today?"}
    ]

# Display past messages
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# --- CHAT INPUT AND API CALL ---
# Get new user input
if prompt := st.chat_input("Ask about a Renaissance artwork..."):
    
    # 1. Add user message to session state
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # 2. Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # 3. Call the OpenAI API
    try:
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            # Send the *entire* chat history to OpenAI
            response_stream = openai.chat.completions.create(
                model="gpt-4o", # or "gpt-3.5-turbo"
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True, # Stream the response for a "typing" effect
            )
            
            # Process the stream
            for chunk in response_stream:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌") # Show a typing cursor
            
            message_placeholder.markdown(full_response)
        
        # 4. Add AI response to session state
        st.session_state.messages.append({"role": "assistant", "content": full_response})

    except openai.RateLimitError:
        st.error("You have exceeded your OpenAI API quota. Please check your billing.")
    except Exception as e:
        st.error(f"An error occurred: {e}")
