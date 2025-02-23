import os
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database connection parameters from environment variables
db_params = {
    "dbname": os.getenv("DB_NAME", "default_dbname"),
    "user": os.getenv("DB_USER", "default_user"),
    "password": os.getenv("DB_PASSWORD", "default_password"),
    "host": os.getenv("DB_HOST", "default_host"),
    "port": os.getenv("DB_PORT", "default_port"),
}

# Ensure all required environment variables are set
for key, value in db_params.items():
    if value is None:
        raise ValueError(f"Environment variable for {key} is not set.")

# SQL statement to create the table

create_table_query = """
        CREATE TABLE IF NOT EXISTS progresos_respaldo (
            id SERIAL PRIMARY KEY,
            colaboradora TEXT,
            identificador_sujetosObligados TEXT,
            sujetosObligado TEXT,
            identificador_obligacionesTransparencia TEXT,
            obligacionesTransparencia TEXT,
            index_actual INTEGER,
            data JSONB,
            hash_key TEXT UNIQUE,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """


# Create the table
def create_db():

    try:
        conn = psycopg2.connect(
            dbname=db_params["dbname"],
            user=db_params["user"],
            password=db_params["password"],
            host=db_params["host"],
            port=db_params["port"],
        )
        cursor = conn.cursor()

        cursor.execute(create_table_query)

        conn.commit()
        cursor.close()
        conn.close()

        print("Table created successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")


# Insert data into the table
def insert_db(data_to_insert):
    try:
        conn = psycopg2.connect(
            dbname=db_params["dbname"],
            user=db_params["user"],
            password=db_params["password"],
            host=db_params["host"],
            port=db_params["port"],
        )
        cursor = conn.cursor()

        insert_query = sql.SQL(
            """INSERT INTO progresos_respaldo (
            colaboradora,
            identificador_sujetosObligados,
            sujetosObligado,
            identificador_obligacionesTransparencia,         
            obligacionesTransparencia,
            index_actual,
            data,
            hash_key ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
        )

        cursor.execute(insert_query, data_to_insert)
        conn.commit()
        cursor.close()
        conn.close()

        print("Data inserted successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")


def select_db(select_query):
    hash_key_value = None
    try:
        conn = psycopg2.connect(
            dbname=db_params["dbname"],
            user=db_params["user"],
            password=db_params["password"],
            host=db_params["host"],
            port=db_params["port"],
        )
        cursor = conn.cursor()

        cursor.execute(select_query)

        hash_key = cursor.fetchone()

        if hash_key:
            hash_key_value = hash_key[0]
            conn.commit()
            cursor.close()
            conn.close()
            return hash_key_value
        else:
            print("No hash_key found for the given criteria.")
            return hash_key_value

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")
        return hash_key_value
