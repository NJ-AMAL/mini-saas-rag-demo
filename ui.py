import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.title("Mini SaaS – RAG Client Portal")
st.write("🔐 Ask questions; answers come only from your documents")

api_key = st.text_input("API Key", type="password")

if api_key:
    headers = {"X-API-KEY": api_key}

    question = st.text_input("Ask a question about your documents:")

    if question and st.button("Get Answer"):
        response = requests.get(
            f"{API_URL}/answer",
            headers=headers,
            params={"question": question}
        )

        if response.status_code == 200:
            data = response.json()
            st.subheader("Answer")
            st.write(data["answer"])
        else:
            st.error(response.json().get("detail", "Unknown error"))
