import psycopg2
import pandas as pd
import numpy as np

conn = psycopg2.connect(
            host="localhost",
            user="postgres",
            password="postgres",
            port="5432",
            dbname='imdb'
        )
conn.autocommit = False 
cur = conn.cursor()

df = pd.read_csv("movies.csv")

for _, row in df.iterrows():
    cur.execute(
        "INSERT INTO movies (mov_id, mov_details, embedding) VALUES (%s, %s, NULL)",
        (row['mov_id'], row['mov_details'])
    )

conn.commit()
cur.close()
conn.close()

