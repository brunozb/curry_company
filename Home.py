import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Home",
    page_icon="🍕"
)
   
image = Image.open ('image.jfif')
st.sidebar.image ( image , width=120 )

st.sidebar.markdown('# Curry Company #')
st.sidebar.markdown('## Fastest Delivery in Town ##')
st.sidebar.markdown('''---''')

st.write( "# Curry Company Growth Dashboard" )

st.markdown(
    """
    Growth Dashboard was built to follow Delivery people an Restaurants growth metrics 
    ### How can I use this Growth Dashboard?
    - Company Vision:
        - Management Vision: Behavior overall metrics;
        - Tactic Vision: Weekly growth indicators;
        - Geographic Vision: Geolocalization insights
    - Delivery Vision:
        - Monitoring weekly growth indicators
    - Restaurant Vision:
        - Weekly restaurant growth indicators 
    ### Ask for Help
    - @bruno.boneto - brunozb10@gmail.com
    """ )