import os
import streamlit as st
import time
from dotenv import load_dotenv, find_dotenv
from langchain.utilities import SQLDatabase
load_dotenv(find_dotenv(), override=True)
from langchain.llms import OpenAI
from langchain_experimental.sql import SQLDatabaseChain


# @st.cache_resource
def db_loader(file):
    name, extension = os.path.splitext(file)

    if extension == '.db':
        print("Creating engine")
        db = SQLDatabase.from_uri(f'sqlite:///{file}')
        print("Engine Created!")

    return db

def format_intermediate_steps(intermediate_steps):
    import re
    
    #regular expression splitting parameteres
    parameters = "[' '\n:]"
    #split
    reg_result = re.split(parameters, intermediate_steps)
    return reg_result

def extract_sql_query(sqlquery_str):
        
    #extract sql query from intermediate steps
    sql_query_start_index = sqlquery_str.index('SQLQuery')
    sql_query_end_index = sqlquery_str.index('SQLResult')
    # Slice the string
    sql_query = ' '.join(sqlquery_str[sql_query_start_index + 1:sql_query_end_index])

    return sql_query

def extract_sql_result(sqlresult_str):
        
    #extract tuple/list from intermediate steps to form tables if needed
    sql_result_start_index = sqlresult_str.find('SQLResult:') + len('SQLResult:')
    sql_result_end_index = sqlresult_str.find('\nAnswer:')
    # Slice the string
    sql_result = sqlresult_str[sql_result_start_index:sql_result_end_index]
    # Remove leading and trailing whitespaces and newlines
    sql_result = sql_result.strip()
        
    return sql_result

def create_dataframe(element_str):
    import pandas as pd
    import ast

    #String to list conversion
    converted_list = ast.literal_eval(element_str)
    #list to dataframe
    df = pd.DataFrame(converted_list)
    return df

#@st.cache_data
def query_answer(data, q):

    if isinstance(data, SQLDatabase):
        
        llm = OpenAI(model_name="text-davinci-003", temperature=0)
        db_chain = SQLDatabaseChain.from_llm(llm=llm, db=data, use_query_checker=True, return_intermediate_steps=True)
        results = db_chain(q)
        final_answer = results['result']
        
        #intermediate steps
        intermediate_steps = results['intermediate_steps'][0]['input']
        
        reg_result = format_intermediate_steps(intermediate_steps)
        sql_query = extract_sql_query(reg_result)
        sql_result = extract_sql_result(intermediate_steps)
        gen_dataframe = create_dataframe(sql_result)

        return final_answer, sql_query, gen_dataframe

def refresh_page():
    """
    This function triggers a page refresh and clears the uploaded file.
    """
    st.session_state.clear()
    
    st.rerun()



st.header("Query your database using Natural Language :panda_face:")
st.divider()
with st.sidebar:
    uploaded_file = st.file_uploader(label="Upload your database",
                        type=['db'])
    # add_data = st.button('New Database')

    
if uploaded_file:
    with st.spinner("New file loading......"):
        
        bytes_data = uploaded_file.read()
        file_name = os.path.join('./', uploaded_file.name)
        with open(file_name, 'wb') as f:
            f.write(bytes_data)
        
        db_data = db_loader(file_name)
        st.session_state.new_db = db_data
        st.sidebar.success('File Loaded')


q = st.text_input('What would you like to ask from the database?', key='q', value=st.session_state.get('q'))
# st.write(st.session_state.new_db)
if q:
    db_data = st.session_state.new_db
    final_answer, sql_query, frame = query_answer(db_data, q)
    # st.write(frame)
    if st.button('Reset'):
        refresh_page()

    # run_button = st.button("Run", on_click=answer)
    st.text_area('Answer', value = final_answer)
    st.text_area('SQL query:', value = sql_query)
    st.dataframe(frame)

st.sidebar.markdown('''
# App Information
This app is currently in beta mode and is a work in progress. Expect updates and improvements as we refine its features and functionality.

**App Owner:** Ankur Kumar
\nContact the owner for questions and feedback:
- Email: ankvis21@outlook.com
- LinkedIn: https://www.linkedin.com/in/ankur21/
''')