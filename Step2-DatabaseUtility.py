import psycopg2

def create_database(db_name, db_user, db_password, db_host, db_port):
    conn = None
    try:
        # Connect to the PostgreSQL server
        conn = psycopg2.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            port=db_port
            #dbname=db_name 
        )
        conn.autocommit = True # Set autocommit to True to commit changes immediately
        cur = conn.cursor()

        # Check if the database already exists
        cur.execute(f"SELECT 1 FROM pg_database WHERE datname='{db_name}'")
        exists = cur.fetchone()

        if not exists:
            # Create the new database
            cur.execute(f"CREATE DATABASE {db_name}")
            print(f"Database '{db_name}' created successfully.")
        else:
            print(f"Database '{db_name}' already exists.")

        cur.close()

        conn = psycopg2.connect(
            database=db_name, user=db_user, password=db_password, host=db_host, port=db_port
        )
        conn.autocommit = True  # Enable autocommit for extension creation
        cur = conn.cursor()
        # Check if vector extension exists
        cur.execute("SELECT 1 FROM pg_extension WHERE extname='vector'")
        vector_exists = cur.fetchone()
        if not vector_exists:
            cur.execute("CREATE EXTENSION vector")
            print("Vector extension enabled successfully.")
        else:
            print("Vector extension already enabled.")
        
        # Check if table exists
        cur.execute("select * from pg_tables where tableowner = 'postgres' and schemaname='public' and tablename = 'movies'")
        movies_exists = cur.fetchone()
        if not movies_exists:
            print("Creating movies table...")
            create_table_query = """
            CREATE TABLE IF NOT EXISTS movies (
                mov_id VARCHAR(25) PRIMARY KEY,
                mov_details TEXT,
                embedding VECTOR(384)
            );
            """
            cur.execute(create_table_query)
            print("Movies table created successfully.")
        else:
            print("Movies table Already Exists! Deleting existing records..")
            cur.execute("SELECT COUNT(*) FROM movies;")
            total_rows = cur.fetchone()[0]
            cur.execute("DELETE FROM movies")
            print(f"Deleted {total_rows} rows from movies table.")
        
        print("\n Database Setup completed successfully!")

        cur.close()
        conn.close()

    except psycopg2.Error as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    db_name = "imdb" # Name of the database to be created
    db_user = "postgres" # Username to connect to PostgreSQL
    db_password = "postgres" # Password for the user
    db_host = "localhost" # Host address of the PostgreSQL server
    db_port = "5432" # Port number of the PostgreSQL server

    create_database(db_name, db_user, db_password, db_host, db_port)