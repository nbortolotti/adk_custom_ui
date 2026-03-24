import streamlit as st
import httpx
import json

st.set_page_state = "wide"
st.title("ADK Custom Chat UI")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("Escribe tu mensaje aquí..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Call backend
    with st.chat_message("assistant"):
        try:
            with st.spinner("Pensando..."):
                response = httpx.post(
                    "http://localhost:8000/chat",
                    json={
                        "user_id": "test_user",
                        "session_id": "test_session",
                        "message": prompt
                    },
                    timeout=60.0
                )
            
            if response.status_code == 200:
                answer = response.json().get("response", "No se encontró respuesta.")
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            else:
                st.error(f"Error del servidor: {response.status_code}")
                st.code(response.text)
        except httpx.ConnectError:
            st.error("No se pudo conectar al backend. Asegúrate de que `backend.py` esté corriendo en el puerto 8000.")
        except Exception as e:
            st.error(f"Ocurrió un error: {e}")