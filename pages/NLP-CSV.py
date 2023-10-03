import streamlit as st
import os
import pandas as pd
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(), override=True)

from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.agents.agent_types import AgentType
from langchain.agents import create_csv_agent

#@st.cache_data
def csv_agent(file, query):

    agent = create_csv_agent(
        OpenAI(temperature=0),
        path=file,
        verbose=True,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        return_intermediate_steps=True
    )

    response = agent(
        {
            "input" : query
        }
        )

    final_answer = response['output']
    pandas_code = response['intermediate_steps'][0][0].tool_input
    output = response['intermediate_steps'][0][1]
    
    return final_answer, pandas_code, output

def refresh_page():
    """
    This function triggers a page refresh and clears the uploaded file.
    """
    st.session_state.clear() 
    st.rerun()

st.header('Query your excel sheet using Natural Language :polar_bear:')
st.divider() 
uploaded_file = st.sidebar.file_uploader('Upload a CSV file', type=['csv'])

if uploaded_file:
    with st.spinner('Loading File'):
        bytes_data = uploaded_file.read()
        file_name = os.path.join('./', uploaded_file.name)
        with open(file_name,'wb') as f:
            f.write(bytes_data)

    
    st.session_state.csv = file_name
    st.sidebar.success('File Loaded')
    

q = st.text_input('Ask your question from the csv data', key='q', value=st.session_state.get('q'))
if q:
    file = st.session_state.csv
    final_answer,pandas_code,output = csv_agent(file, q)
    
    if st.button('Reset'):
        refresh_page()  
    
    
    st.text_area('LLM answer: ', value= final_answer)
    st.text_area('Pandas query used: ', value = pandas_code)
    st.divider()
    
    if isinstance(output, (pd.Series, pd.DataFrame)):
        st.dataframe(output)
    else:
        st.text_area('output query: ', value = output)
    #st.text_area('output query: ', value = output)
  
 

st.sidebar.markdown('''
# App Information
This app is currently in beta mode and is a work in progress. Expect updates and improvements as we refine its features and functionality.

**App Owner:** Ankur Kumar
\nContact the owner for questions and feedback:
- Email: ankvis21@outlook.com
- LinkedIn: https://www.linkedin.com/in/ankur21/
''')

