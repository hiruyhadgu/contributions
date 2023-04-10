import streamlit as st
import pandas as pd
import plotly.express as px
from modules.functions import group_by_filing_period
from modules.db_load import load, developer
import datetime as dt
import re

## Load all tables
raw_table = load()
raw_table['Contribution Date'] = pd.to_datetime(raw_table['Contribution Date'])

def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]

developer_filter = developer()

developer_list = developer()

developer_verify = developer_list['Developer/Developer Affiliated'].isin(['yes','Yes', 'YES'])
developer_list = developer_list[developer_verify]
developer_mask = raw_table['Contributor Name'].isin(developer_list['Contributor Name'])

st.markdown('##### Click on the individual districts to drill down on candidates')
office = st.selectbox('Select Office Type (CC or CE):', raw_table['Office'].unique())
@st.cache_data
def plot1(office):
    mask1 = raw_table['Office']== office
    fig = px.sunburst(raw_table[mask1], path=['Councilmanic District', 'Candidate Name'], values='Contribution Amount')
    st.write(fig)
    st.markdown('----')
    if office == 'County Executive':
        x_val = 'Candidate Name'
    else:
        x_val = 'Councilmanic District'
    fig1 = px.bar(raw_table[mask1], x=x_val, y="Contribution Amount", color="Candidate Name", pattern_shape="Candidate Name")
    st.write(fig1)

@st.cache_data
def plot2(value, office, candidate):
    mask = (raw_table['Office']== office) & (raw_table['Candidate Name']==candidate)
    slider_mask =  (raw_table["Contribution Amount"] >=value[0]) & (raw_table["Contribution Amount"] <=value[1])
    to_plot = raw_table[mask & slider_mask]
    count = to_plot['Contribution Amount'].count()
    fig2 = px.histogram(to_plot, x="Contribution Amount", nbins=100, title = f'Contributions for {candidate} in selected range: {count}')
    st.write(fig2)

plot1(office)

st.markdown('----')
st.markdown("### To examine small-dollar contributions, select from the following range.")
sub_table = raw_table[raw_table['Office']==office]
candidate_name1 =  sub_table['Candidate Name'].unique()
candidate_selection1 = st.selectbox('Candidate Name:',
                                    candidate_name1, key = 1)
slider_range = st.slider("Select Dollar Range ($)", value = [0, 250])

plot2(slider_range, office, candidate_selection1)

st.markdown('----')

plot_data = st.sidebar.checkbox('Show Plots for Selected Criteria', value=False)
developer_analysis = st.sidebar.checkbox('Show Developer Contributions')
st.markdown('### Click on the checkboxes on the sidebar to review developer contribution.')
# Filter by filing period
candidate_name =  raw_table['Candidate Name'].unique()
candidate_selection = st.selectbox('Candidate Name:',
                                    candidate_name)
candidate_mask = raw_table['Candidate Name']==candidate_selection
filtered_candidate = raw_table[candidate_mask]

filing_options = filtered_candidate['Filing Period'].unique().tolist()
filing_options.sort(key=natural_keys)
filing_options.insert(0,'All Filing Periods')
select_filing_period = st.selectbox('Select Filing Period',filing_options,0)


if select_filing_period =='All Filing Periods':
    filtered_filing_period = filtered_candidate
else:
    filing_option_mask = filtered_candidate['Filing Period']==select_filing_period
    filtered_filing_period = filtered_candidate[filing_option_mask]


#selected_candidate = st.sidebar.selectbox('Candidate Name:', candidate_name)

if developer_analysis==True:
    mask =developer_mask
    bar_mask = True
    who = 'Developers'
    to_display = filtered_filing_period[mask]
    
else:
    bar_mask=False
    who = 'All'
    to_display = filtered_filing_period

@st.cache_data
def grouped_for_plot(df):
    df_grouped = df.groupby(['Contributor Name', 'Candidate Name']).agg({'Contribution Amount':["sum"], 'Contributor Name':["count"]})
    df_grouped.columns=['Total Contribution', 'No of Contributions']
    return df_grouped

if plot_data:

    plots = ['Top N Contributions', 'Developer Percent Contribution', 'By Filing Period']
    picked_plot = st.sidebar.selectbox('Pick a Plot', plots)

    #st.write(f'{len(picked_plot)}')
    if picked_plot == plots[1]:
        if developer_analysis:
            try:
                # st.write('Select the "Display Developer Contributions" checkbox')
                data_set=['Developer Donations', 'Remaining']
                percent_dev = filtered_filing_period[developer_mask]['Contribution Amount'].sum()/filtered_filing_period['Contribution Amount'].sum()
                values = [percent_dev, 1-percent_dev]
                fig = px.pie(filtered_filing_period['Contribution Amount'], values=values, names=data_set)
                st.caption('Percent share of contributions from developers. Note that some candidates\
                    participate in public financing or did not file for the selected criteria.')
                display = st.plotly_chart(fig)
            except ValueError:
                st.markdown('### Data does not exist for selected criteria.')
                st.code('Try a different filing period.')
        else:
            st.markdown('Select the **Display Developer Contributions Only** checkbox')
    elif picked_plot == plots[0]:
        n = st.sidebar.slider('How Many Contributions?:', 
                                min_value = 10,
                                max_value = 40)
        try:
            table_cols = grouped_for_plot(to_display).reset_index().sort_values(by=['Total Contribution'], ascending = False).head(n)
            fig = px.bar(table_cols, x=table_cols['Contributor Name'], y=table_cols['Total Contribution'],color=table_cols['Candidate Name'])
            display = st.plotly_chart(fig)
        except ValueError:
            st.markdown('### Data does not exist for selected criteria.')
            st.code('Try a different filing period.')
    elif picked_plot == plots[2]:
        try:
            if developer_analysis:
                df_master_bar = filtered_candidate[developer_mask]
            else:
                df_master_bar = filtered_candidate

            contribution_by_filing_period = to_display.groupby(['Candidate Name','Filing Period'])
            contribution_by_filing_period=contribution_by_filing_period.agg(
                TotalContribution =('Contribution Amount','sum')).reset_index()
            fig = px.bar(contribution_by_filing_period, x = contribution_by_filing_period['Filing Period'], 
                        y=contribution_by_filing_period['TotalContribution'],color=contribution_by_filing_period['Candidate Name'])
            display = st.plotly_chart(fig)
        except ValueError:
            st.markdown('### Data does not exist for selected criteria.')
            st.code('Try a different filing period.')

# fig4 = px.scatter(raw_table, x="Contribution Amount", y="Candidate Name", color="Councilmanic District",
#                  title="Countribution Amounts by Candidate and District",
#                  labels={"Countribution Amount":"Countribution Amount (in thousands)"} # customize axis label
#                 )

# st.write(fig4)
# raw_table['Contribution Date'] =  pd.to_datetime(raw_table['Contribution Date'])
# year = raw_table['Contribution Date'].sort_values().dt.year
# fig5 = px.scatter(raw_table, x="Filing Period", y="Contribution Amount", animation_frame='Contribution Date',
#                   animation_group='Contribution Amount', size="Contribution Amount", color="Candidate Name",
#            hover_name="Candidate Name", size_max=100)
# st.write(fig5)


#histogram
# hist_table = filtered_by_candidate.value_counts('Contribution Amount').sort_values()
# print(hist_table)
# fig = px.histogram(hist_table)
# st.write(fig)