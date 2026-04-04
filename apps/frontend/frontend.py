import streamlit as st
import httpx

st.set_page_config(layout="wide")
st.title("Technical Learning Coach")

# Session state to hold our dynamic user configuration
if "current_user_id" not in st.session_state:
    st.session_state["current_user_id"] = "test_engineer_id"

# Sidebar settings configuration
with st.sidebar:
    st.header("Simulation Settings")
    input_user_id = st.text_input("User ID", value=st.session_state["current_user_id"])
    if st.button("Simulate Login", type="primary"):
        st.session_state["current_user_id"] = input_user_id
        if "messages" in st.session_state:
            del st.session_state["messages"]
        st.rerun()

user_id = st.session_state["current_user_id"]

# Initialize chat history and trigger proactive greeting
if "messages" not in st.session_state:
    st.session_state.messages = []
    
    with st.spinner("Identifying learning opportunities..."):
        try:
            # Trigger initial proactive message
            response = httpx.post(
                "http://localhost:8000/learning_coach/chat",
                json={
                    "user_id": user_id,
                    "session_id": "learning_coach_session",
                    "message": f"Hi, I just logged in. My engineer ID is '{user_id}'. As my Technical Learning Coach, please analyze my recent commits and proactively suggest a nano-learning opportunity based on what you find. Share exactly one clear suggestion in a conversational and encouraging tone, starting with predicting what I've been doing."
                },
                timeout=60.0
            )
            if response.status_code == 200:
                answer = response.json().get("response", "No response found..")
                st.session_state.messages.append({"role": "assistant", "content": answer})
            else:
                st.session_state.messages.append({"role": "assistant", "content": "Welcome! I couldn't connect to my analysis engine."})
        except httpx.ConnectError:
            st.session_state.messages.append({"role": "assistant", "content": "Welcome! Please ensure the backend is running to analyze your commits."})
        except Exception as e:
            st.session_state.messages.append({"role": "assistant", "content": f"An error occurred while initializing: {e}"})

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("Write your message here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Call backend
    with st.chat_message("assistant"):
        try:
            with st.spinner("Thinking..."):
                response = httpx.post(
                    "http://localhost:8000/learning_coach/chat",
                    json={
                        "user_id": user_id,
                        "session_id": "learning_coach_session",
                        "message": prompt
                    },
                    timeout=60.0
                )
            
            if response.status_code == 200:
                answer = response.json().get("response", "No response found.")
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            else:
                st.error(f"Server error: {response.status_code}")
                st.code(response.text)
        except httpx.ConnectError:
            st.error("Could not connect to the backend. Make sure `backend.py` is running on port 8000.")
        except Exception as e:
            st.error(f"An error occurred: {e}")