from openai import OpenAI
import streamlit as st
import json
import os
import psycopg2
from sentence_transformers import SentenceTransformer
import numpy as np
from pgvector.psycopg2 import register_vector
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_core.prompts import ChatPromptTemplate
import os
import json
from langchain_openai import ChatOpenAI
from langchain_deepseek import ChatDeepSeek
from langchain_ollama import ChatOllama


with open("api_key.json", "r") as fi:
    api_key = json.load(fi)['api_key']

os.environ["OPENAI_API_KEY"] = api_key
os.environ["OPENAI_API_BASE"] = "https://openrouter.ai/api/v1"

embedder = SentenceTransformer('all-MiniLM-L6-v2')

def getDBConnection():

    conn = psycopg2.connect(
        host="localhost",
        user="postgres",
        password="postgres",
        port="5432",
        dbname='imdb'
    )

    register_vector(conn)
    return conn

def getEmbedding(query):
    return embedder.encode(query).tolist()

def generateResponse(question,llm):
    conn = getDBConnection()

    llm = getALLM(llm)

    cur = conn.cursor()
    cur.execute("""
    SELECT mov_details, 1 - (embedding <=> %s::vector) AS similarity
    FROM movies
    ORDER BY similarity DESC
    LIMIT 10;
    """, (getEmbedding(question),))

    rows = cur.fetchall()

    context = ''
    for row in rows:
        context = context + row[0]

    cur.close()
    conn.close()

    template = """
    You are a movie assistant.
    If the information is not available in the context, return "I am sorry, I don't have enough information about it".
    If the context doesn't have enough information, do not add your known information.
    Do not say "based on the context", answer in natural language.
    You have to understand the context provided and answer specific to the question. The context contains multiple movies.
    In the IMDb system, a blockbuster movie is one that has an IMDb rating above 8.5 and more than 1 million votes. Ratings are from 1 to 10
    question: {question}
    context: {context}
    Answer: 
    """

    prompt_template = ChatPromptTemplate.from_template(template)

    prompt = prompt_template.invoke({"context": context,"question": question,})

    # invoke the LLM to get the response
    response = llm.invoke(prompt)

    return response.content


def getALLM(llm):
    if llm == "deepseek":           
        llm = ChatDeepSeek(
            model="deepseek-r1"
        )
    
    if llm == "llama":           
        llm = ChatOllama(
            model="llama3.2",
            base_url="http://localhost:11434"
        )
    
    if llm == "openAI - Free":           
        llm = ChatOpenAI(
            base_url="https://openrouter.ai/api/v1",
            #model_name="meta-llama/llama-4-scout:free",
            #model_name="meta-llama/llama-4-maverick:free",
            #model_name="google/gemini-2.0-flash-exp:free",
            model_name ="mistralai/mistral-small-3.1-24b-instruct:free",
            openai_api_key=api_key,
            #max_tokens=56000  
        )
    
    return llm


with st.sidebar:

    optionLLM = st.selectbox(
        "LLM:",
        ("deepseek", "openAI - Free","llama"),
        index=None,
        placeholder="Select LLM"
    )

    #st.markdown("---")

    expander = st.expander("About this App")
    expander.write('''
        This application allows you to **semantically search movies and actors/directors** 
        based on your natural language query.

        ✨ Powered by:
        - Local **PostgreSQL**
        - **pgvector** extension
        - **Sentence Transformer** for embeddings
        - **OpenAI** LLM models (**meta-llama/llama-4-scout:free**) for natural answers
        - **Streamlit** for the web app

        **Main Features:**
        - Semantic search movies or people (actors/directors)
        - Natural language responses using Open AI LLM

        _**Built by** Nitin Pawar_
    ''')

    st.markdown("---")
    st.markdown("""
    **Connect Me:**
    """)
    st.markdown("[GitHub](https://github.com/ndpawar1981/IMDb-Movie-chat-bot)")
    st.markdown("[LinkedIn](https://linkedin.com/in/nitin-pawar-ds)")

st.image("./imdb.jpeg", use_container_width=True, caption="Welcome to IMDb Movies!")

st.title("Let's Chat")
#st.markdown("Ask me: about movies or actors*")


if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Refer - https://docs.streamlit.io/develop/tutorials/chat-and-llm-apps/build-conversational-apps
# React to user input
if user_input := st.chat_input("Interested in movies or people, ask here!"):

    # Display user message in chat message container    
    with st.chat_message("user"):
        st.markdown(user_input)

    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    response = generateResponse(user_input,optionLLM)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})