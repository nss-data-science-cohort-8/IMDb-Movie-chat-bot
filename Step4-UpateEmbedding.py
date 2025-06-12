import psycopg2
from sentence_transformers import SentenceTransformer
import pandas as pd

conn = psycopg2.connect(
            host="localhost",
            user="postgres",
            password="postgres",
            port="5432",
            dbname='imdb'
        )
conn.autocommit = False 
cur = conn.cursor()

query = "SELECT mov_id, mov_details FROM movies WHERE embedding IS NULL"

df = pd.read_sql(query, conn)

cur.close()

cur = conn.cursor()
embedder = SentenceTransformer('all-MiniLM-L6-v2')

for _, row in df.iterrows():
    embedding = embedder.encode(row['mov_details']).tolist()
    cur.execute(
        "UPDATE movies set embedding = %s WHERE mov_id = %s",
        (embedding, row['mov_id'])
    )
cur.close()
conn.commit()
conn.close()

