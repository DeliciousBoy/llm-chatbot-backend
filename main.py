import os
import time

import chromadb
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types
from sentence_transformers import SentenceTransformer

load_dotenv()
API_KEY = os.getenv("API_KEY")

client = genai.Client(api_key=API_KEY)
EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
PERSIST_PATH = "data/04_chroma_db"
CHROMA_COLLECTION = "forum_data"


def retrieve_relevant_documents(
    user_query: str, embed_model: str, persist_path: str, top_k: int = 5
):
    # Load Chroma client and collection
    client = chromadb.PersistentClient(path=persist_path)
    collection = client.get_or_create_collection(name=CHROMA_COLLECTION)

    # Load embedding model
    embedding_model = SentenceTransformer(embed_model)
    query_embedding = embedding_model.encode([user_query])[0]

    # Query the collection
    results = collection.query(query_embeddings=[query_embedding], n_results=top_k)

    replies = []
    if results["documents"] is not None:
        for i in range(len(results["documents"][0])):
            context = results["documents"][0][i]
            replies.append(context)
    return replies


def generate_answer(user_query: str, context: list[str]) -> str:
    # context_doc = "\n".join(context)
    prompt = f"""
    คุณเป็นผู้ช่วยที่สามารถให้คำแนะนำเกี่ยวกับการแพทย์ได้โดยอิงจาก context ที่มีให้แล้วนำมาวิเคราะห์โดยอิงจากข้อความให้มากที่สุด.
    **สำคัญ**: ตอนตอบกลับ ให้ตอบราวกับเป็นคำตอบตรงประเด็นจากผู้ช่วยทางการแพทย์ในระบบสนทนา ถ้าสามารถให้คำแนะนำได้ให้ทำเลยโดยอิงจากข้อมูลที่มีให้ใน context.
    Context: {context}
    User's questiion: {user_query}
    """
    # response = models.generate_content(prompt)
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            max_output_tokens=500,
            system_instruction="คุณเป็นผู้ช่วยที่สามารถให้คำแนะนำเกี่ยวกับการแพทย์ได้",
            temperature=0.2,
        ),
    )

    return response.text or ""


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "สามารถสอบถามปัญหาสุขภาพได้เลย! 👇"}
    ]

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        with st.spinner("Wait for it...", show_time=True):
            context = retrieve_relevant_documents(
                user_query=prompt,
                embed_model=EMBED_MODEL,
                persist_path=PERSIST_PATH,
            )
            assistant_response = generate_answer(prompt, context)

        # Simulate stream of response with milliseconds delay
        for chunk in assistant_response.split():
            full_response += chunk + " "
            time.sleep(0.05)
            message_placeholder.markdown(
                full_response + "▌"
            )  # Add a blinking cursor to simulate typing

        message_placeholder.markdown(full_response)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})
