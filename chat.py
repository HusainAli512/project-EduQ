
import streamlit as st
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
import os
from pinecone import Pinecone, ServerlessSpec
import google.generativeai as genai 


load_dotenv()
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")


embeddings = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))


book_options = {
    "Computer Science Book (9th Grade)": "cs9",
    "Biology Book (9th Grade)": "pdf-qa"
}


st.set_page_config(page_title="AI Summarization Tool", layout="centered", initial_sidebar_state="collapsed")


st.markdown("""
    <style>
    body {
        background-color: #000000;
        color: #ffffff;
    }
    .stTextInput input {
        background-color: #ffffff;
        color: #000000;
    }
    .stButton button {
        background-color: #4CAF50;
        color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)


st.title("Q/A Chatbot")


selected_book = st.selectbox("Select a Book", list(book_options.keys()))
selected_index = book_options[selected_book]  


index = pc.Index(selected_index)


query = st.text_input("Enter your query:", "")


def retrieve_answer(query):
    
    query_embedding = embeddings.embed_query(query)

    results = index.query(vector=query_embedding, top_k=5, include_metadata=True)  

    
    relevant_texts = []
    for match in results['matches']:
        if match['metadata'] and 'text' in match['metadata']:
            relevant_texts.append(match['metadata']['text'])
        else:
            print(f"ID: {match['id']} has no metadata or 'text' field.")

    return relevant_texts


def generate_answer(query):
    
    relevant_texts = retrieve_answer(query)
    
    if not relevant_texts:
        return "No relevant information found to generate an answer."
    
    
    context = "\n".join(relevant_texts)

    
    try:
        response = model.generate_content(
            f"Based on the following information (dont provide answer if the question is not related to text just say it is not present in text), answer the question:\n\n{context}\n\nQuestion: {query}"
        )
        return response.text  
    except Exception as e:
        return f"An error occurred while generating the answer: {str(e)}"

# Answer generation
if st.button("Generate Answer"):
    if query:
        with st.spinner("Generating answer..."):
            answer = generate_answer(query)
        st.write("Answer:", answer)
    else:
        st.warning("Please enter a query to generate an answer.")
