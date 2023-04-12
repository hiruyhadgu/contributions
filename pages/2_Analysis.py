import streamlit as st
import pandas as pd
import plotly.express as px
from modules.functions import group_by_filing_period, summary_tables
from modules.db_load import Database, Tables, Table
import re

## Load all tables
db = Database('pages/contributions.db')
tables = Tables(db).fetch_list()
unpacked_tables = [t[0] for t in tables]

table = Table(unpacked_tables, db)
raw_table = table.fetch_all()

@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

excluded_columns = ['FilingPeriod', 'Office', 'Fundtype', 'CandidateName', 'CouncilmanicDistrict']

st.markdown('### Search the database of campaign donors')
text_input = st.text_input('Enter name here:', placeholder='enter as last name, first name')

if len(text_input)>0:
    search_database = raw_table['ContributorName'].str.contains(text_input,case=False, na=False)
    results = raw_table[search_database]
    to_display = results.loc[:,~results.columns.isin(excluded_columns)]
    to_display = to_display.sort_values(by='ContributionDate').reset_index().drop(columns = 'index')
    st.write(to_display.sort_values(by='ContributionDate').reset_index().drop(columns = 'index'))
    csv = convert_df(to_display)
elif len(text_input)<=0:
    st.write('Enter a valid name as lastname, firstname, then press enter.')
    csv = ''


st.download_button('Download as CSV', csv, file_name=f'{text_input}_contribution_info.csv', mime = 'text/csv')

st.markdown('----')

st.markdown('### Explore pre-defined table summaries by selecting from the options below.')

councilmanic_list = raw_table['CouncilmanicDistrict'].unique().tolist()
councilmanic_list.insert(0, 'All')
district_options= st.sidebar.selectbox('CouncilmanicDistrict', councilmanic_list)
if district_options =='All':
    filtered_by_district = raw_table
else:
    mask = raw_table['CouncilmanicDistrict'] == district_options
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

table_summary[table_description[0]] = summary_tables(filtered_by_district, ['FilingPeriod', 'CouncilmanicDistrict'])
table_summary[table_description[1]] = summary_tables(raw_table, ['FilingPeriod', 'CandidateName'])
table_summary[table_description[2]] = group_by_filing_period(raw_table, ['CandidateName'])
table_summary[table_description[3]] = summary_tables(filtered_by_office, ['CandidateName','CouncilmanicDistrict'])

select_table = st.selectbox('View Summary',table_description)
if select_table:
    st.write(table_summary[select_table].style.format('$ {:,.2f}'))

st.markdown('----')
st.markdown('### Use the "View Tables" option on the sidebar to select and view your own custom summaries.')
groupby = st.sidebar.multiselect('View Table:', raw_table.columns, None)

if groupby:
    new_table = group_by_filing_period(raw_table, groupby)
    st.write(new_table.style.format('$ {:,.2f}'))

st.markdown('---')
table1 = Table('developercrossreference', db)
developer_list = table1.fetch_reference()

developer_analysis = st.sidebar.checkbox('Show Developer Contributions')
st.markdown("### Select the 'show developer contributions' to examine developer contribution data")

if developer_analysis:
    developer_verify = developer_list['DeveloperOrDeveloperAffiliated'].isin(['yes','Yes', 'YES'])
    developer_list = developer_list[developer_verify]
    developer_mask = raw_table['ContributorName'].str.lower().isin([d.lower() for d in developer_list['ContributorName']])
    excluded_columns.remove('CandidateName')
    excluded_columns.insert(0, 'ReceivingCommittee')
    to_display1 = raw_table[developer_mask].loc[:,~raw_table[developer_mask].columns.isin(excluded_columns)]
    display_cols = to_display1.columns.tolist()
    display_cols = display_cols[-1:] + display_cols[:-1]
    to_display1 = to_display1[mask1].sort_values(by='ContributionDate').reset_index().drop(columns = 'index')
    st.dataframe(to_display1[display_cols])

    developers = group_by_filing_period(raw_table[developer_mask],['CandidateName'])
    contributor_name = group_by_filing_period(raw_table[developer_mask],['ContributorName'])
  
    col1, col2 = st.columns(2)
    with col1:
        st.dataframe(developers.style.format('$ {:,.2f}'))
    
    with col2:
        st.dataframe(contributor_name.style.format('$ {:,.2f}'))