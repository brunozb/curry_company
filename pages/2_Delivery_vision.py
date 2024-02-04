
# Libraries

import pandas as pd
from haversine import haversine
import re
import numpy as np
import plotly
import plotly.express as px
import folium
import streamlit as st
from PIL import Image
from streamlit_folium import folium_static

st.set_page_config( page_title='Delivery Vision',page_icon='📈', layout='wide' )

# -----------------------------------
# Functions
# -----------------------------------

def top10(df , top_asc):
    """ This function brings the top 10 fastest and slowest delivery people from the DataFrame:
    
        Steps:
        1. Selects the columns 'City', 'Delivery_person_ID' and 'Time_taken(min)';
        2. Calculates the average and reset index;
        3. Orders by the column 'Time_taken(min)', ascending or descending, depending of the parameter input;
        4. Selects the top 10 in groups of types of cities
        5. Concatenates the 3 columns generated and show the result in a only DataFrame called df_top
        
        Input: DataFrame and order of column 'Time_taken(min)'
        Output: DataFrame   
    """
    # Calculating the average delivery time for each delivery person in each city:
    df_velocity = df.groupby(['City', 'Delivery_person_ID'])['Time_taken(min)'].mean().reset_index()
    # Sorting values in order - ascending or descending
    df_velocity = df_velocity.sort_values(['City', 'Time_taken(min)'], ascending=top_asc)
    # Selecting the top 10 for each type of city:
    df_top = pd.concat([df_velocity[df_velocity['City'] == 'Metropolitian'].head(10),
                       df_velocity[df_velocity['City'] == 'Urban'].head(10),
                       df_velocity[df_velocity['City'] == 'Semi-Urban'].head(10)]).reset_index(drop=True)

    return df_top

def ratings (col):
    
    #Selecting columns:
    avg_rat = df.loc[: , ['Delivery_person_Ratings' , col]]

    #Calculating the column with the average rating by the selected column:
    avg_rat = (avg_rat.loc[: , ['Delivery_person_Ratings' , col ] ]
                    .groupby(col)
                    .agg( {'Delivery_person_Ratings': ['mean' , 'std' ] } ))
    #Renaming the columns:
    avg_rat = (avg_rat.rename(columns={ 'Delivery_person_Ratings':'Delivery person ratings' , 'mean':'Average' , 'std':'Standard Deviation' })
                      .reset_index())
    st.dataframe(avg_rat)

def calculate (col , operation):
    if operation == 'max':
        results = df.loc[: , col].max()

    elif operation == 'min':
        results = df.loc[: , col].min()

    return results

def clean_code ( df_raw ):
    """ This function cleans the DataFrame
    
        Types of cleaning:
        1. Removing NaN datas
        2. Changing the type of the columns
        3. Removing spaces from strings variables
        4. Formatation of Date Column
        5. Cleaning of Time column - removing text from number variable
        
        Input: DataFrame
        Output: DataFrame   
    """
    
    # Remover espaco da string
    df_raw.loc[: , 'ID'] = df_raw.loc[: , 'ID' ].str.strip()
    df_raw.loc[: , 'Delivery_person_ID'] = df_raw.loc[: , 'Delivery_person_ID' ].str.strip()
    df_raw.loc[: , 'Road_traffic_density'] = df_raw.loc[: , 'Road_traffic_density' ].str.strip()
    df_raw.loc[: , 'Type_of_order'] = df_raw.loc[: , 'Type_of_order' ].str.strip()
    df_raw.loc[: , 'Type_of_vehicle'] = df_raw.loc[: , 'Type_of_vehicle' ].str.strip()
    df_raw.loc[: , 'Festival'] = df_raw.loc[: , 'Festival' ].str.strip()
    df_raw.loc[: , 'City'] = df_raw.loc[: , 'City' ].str.strip()

    # Excluir as linhas com a idade dos entregadores vazia
    # ( Conceitos de seleção condicional )
    linhas_vazias = df_raw['Delivery_person_Age'] != 'NaN '
    df_raw = df_raw.loc[linhas_vazias, :]

    # Conversao de texto/categoria/string para numeros inteiros
    df_raw['Delivery_person_Age'] = df_raw['Delivery_person_Age'].astype( int )

    # Conversao de texto/categoria/strings para numeros decimais
    df_raw['Delivery_person_Ratings'] = df_raw['Delivery_person_Ratings'].astype( float )

    # Conversao de texto para data
    df_raw['Order_Date'] = pd.to_datetime( df_raw['Order_Date'], format='%d-%m-%Y' )

    # Remove as linhas de algumas colunas que tenham o 
    # conteudo igual a NaN:
    linhas_vazias = df_raw['multiple_deliveries'] != 'NaN ' 
    linhas_vazias2 = df_raw['Weatherconditions'] != 'conditions NaN'
    df_raw = df_raw.loc[linhas_vazias, :]
    df_raw = df_raw.loc[linhas_vazias2, :]
    df_raw = df_raw.loc[df_raw['City'] != 'NaN' , :]
    df_raw['multiple_deliveries'] = df_raw['multiple_deliveries'].astype( int )
    
    # Comando para remover o texto de números
    df_raw = df_raw.reset_index( drop=True )
    for i in range( len( df_raw ) ):
        df_raw.loc[i, 'Time_taken(min)'] = re.findall( r'\d+', df_raw.loc[i, 'Time_taken(min)'] )

    # Transformando os elementos da coluna "Time_taken" de listas para int:
    df_raw['Time_taken(min)'] = df_raw['Time_taken(min)'].explode().astype(int)

    return df_raw

# ----------------- Starting the logical structure of the code -------------------------------
# -----------------
# Import dataset:
# -----------------
df_raw = pd.read_csv('ftc_train.csv')

# -------------------
# Cleaning Dataset
# -------------------

df = clean_code (df_raw)

#======================================================================

# Side bar

#======================================================================


st.header('Marketplace - Delivery Person Vision', divider='rainbow')

#image_path = 'image.jfif'
image = Image.open ( 'image.jfif' )
st.sidebar.image( image , width=120 )

st.sidebar.markdown('# Curry Company #')
st.sidebar.markdown('## Fastest Delivery in Town ##')
st.sidebar.markdown('''---''')

st.sidebar.markdown('## Select a deadline ##')

data_slider = st.sidebar.slider(
    'Up to date:',
    value=pd.datetime(2022 , 4 , 3),
    min_value=pd.datetime(2022 , 2 , 4 ),
    max_value=pd.datetime(2022 , 6 , 4),
    format='DD-MM-YYYY')

traffic_options = st.sidebar.multiselect(
    'What are the possible traffic conditions?',
    ['Low', 'Medium', 'High' , 'Jam'],
     default=['Low', 'Medium', 'High' , 'Jam'])

st.sidebar.markdown('''---''')
st.sidebar.markdown('### Powered by Bruno Boneto ###')

#Date filter
selected_rows = df['Order_Date'] < data_slider
df = df.loc[selected_rows , :]

#======================================================================

# Layout in Streamlit - to run, press 'streamlit run visao_entregadores_funcional.py'

#======================================================================

tab1, tab2, tab3 = st.tabs(['Management Vision' , '_' , '_'])

with tab1:
    with st.container():
        st.title('Overal Metrics')
        
        col1, col2, col3, col4 = st.columns(4 , gap='large')
        
        with col1: 
            st.subheader('Older age of delivery person')
            
            #Calculating the oldest age and showing:
            oldest_age = calculate ('Delivery_person_Age' , 'max')
            col1.metric('' , oldest_age)
        
        with col2:
            st.subheader('Younger age of delivery person')
            
            #Calculating the younger age en showing:
            younger_age = calculate ('Delivery_person_Age' , 'min')
            col2.metric('', younger_age)
        
        with col3: 
            st.subheader('Best condition of vehicles')
        
            #Selecting and showing the best condition of vehicles:
            best_condition = calculate ( 'Vehicle_condition' , 'max' )
            col3.metric('',best_condition)
        
        with col4: 
            st.subheader('Worst condition of vehicles')
            
            #Selecting and showing the worst condition of vehicles:
            worst_condition = calculate ( 'Vehicle_condition' , 'min' )
            col4.metric('' , worst_condition)
            
    with st.container():
        st.markdown("""---""")
        st.title('Ratings')
        
        col1, col2 = st.columns( 2 )
        
        with col1:
            st.markdown('##### Average rating by delivery person')
        
            #Calculating and showing average ratings of each delivery person:
            average_rating = (df.loc[: , ['Delivery_person_ID' ,'Delivery_person_Ratings']]
                                .groupby('Delivery_person_ID')
                                .mean()
                                .reset_index())
            st.dataframe(average_rating)
        
        
        with col2:
            st.markdown('##### Average rating by type of traffic')
            ratings ('Road_traffic_density')
                       
            st.markdown('##### Average rating by weather conditions')
            ratings ('Weatherconditions')    
            

            
    with st.container():
        st.markdown("""---""")
        st.title('Delivery Time')
        
        col1, col2 = st.columns( 2 )
        
        with col1:
            st.markdown('##### Top Fastest Deliverers')
            df_top_fastest = top10 (df , top_asc=True )
            st.dataframe( df_top_fastest )     
        
        with col2:
            st.markdown('##### Top Slowest Deliverers')
            df_top_slowest = top10 (df , top_asc=False)
            st.dataframe( df_top_slowest )