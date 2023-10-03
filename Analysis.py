import os
import streamlit as st
import pandas as pd
import plotly.express as px

st.header('Visualization Analysis :dog:', divider=True)

# Load CSV file if uploaded
def load_data(uploaded_file):
    try:
        df = pd.read_csv(uploaded_file, encoding='utf-8')
        st.session_state['frame'] = df
        return df
    except Exception as e:
        st.error(f"Error: Unable to read the CSV file. {e}")
        return None

# Display the DataFrame if uploaded
def display_dataframe(df):
    st.dataframe(df)
    numeric_data = list(df.select_dtypes(include=['float', 'int']).columns)
    categorical_data = list(df.select_dtypes(include=['object']).columns)
    return numeric_data, categorical_data

# Display a chart based on the selected chart type
def display_chart(chart_type, df, numeric_data, categorical_data):
    st.subheader(f'{chart_type} Plot')
    st.sidebar.subheader(f"{chart_type} settings")

    if chart_type == 'Histogram':
        x_values = st.sidebar.selectbox('X axis', options=numeric_data)
        try:
            chart = px.histogram(data_frame=df, x=x_values)
            st.plotly_chart(chart)
        except Exception as e:
            st.error(f"An error occurred: {e}")

    elif chart_type == 'Box plot':
        x_values = st.sidebar.selectbox('X axis', options=categorical_data)
        y_values = st.sidebar.selectbox('Y axis', options=numeric_data)
        color_choice = st.sidebar.checkbox('Color by Category', True)  # Checkbox for coloring

        try:
            if color_choice:
                color_column = st.sidebar.selectbox('Color by', options=categorical_data)
            else:
                color_column = None

            chart = px.box(data_frame=df, x=x_values, y=y_values, color=color_column,
                                    hover_data=df.columns)

            st.plotly_chart(chart)
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:  # Scatterplot and Lineplot
        x_values = st.sidebar.selectbox('X axis', options=numeric_data)
        y_values = st.sidebar.selectbox('Y axis', options=numeric_data)

        try:
            if chart_type == 'Scatterplot':
                chart = px.scatter(data_frame=df, x=x_values, y=y_values)
            else:  # Lineplot
                chart = px.line(data_frame=df, x=x_values, y=y_values)

            st.plotly_chart(chart)
        except Exception as e:
            st.error(f"An error occurred: {e}")

# Function to filter the data based on specific criteria
def filter_data_categorical(df, column, values):
    filtered_df = df[df[column].isin(values)]
    return filtered_df

def filter_data_numeric(df, column, threshold):
    filtered_df = df[df[column] > threshold]
    return filtered_df

def describe_data(dataframe, selected_columns):
    """
    Generates a summary report for the DataFrame.
    """
    summary = dataframe[selected_columns].describe()
    return summary

def refresh_page():
    """
    This function triggers a page refresh and clears the uploaded file.
    """
    st.session_state.clear()
    
    st.rerun()

def sort_data(df, columns, ascending=True):
    """
    Sorts the DataFrame based on specific columns (numerical only).
    """
    numerical_columns = df.select_dtypes(include=['float', 'int']).columns
    valid_columns = [col for col in columns if col in numerical_columns]
    if valid_columns:
        return df.sort_values(by=valid_columns, ascending=[ascending] * len(valid_columns))
    else:
        st.warning('No valid numerical columns selected for sorting.')
        return df


with st.sidebar:
    uploaded_file = st.file_uploader("Upload a CSV file", type=['csv'])
    if uploaded_file is not None:
        df = load_data(uploaded_file)

if 'frame' in st.session_state:
    df = st.session_state.frame
    numeric_data, categorical_data = display_dataframe(df)
    st.divider()
    st.sidebar.divider()

    if st.sidebar.button('Reset'):
        refresh_page()    
    
    chart_checkbox = st.sidebar.checkbox(':blue[Charts] :chart_with_upwards_trend:', key='chart_checkbox', value=st.session_state.get('chart_checkbox', False))
    if chart_checkbox:
        chart_select = st.sidebar.selectbox(
            label='Select a chart type',
            options=['Scatterplot', 'Lineplot', 'Histogram', 'Box plot']
        )
        # Display the selected chart based on the user's choice
        display_chart(chart_select, df, numeric_data, categorical_data)
        st.divider()

    # Allow data filtering for both numerical and categorical data
    filter_data_checkbox = st.sidebar.checkbox(':blue[Filter Data] :hammer_and_wrench:', key='filter_data_checkbox', value=st.session_state.get('filter_data_checkbox', False))
    if filter_data_checkbox:
        filter_type = st.sidebar.selectbox('Filter by Data Type', ['Numeric', 'Categorical'])

        if filter_type == 'Numeric':
            filter_column = st.sidebar.selectbox('Filter by Column (Numeric)', options=numeric_data)
            filter_threshold = st.sidebar.slider('Filter Threshold', min_value=df[filter_column].min(),
                                                max_value=df[filter_column].max())
            filtered_df = filter_data_numeric(df, filter_column, filter_threshold)
            st.subheader('Filtered Data (Numeric)')
            st.write(filtered_df)
            st.divider()
        else:
            filter_column = st.sidebar.selectbox('Filter by Column (Categorical)', options=categorical_data)
            selected_categories = st.sidebar.multiselect('Select Categories',
                                                         options=df[filter_column].unique())
            if selected_categories:
                filtered_df = filter_data_categorical(df, filter_column, selected_categories)
                st.subheader('Filtered Data (Categorical)')
                st.write(filtered_df)
                st.divider()

    describe_data_checkbox = st.sidebar.checkbox(':blue[Statistics]', key='describe_data_checkbox', value=st.session_state.get('describe_data_checkbox', False))
    if describe_data_checkbox:
        selected_columns = st.sidebar.multiselect('Select Columns for Summary Statistics', df.columns)
        if len(selected_columns) > 0:
            summary_report = describe_data(df, selected_columns)
            st.subheader('Summary Report')
            st.write(summary_report)
        else:
            st.warning('Please select columns for summary statistics.')
    
    
    sort_data_checkbox = st.sidebar.checkbox(':blue[Sort Data]', key='sort_data_checkbox', value=st.session_state.get('sort_data_checkbox', False))
    if sort_data_checkbox:
        sort_columns = st.sidebar.multiselect('Select Columns to Sort (Numerical)', options=numeric_data)
        ascending_order = st.sidebar.checkbox('Ascending Order', True)
        
        if sort_columns and ascending_order is not None:
            sorted_df = sort_data(df, sort_columns, ascending_order)
            st.subheader('Sorted Data')
            st.write(sorted_df)
            st.divider()

st.sidebar.markdown('''
# App Information
This app is currently in beta mode and is a work in progress. Expect updates and improvements as we refine its features and functionality.

**App Owner:** Ankur Kumar
\nContact the owner for questions and feedback:
- Email: ankvis21@outlook.com
- LinkedIn: (https://www.linkedin.com/in/ankur21/)
''')