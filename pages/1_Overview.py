import streamlit as st
import pandas as pd
import sqlite3 as db
import plotly.express as px
import datetime as dt
from modules.db_load import Database, Tables, Table
st.markdown('### Fundraising data for all candidates for county council and county executive since 2006.')

db = Database('pages/contributions.db')
tables = Tables(db).fetch_list()
unpacked_tables = [t[0] for t in tables]
table = Table(unpacked_tables, db)
raw_table = table.fetch_all()

office_options = st.sidebar.selectbox('Office:', raw_table['Office'].unique())
mask = raw_table['Office']==office_options
filtered_by_office = raw_table[mask]

district_options= st.sidebar.selectbox('Councilmanic District:', filtered_by_office['CouncilmanicDistrict'].unique())
mask1 = filtered_by_office['CouncilmanicDistrict'] == district_options
filtered_by_district = filtered_by_office[mask1]

start_date = filtered_by_district['ContributionDate'].min()
end_date = filtered_by_district['ContributionDate'].max()
value = [start_date, end_date]

val = st.date_input(label='Date Range: ', value=value, help="The start and end date time")

try:
    start_date, end_date = val
except ValueError:
    st.error("You must pick a start and end date")
    st.stop()

mask3 = (filtered_by_district['ContributionDate']>=val[0]) & (filtered_by_district['ContributionDate'] <=val[1])
filtered_by_date = filtered_by_district[mask3]
filtered_by_date = filtered_by_date.sort_values(['ReceivingCommittee','ContributionDate']).reset_index().drop(columns='index')

filing_options = filtered_by_date['FilingPeriod'].unique().tolist()
filing_options.insert(0, 'All Filing Periods')

select_filing_period = st.selectbox('Select Filing Period:',options=filing_options)

if select_filing_period =='All Filing Periods':
    filtered_by_filing_period = filtered_by_date
else:
    mask4 = filtered_by_date['FilingPeriod']==select_filing_period
    filtered_by_filing_period = filtered_by_date[mask4]

# Filter the dataframe based on the selected date range and categories

if st.checkbox('Compare various candidates'):
    candidate_selection = st.multiselect('Candidate Name:', filtered_by_filing_period['CandidateName'].unique())
    st.markdown('#### Campaign Finance Summary for Selected Criteria')
    summary_cols = st.columns(len(candidate_selection)+1)
    nn=0
    with summary_cols[nn]:
         st.text(f'Name: \nCount: \nSum:')
         nn+=1
    for candidate in candidate_selection:
        narrow_mask = filtered_by_filing_period['CandidateName']==candidate
        number_of_results = filtered_by_filing_period[narrow_mask]['ContributionAmount'].shape[0]
        sum_of_results = filtered_by_filing_period[narrow_mask]['ContributionAmount'].sum()
        with summary_cols[nn]:  
            st.text(f'{candidate} \n{number_of_results} \n${sum_of_results:,.2f}')
        nn+=1
else:
    name_options = st.sidebar.selectbox('Candidate Name:', filtered_by_filing_period['CandidateName'].unique())
    mask2 = filtered_by_filing_period['CandidateName'] == name_options
    filtered_by_name = filtered_by_filing_period[mask2]

    candidate_options = filtered_by_name['ReceivingCommittee'].unique()
    select_candidates = st.multiselect('Select Campaign Committees:',options=candidate_options, default=candidate_options)
    mask5 = filtered_by_name['ReceivingCommittee'].isin(select_candidates)

    filtered_by_candidate = filtered_by_name[mask5] 
    col1, col2 = st.columns(2)

    with col1:
        st.metric('Total Number of Contributions:',filtered_by_candidate['ContributionAmount'].count())

    with col2:
        st.metric('Total Money Raised:','${:,.2f}'.format(filtered_by_candidate['ContributionAmount'].sum()))

    excluded_row = ['ReceivingCommittee', 'FilingPeriod','Office','Fundtype','CandidateName', 'CouncilmanicDistrict']
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