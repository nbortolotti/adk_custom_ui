import streamlit as st
import httpx

st.set_page_config(layout="wide", page_title="Git Tutor")
st.title("Personal Git Tutor")

if "current_user_id" not in st.session_state:
    st.session_state["current_user_id"] = "student_1"

with st.sidebar:
    st.header("Settings")
    input_user_id = st.text_input("User ID", value=st.session_state["current_user_id"])
    if st.button("Start New Session", type="primary"):
        st.session_state["current_user_id"] = input_user_id
        if "git_tutor_messages" in st.session_state:
            del st.session_state["git_tutor_messages"]
        st.rerun()

user_id = st.session_state["current_user_id"]

if "git_tutor_messages" not in st.session_state:
    st.session_state.git_tutor_messages = []
    
    with st.spinner("Initializing your Git tutor..."):
        try:
            response = httpx.post(
                "http://localhost:8000/git_tutor/chat",
                json={
                    "user_id": user_id,
                    "session_id": "git_tutor_session",
                    "message": "Hello, I'm ready to start my Git training. Tell me what the first task is."
                },
                timeout=60.0
            )
            if response.status_code == 200:
                answer = response.json().get("response", "No response found.")
                st.session_state.git_tutor_messages.append({"role": "assistant", "content": answer})
            else:
                st.session_state.git_tutor_messages.append({"role": "assistant", "content": "Welcome. I couldn't connect with the tutor."})
        except httpx.ConnectError:
            st.session_state.git_tutor_messages.append({"role": "assistant", "content": "Make sure the backend is running on port 8000."})
        except Exception as e:
            st.session_state.git_tutor_messages.append({"role": "assistant", "content": f"An error occurred: {e}"})

for message in st.session_state.git_tutor_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Type 'ready' when you've completed the task or ask for help if you need it..."):
    st.session_state.git_tutor_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            with st.spinner("Validating..."):
                response = httpx.post(
                    "http://localhost:8000/git_tutor/chat",
                    json={
                        "user_id": user_id,
                        "session_id": "git_tutor_session",
                        "message": prompt
                    },
                    timeout=60.0
                )
            
            if response.status_code == 200:
                answer = response.json().get("response", "No response found.")
                st.markdown(answer)
                st.session_state.git_tutor_messages.append({"role": "assistant", "content": answer})
            else:
                st.error(f"Server error: {response.status_code}")
        except httpx.ConnectError:
            st.error("Could not connect to the backend.")
        except Exception as e:
            st.error(f"An error occurred: {e}")
