# Libraries

import pandas as pd
from haversine import haversine
import re
import numpy as np
import plotly
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import folium
import streamlit as st
from PIL import Image
from streamlit_folium import folium_static

st.set_page_config( page_title='Restaurant Vision',page_icon='📈', layout='wide' )

# -----------------------------------
# Functions
# -----------------------------------

def avg_time_city (df):
    # Fazendo a tabela dinâmica e calculando a média e o desvio padrão:
    df_time = (df.loc[: , ['City' , 'Road_traffic_density' , 'Time_taken(min)']]
               .groupby(['City' , 'Road_traffic_density'])
               .agg( {'Time_taken(min)': ['mean' , 'std'] } ))
    #Renaming average and standard deviation columns and reseting index:
    df_time.columns = ['avg_time' , 'std_time']
    df_time = df_time.reset_index()
    #Making the graphic
    fig = px.sunburst(df_time , path=['City' , 'Road_traffic_density'] , values='avg_time' , color='std_time' , color_continuous_scale='RdBu' , color_continuous_midpoint=np.average(df_time['std_time'] ) )
    return fig

def dist_distr_city (df):
    #Calculate the distance between restaurants and order locations:
    #haversine( (latitude , longitude) , (latitude , longitude) )
    cols = ['Restaurant_latitude' , 'Restaurant_longitude' , 'Delivery_location_latitude' , 'Delivery_location_longitude']
    df['distance'] = df.loc[: , ['Restaurant_latitude' , 'Restaurant_longitude' , 'Delivery_location_latitude' , 'Delivery_location_longitude']]\
                       .apply( lambda x: haversine( (x['Restaurant_latitude'] , x['Restaurant_longitude']) , (x['Delivery_location_latitude'] , x['Delivery_location_longitude'])), axis=1)
    #Calculate average distances between restarants and order locations:
    avg_distance = df.loc[: , ['City' , 'distance']].groupby('City').mean().reset_index()
    #pull is given as a fraction of a pie radius
    fig = go.Figure( data=[go.Pie( labels=avg_distance['City'], values=avg_distance['distance'],pull=[0, 0 , 0.1])])
    return fig
            
def avg_std_time_graph (df , col , group , returning):
    df_time = df.loc[: , col].groupby(group).agg( {'Time_taken(min)': ['mean' , 'std'] } )
    df_time.columns = ['avg_time' , 'std_time']
    df_time = df_time.reset_index()
    if returning  == 'graph':
        graph = go.Figure()
        graph.add_trace( go.Bar( name='Control', x=df_time['City'] , y=df_time['avg_time'] , error_y=dict( type='data' , array=df_time['std_time'] ) ) )
        graph.update_layout(barmode='group')
        #fig.show()    
        fig = st.plotly_chart(graph, use_container_width=True)
        return fig
    elif returning == 'dframe':
        table = st.dataframe( df_time  )
        return table

                
def time (df , festival , operation):
    """ This function calculates the average and the standard deviation from all the time deliveries:
        
        Input: DataFrame, during festival or not, operation ('avg' or 'std')'
        Output: avg or std with or without festival   
    """
    if operation == 'mean':
        result = np.round(df.loc[df['Festival'] == festival , 'Time_taken(min)'].mean() , 2 )
    elif operation == 'std':
        result = np.round(df.loc[df['Festival'] == festival , 'Time_taken(min)'].std() , 2 )
    return result      
        
def distance (df):
    #Calculating the distance between restaurants and delivery locations by latitude and longitude:
    df['distance'] = df.loc[: , ['Restaurant_latitude' , 'Restaurant_longitude' , 'Delivery_location_latitude' , 'Delivery_location_longitude']]\
                       .apply( lambda x: haversine( (x['Restaurant_latitude'] , x['Restaurant_longitude']) , (x['Delivery_location_latitude'] , x['Delivery_location_longitude'])), axis=1)
    #Calculating the average of the distances:
    avg_distance = np.round(df['distance'].mean() , 2)

    return avg_distance
            
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

# Filtro de Data
linhas_selecionadas = df['Order_Date'] < data_slider
df = df.loc[linhas_selecionadas , :]

#======================================================================

# Layout in Streamlit - to run, press 'streamlit run visao_restaurantes_funcional.py'

#======================================================================


tab1, tab2, tab3 = st.tabs(['Management Vision' , '_' , '_'])

with tab1:
    
    #Container 1
    with st.container():
        st.title('Overal Metrics')
        
        col1, col2, col3, col4, col5, col6 = st.columns( 6 )
        
        with col1: 
            #Calculating the number of unique delivery people and showing the result:
            unique_deliveries = len(df.loc[: , 'Delivery_person_ID'].unique())
            col1.metric('Delivery People',unique_deliveries )
        
        with col2:
            avg_distance = distance (df)           
            col2.metric('AVG delivery distance' , avg_distance)
        
        with col3: 
            avg_time_yes = time (df , 'Yes' , 'mean')
            col3.metric('AVG time with Fest' , avg_time_yes)
        
        with col4:
            std_time_yes = time (df , 'Yes' , 'std')
            col4.metric('STD time with Fest' , std_time_yes)
                                   
        with col5:
            avg_time_no = time (df , 'No' , 'mean')
            col5.metric('AVG time without Fest' , avg_time_no)
            
        with col6:
            std_time_no = time (df , 'No' , 'std')
            col6.metric('STD time without Fest' , std_time_no)
            
    # Container 2
    with st.container():
        st.title('Time Distribution')
        col1, col2 = st.columns( 2 )
        
        with col1:
            st.markdown('##### By Cities')
            avg_std_time_graph (df , ['City' , 'Time_taken(min)'] , 'City' , 'graph')
            
        with col2:  #Média e desv pdr por cidade e tipo de entrega
            st.markdown('##### Avg and Std by City and type of order')
            avg_std_time_graph (df , ['City' , 'Type_of_order' , 'Time_taken(min)'] , ['City' , 'Type_of_order'] , 'dframe')
            
    #Container 3
    with st.container():
        #st.title('Distance Distribution')
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('##### Distance distribution by cities')
            figure = dist_distr_city (df)
            st.plotly_chart(figure, use_container_width=True)
            
        with col2:
            st.markdown('##### Average time by cities and type of traffic') 
            figure = avg_time_city (df)
            st.plotly_chart(figure)
            
            
                 
            
        
        
    
        
        
        
        
       