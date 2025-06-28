import psycopg2
from sentence_transformers import SentenceTransformer
import numpy as np
from pgvector.psycopg2 import register_vector
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_core.prompts import ChatPromptTemplate
import os
import json
from langchain_openai import ChatOpenAI


with open("api_key.json", "r") as fi:
    api_key = json.load(fi)['api_key']

os.environ["OPENAI_API_KEY"] = api_key
os.environ["OPENAI_API_BASE"] = "https://openrouter.ai/api/v1"

question = "Suggest movies like intersteller"
embedder = SentenceTransformer('all-MiniLM-L6-v2')

conn = psycopg2.connect(
            host="localhost",
            user="postgres",
            password="postgres",
            port="5432",
            dbname='imdb'
        )
conn.autocommit = False 
register_vector(conn)
cur = conn.cursor()

query_embedding = embedder.encode(question)
embedding_array = query_embedding
cur.execute("""
    SELECT mov_details, 1 - (embedding <=> %s) AS similarity
    FROM movies
    ORDER BY similarity DESC
    LIMIT 50;
    """, (embedding_array,))

rows = cur.fetchall()

context = ''
for row in rows:
    print(f" Match {row[0]}\n Similarity: {row[1]}")
    #print(f"{row[0]}")
    print("\n")
    context = context + row[0]

#print(f"\n\nContext: {context}")
cur.close()
conn.close()

  # template for the prompt
template = """
    You are a movie assistant.
    If the information is not available in the context, return "I am sorry, I don't have enough information about it".
    If the context doesn't have enough information, do not add your known information.
    Do not say "based on the context", answer in natural language.
    You have to understand the context provided and answer specific to the question. The context contains multiple movies.

    Use bullet points when listing multiple movies or cast members.
    question: {question}
    context: {context}
    Answer: 
    """
prompt_template = ChatPromptTemplate.from_template(template)

prompt = prompt_template.invoke({"context": context,"question": question,})
#model = ChatOllama(model="deepseek-r1")
#response = model.invoke(prompt)
#print(f"response: {response.content}")

llm = ChatOpenAI(
    base_url="https://openrouter.ai/api/v1",
    #model_name="meta-llama/llama-4-scout:free",
    model_name="deepseek/deepseek-chat:free",
    openai_api_key=api_key,
    max_tokens = 58000
)

# invoke the LLM to get the response
response = llm.invoke(prompt)

# read only the answer from the response
print(response.content)