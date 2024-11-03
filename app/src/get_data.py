import os
import psycopg2
import streamlit as st 
from dotenv import load_dotenv
from sqlalchemy import create_engine
import pandas as pd

load_dotenv()


def connect_to_db():
    # Create a database connection using SQLAlchemy
    DB_HOST = os.getenv("POSTGRES_HOST")
    DB_PORT = os.getenv("POSTGRES_PORT")
    DB_NAME = os.getenv("POSTGRES_DB")
    DB_USER = os.getenv("POSTGRES_USER")
    DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")

    connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(connection_string)
    return engine

@st.cache_data
def load_data()-> pd.DataFrame:
    engine = connect_to_db()
    query = "SELECT * FROM dw_lcs.solar_summary_processed"
    query2 = "SELECT * FROM dw_lcs.solar_energy_processed"
    
    # Load data into a DataFrame
    df = pd.read_sql(query, engine)
    
    df2 = pd.read_sql(query2, engine)
    
    engine.dispose()  # Close the connection when done
    
    df['prod_date'] = pd.to_datetime(df['prod_date'])
    df2['prod_datehour'] = pd.to_datetime(df2['prod_datehour'])
    
    return df, df2

def monthly_chart(df: pd.DataFrame)->pd.DataFrame:
    df1 = df.resample('M', on='prod_date').sum(numeric_only=True)
    return df1

def heat_map(df: pd.DataFrame)->pd.DataFrame:
    
    df.set_index('prod_date',inplace=True)
    df['day'] = df.index.day 
    df['month_year'] = df.index.to_period('M')
    
    df_pivot = df.pivot_table(values='total', index='day', columns='month_year', aggfunc='sum')
    
    return df_pivot


if __name__ == "__main__":
    data,data2 = load_data()
    # print(data.head())
    ht = heat_map(data)
    print(ht.head())