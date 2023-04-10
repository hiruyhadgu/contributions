import pandas as pd
import sqlite3 as db
import datetime as dt
import streamlit as st

conn = db.connect('contributions.db', check_same_thread=False)
c = conn.cursor()
sql_query = """SELECT name FROM sqlite_master
WHERE type='table';"""
    
# executing our sql query
c.execute(sql_query)
    
# printing all tables list
list = c.fetchall()

list.remove(('developercrossreference',))

def contributions(name):
    table = pd.read_sql_query(f'select * from {name}',conn)
    table['Contribution Date'] = pd.to_datetime(table['Contribution Date']).dt.date
    table['Contribution Amount'] = table['Contribution Amount'].astype(float)
    table = table.drop(columns='index')
    return table

candidate_data_frame = {}

@st.cache_data
def load():
    raw_table = pd.DataFrame()
    for n in list:
        raw_table = pd.concat([raw_table, contributions(n[0])])
        raw_table = raw_table.reset_index().drop(columns='index')
    return raw_table
@st.cache_data
def developer():
    table1 = pd.read_sql_query(f'select * from developercrossreference',conn)
    table1 = table1.drop(columns='index')
    return table1