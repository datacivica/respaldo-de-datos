import os
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database connection parameters from environment variables
db_params = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
}

# SQL statement to create the table

create_table_query = """
        CREATE TABLE IF NOT EXISTS progresos_respaldo (
            id SERIAL PRIMARY KEY,
            colaboradora VARCHAR(150),
            identificador_sujetosObligados VARCHAR(255),
            sujetosObligado VARCHAR(255),
            identificador_organosGarantes VARCHAR(255),
            organosGarantes VARCHAR(255),
            identificador_obligacionesTransparencia VARCHAR(255),
            obligacionesTransparencia VARCHAR(255),
            index_actual INTEGER,
            index_final INTEGER,
            data JSONB,
            hash_key TEXT UNIQUE,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """


# Create the table
def create_db():

    try:
        conn = psycopg2.connect(**db_params)
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
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()

        insert_query = sql.SQL(
            """INSERT INTO progresos_respaldo (colaboradora,
            identificador_sujetosObligados,
            sujetosObligado,
            identificador_organosGarantes,
            organosGarantes,
            identificador_obligacionesTransparencia,         
            obligacionesTransparencia,
            index_actual,
            index_final,
            data,
            hash_key ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
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
        conn = psycopg2.connect(**db_params)
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
