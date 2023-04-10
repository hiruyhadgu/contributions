import streamlit as st

st.title('Howard County Local Election Campaign Finance')
st.write(
    """
    This website presents campaign finance data for Howard County candidates. It includes all
    contribution data, since 2006, of all candidates who have participated in county council and 
    county executive races. It will be updated with new candidates over time.
    This page provides a visual analysis of all-time campaign contributions for
    candidates running for the County Council and County Executive.
    """
    )
st.markdown("""
    [Click Here](https://data.howardcountymd.gov/DataExplorer/Search.aspx?Application=CouncilMember) 
    to navigate to the county website to find your Councilmember then pick the **District** and **Filing Period** 
    to examine from the left sidebar.
""")

st.write('__________________')
    

st.markdown("""
        The entities and individuals classified as developer contributions closely aligns with the classification
        in the [No Developer Pledge](https://www.hocopledge.com/candidate-signing/). The process to identify the 
        entities entails establishing connections based on local groups that deal with zoning and land use, looking 
        at Maryland Corporate and LLC registration info, looking up reported addresses, reviewing campaign contributions 
        for other candidates, and public testimony and affidavit. Please use the contact form to share your thoughts on the 
        list and how it may be improved.

        This list will be updated over time.
""")

st.header(":mailbox: Share your thoughts here.")

contact_form = """
<form action="https://formsubmit.co/joinus@hiruyhadgu.COM" method="POST">
     <input type="hidden" name="_captcha" value="false">
     <input type="text" name="name" placeholder="Your name" required>
     <input type="email" name="email" placeholder="Your email" required>
     <textarea name="message" placeholder="Your message here"></textarea>
     <button type="submit">Send</button>
</form>
"""

st.markdown(contact_form, unsafe_allow_html=True)

# Use Local CSS File
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


local_css("style/style.css")

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# plot_data = st.sidebar.checkbox('Show Plots for Selected Criteria', value=True)

# if plot_data:

#         plots = ['Developer Percent Contribution','Top N Contributions', 'By Filing Period']
#         picked_plot = st.sidebar.selectbox('Pick a Plot', plots)
#         #st.write(f'{len(picked_plot)}')
#         if picked_plot == plots[0]:
#             if developer:
#                 try:
#                    # st.write('Select the "Display Developer Contributions" checkbox')
#                     data_set=['Developer Donations', 'Remaining']
#                     percent_dev = df_master[mask]['Contribution Amount'].sum()/df_master[base_mask]['Contribution Amount'].sum()
#                     values = [percent_dev, 1-percent_dev]
#                     fig = px.pie(df_master['Contribution Amount'], values=values, names=data_set)
#                     st.caption('Percent share of contributions from developers. Note that some candidates\
#                         participate in public financing or did not file for the selected criteria.')
#                     display = st.plotly_chart(fig)
#                 except ValueError:
#                     st.markdown('### Data does not exist for selected criteria.')
#                     st.code('Try a different filing period.')
#             else:
#                 st.markdown('Select the **Display Developer Contributions Only** checkbox')
#         elif picked_plot == plots[1]:
#             n = st.sidebar.slider('How Many Contributions?:', 
#                                     min_value = 10,
#                                     max_value = 40)
#             try:
#                 table_cols = df_grouped_for_plot.reset_index().sort_values(by=['Total Contribution'], ascending = False).head(n)
#                 candidate_names(candidates, table_cols, 'Receiving Committee')
#                 fig = px.bar(table_cols, x=table_cols['Contributor Name'], y=table_cols['Total Contribution'],color=table_cols['Candidate Name'])
#                 display = st.plotly_chart(fig)
#             except ValueError:
#                 st.markdown('### Data does not exist for selected criteria.')
#                 st.code('Try a different filing period.')
#         elif picked_plot == plots[2]:
#             try:
#                 if bar_mask:
#                     df_master_bar = df_master[developer_filter]
#                 else:
#                     df_master_bar = df_master

#                 contribution_by_filing_period = df_master_bar.groupby(['Candidate Name','Filing Period'])
#                 contribution_by_filing_period=contribution_by_filing_period.agg(
#                     TotalContribution =('Contribution Amount','sum')).reset_index()
#                 fig = px.bar(contribution_by_filing_period, x = contribution_by_filing_period['Filing Period'], 
#                             y=contribution_by_filing_period['TotalContribution'],color=contribution_by_filing_period['Candidate Name'])
#                 display = st.plotly_chart(fig)
#             except ValueError:
#                 st.markdown('### Data does not exist for selected criteria.')
#                 st.code('Try a different filing period.')