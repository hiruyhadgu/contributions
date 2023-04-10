import streamlit as st
import pandas as pd
import plotly.express as px
from modules.functions import group_by_filing_period
from modules.db_load import load, developer
import re



## Load all tables
raw_table = load()

@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

excluded_columns = ['Filing Period', 'Office', 'Fundtype', 'Candidate Name', 'Councilmanic District']

st.markdown('### Search the database of campagin donors')
text_input = st.text_input('Enter name here:', placeholder='enter as last name, first name')
if len(text_input)>0:
    search_database = raw_table['Contributor Name'].str.contains(text_input,case=False, na=False)
    results = raw_table[search_database]
    to_display = results.loc[:,~results.columns.isin(excluded_columns)]
    st.write(to_display.sort_values(by='Contribution Date').reset_index().drop(columns = 'index'))
    csv = convert_df(to_display)
    st.download_button('Download as CSV', csv, file_name=f'{text_input}_contribution_info.csv', mime = 'text/csv')

st.markdown('----')

st.markdown('### Explore pre-defined table summaries by selecting from the options below.')

councilmanic_list = raw_table['Councilmanic District'].unique().tolist()
councilmanic_list.insert(0, 'All')
district_options= st.sidebar.selectbox('Councilmanic District', councilmanic_list)
if district_options =='All':
    filtered_by_district = raw_table
else:
    mask = raw_table['Councilmanic District'] == district_options
    filtered_by_district = raw_table[mask]

office_options = st.sidebar.selectbox('Office', raw_table['Office'].unique())
mask1 = raw_table['Office']==office_options
filtered_by_office = raw_table[mask1]

def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]

table_description = ['Contribution Summaries by Filing Period in Each Councilmanic District',\
                      'Contribution Summaries by Filing Period for Each Candidate',\
                        'Total Raised by Each Candidate thru All Filing Periods',\
                            'Total Raised by Each Candidate by Office']
table_summary = {}

def tables():
    # group by district and filing period
    district_filing_period = group_by_filing_period(filtered_by_district, ['Filing Period', 'Councilmanic District'])
    district_filing_period = district_filing_period.unstack()
    district_filing_period.columns = district_filing_period.columns.droplevel(0)
    table_summary[table_description[0]]=district_filing_period

    # group by candidate name and filing period
    candidate_filing_period = group_by_filing_period(raw_table, ['Filing Period', 'Candidate Name'])
    candidate_filing_period = candidate_filing_period.unstack()
    candidate_filing_period.columns = candidate_filing_period.columns.droplevel(0)
    table_summary[table_description[1]]=candidate_filing_period

    # group by candidate name
    candidate_name = group_by_filing_period(raw_table, ['Candidate Name'])
    table_summary[table_description[2]]=candidate_name

    # group by candidate name and district
    candidate_councilmanic = group_by_filing_period(filtered_by_office, ['Candidate Name','Councilmanic District'])
    candidate_councilmanic = candidate_councilmanic.unstack()
    candidate_councilmanic.columns = candidate_councilmanic.columns.droplevel(0)
    table_summary[table_description[3]]=candidate_councilmanic

    return table_summary

select_table = st.selectbox('View Summary',table_description)
if select_table:
    st.write(tables()[select_table].style.format('$ {:,.2f}'))

st.markdown('----')
st.markdown('### Use the "View Tables" option on the sidebar to select and view your own custom summaries.')
groupby = st.sidebar.multiselect('View Table:', raw_table.columns, None)

if groupby:
    new_table = group_by_filing_period(raw_table, groupby)
    st.write(new_table.style.format('$ {:,.2f}'))

st.markdown('---')
developer_list = developer()

developer_analysis = st.sidebar.checkbox('Show Developer Contributions')
st.markdown("### Select the 'show developer contributions' to examine developer contribution data")

if developer_analysis:
    developer_verify = developer_list['Developer/Developer Affiliated'].isin(['yes','Yes', 'YES'])
    developer_list = developer_list[developer_verify]
    developer_mask = raw_table['Contributor Name'].str.lower().isin([d.lower() for d in developer_list['Contributor Name']])
    excluded_columns.remove('Candidate Name')
    excluded_columns.insert(0, 'Receiving Committee')
    to_display1 = raw_table[developer_mask].loc[:,~raw_table[developer_mask].columns.isin(excluded_columns)]
    display_cols = to_display1.columns.tolist()
    display_cols = display_cols[-1:] + display_cols[:-1]
    to_display1 = to_display1[mask1].sort_values(by='Contribution Date').reset_index().drop(columns = 'index')
    st.dataframe(to_display1[display_cols])

    developers = group_by_filing_period(raw_table[developer_mask],['Candidate Name'])
    contributor_name = group_by_filing_period(raw_table[developer_mask],['Contributor Name'])
    # developers['Contribution Amount']=developers['Contribution Amount'])
    st.dataframe(developers.style.format('$ {:,.2f}'))
    st.dataframe(contributor_name.style.format('$ {:,.2f}'))
