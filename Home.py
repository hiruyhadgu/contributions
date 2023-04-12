import streamlit as st
from PIL import Image

image = Image.open('combined.jpeg')
st.set_page_config(page_title='Howard County Council Candidate Contributions', 
            page_icon=image)

st.sidebar.image("combined.jpeg", use_column_width=True)

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