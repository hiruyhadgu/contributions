import streamlit as st
import pandas as pd
import sqlite3 as db
import plotly.express as px
import datetime as dt

st.markdown('### Fundraising data for all candidates for county council and county executive since 2006.')

conn = db.connect('contributions.db', check_same_thread=False)
sqlite_select_query = """SELECT name FROM sqlite_master WHERE type='table';"""
c = conn.cursor()
c.execute(sqlite_select_query)
records = c.fetchall()

def contributions(name):
    table = pd.read_sql_query(f'select * from {name}',conn)
    table['Contribution Date'] = pd.to_datetime(table['Contribution Date']).dt.date
    table['Contribution Amount'] = table['Contribution Amount'].astype(float)
    table = table.drop(columns='index')
    return table

candidate_data_frame = {}

def load():
    raw_table = pd.DataFrame()
    for n in records:
        if n[0] == 'developercrossreference':
            continue
        raw_table = pd.concat([raw_table, contributions(n[0])])
        raw_table = raw_table.reset_index().drop(columns='index')
    return raw_table

raw_table = load()

office_options = st.sidebar.selectbox('Office', raw_table['Office'].unique())
mask = raw_table['Office']==office_options
filtered_by_office = raw_table[mask]

district_options= st.sidebar.selectbox('Councilmanic District', filtered_by_office['Councilmanic District'].unique())
mask1 = filtered_by_office['Councilmanic District'] == district_options
filtered_by_district = filtered_by_office[mask1]


name_options = st.sidebar.selectbox('Candidate Name', filtered_by_district['Candidate Name'].unique())
mask2 = filtered_by_district['Candidate Name'] == name_options

filtered_by_name = filtered_by_district[mask2]

start_date = filtered_by_name['Contribution Date'].min()
end_date = filtered_by_name['Contribution Date'].max()
value = [start_date, end_date]

val = st.date_input(label='Date Range: ', value=value, help="The start and end date time")

try:
    start_date, end_date = val
except ValueError:
    st.error("You must pick a start and end date")
    st.stop()

mask3 = (filtered_by_name['Contribution Date']>=val[0]) & (filtered_by_name['Contribution Date'] <=val[1])
filtered_by_date = filtered_by_name[mask3]
filtered_by_date = filtered_by_date.sort_values(['Receiving Committee','Contribution Date']).reset_index().drop(columns='index')

filing_options = filtered_by_date['Filing Period'].unique().tolist()
filing_options.insert(0, 'All Filing Periods')

select_filing_period = st.selectbox('Select Filing Period',options=filing_options)

if select_filing_period =='All Filing Periods':
    filtered_by_filing_period = filtered_by_date
else:
    mask4 = filtered_by_date['Filing Period']==select_filing_period
    filtered_by_filing_period = filtered_by_date[mask4]

# Filter the dataframe based on the selected date range and categories

candidate_options = filtered_by_filing_period['Receiving Committee'].unique()
select_candidates = st.multiselect('Select Campaign Committees',options=candidate_options, default=candidate_options)
mask5 = filtered_by_date['Receiving Committee'].isin(select_candidates)

filtered_by_candidate = filtered_by_filing_period[mask5] 
col1, col2 = st.columns(2)

with col1:
    st.metric('Total Number of Contributions:',filtered_by_candidate['Contribution Amount'].count())

with col2:
    st.metric('Total Money Raised:','${:,.2f}'.format(filtered_by_candidate['Contribution Amount'].sum()))


excluded_row = ['Receiving Committee', 'Filing Period','Office','Fundtype','Candidate Name', 'Councilmanic District']
# Display the filtered dataframe
st.write(filtered_by_candidate.loc[:,~filtered_by_candidate.columns.isin(excluded_row)])

st.markdown("""
<style>
div[data-testid="metric-container"] {
   background-color: rgba(28, 131, 225, 0.1);
   border: 1px solid rgba(28, 131, 225, 0.1);
   padding: 5% 5% 5% 10%;
   border-radius: 5px;
   color: rgb(30, 103, 119);
   overflow-wrap: break-word;
}

/* breakline for metric text         */
div[data-testid="metric-container"] > label[data-testid="stMetricLabel"] > div {
   overflow-wrap: break-word;
   white-space: break-spaces;
   color: red; font-size: 200% !important;
}
</style>
"""
, unsafe_allow_html=True)