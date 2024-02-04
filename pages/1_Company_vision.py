
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

st.set_page_config( page_title='Company Vision',page_icon='📈', layout='wide' )

# -----------------------------------
# Functions
# -----------------------------------

def country_maps( df ):
    # Selecting median locations by City:
    df_aux7 = (df.loc[: , ['City' , 'Road_traffic_density' , 'Delivery_location_latitude' , 'Delivery_location_longitude'] ]
                      .groupby(['City' , 'Road_traffic_density'])
                      .median()
                      .reset_index())

    # Creating the map:
    map = folium.Map()

    #Inserting the location medians by City and Road traffic density: 
    for index, location_info in df_aux7.iterrows():
        folium.Marker( [location_info['Delivery_location_latitude' ],
                      location_info['Delivery_location_longitude']],
                      popup=location_info[['City', 'Road_traffic_density']] ).add_to( map )
    
    # Salvar o mapa como uma imagem
    folium_static(map, width=1024 , height=600 ) 

    return None
       

def order_share_by_week ( df ):
          
    # Groupby:
    df_aux4 = ( df.loc[: , ['ID'  , 'week_of_year']]
                  .groupby('week_of_year')
                  .count()
                  .reset_index() )
    df_aux5 = ( df.loc[: , ['Delivery_person_ID' , 'week_of_year']]
                  .groupby('week_of_year')
                  .nunique()
                  .reset_index() )

    # Joining two DFs:
    df_aux6 = pd.merge(df_aux4,df_aux5,how='inner')

    # Creating the column of orders average by Deliveries:  
    df_aux6['Orders_by_deliver'] = df_aux6['ID']/df_aux6['Delivery_person_ID']

    # Creating the graphic:
    fig = px.line(df_aux6 , x='week_of_year' , y='Orders_by_deliver')

    return fig
        
def order_by_week ( df ):
            
    # Creating a column with weeks of the year:
    df['week_of_year'] = df.Order_Date.dt.strftime('%U')

    # Groupby week_of_year:
    pedidos_por_semana = (df.loc[: , ['week_of_year' , 'ID']]
                            .groupby('week_of_year')
                            .count()
                            .reset_index())

    # Building graphic:
    fig = px.line( pedidos_por_semana , x='week_of_year' , y='ID' )

    return fig
        
def traffic_order_city( df ):
    # Groupby:
    df_aux3 = (df.loc[: , ['City' , 'Road_traffic_density' , 'ID']]
                       .groupby(['City','Road_traffic_density'])
                       .count()
                       .reset_index())

    #Building a Bubble graphic:
    fig = px.scatter(df_aux3 , x='City' , y='Road_traffic_density' , size='ID' , color='City')
    
    # Update layout (it´s an option, mas can be useful customize the graphic)
    fig.update_layout(title='')

    return fig    
   
def traffic_order_share( df ):
                                    
    # Groupby Road traffic density:
    pedidos_por_tipodetrafego = (df.loc[: , ['Road_traffic_density' , 'ID']]
                                   .groupby('Road_traffic_density')
                                   .count()
                                   .reset_index())
    pedidos_por_tipodetrafego['perc_entrega'] = pedidos_por_tipodetrafego['ID']/pedidos_por_tipodetrafego['ID'].sum()

    # Building graphic:
    fig = px.pie(pedidos_por_tipodetrafego , values='perc_entrega' ,  names='Road_traffic_density')

    return fig

def order_metric ( df ):
            
    # Selecting columns by day:
    df_aux = df.loc[: , ['Order_Date' , 'ID']].groupby('Order_Date').count().reset_index()

    #Building graphic:
    fig = px.bar(df_aux,x='Order_Date',y='ID')

    return fig
        
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
    
    # Filtro de Trânsito

    #linhas_selecionadas = df['Road_traffic_density'].isin(traffic_options)
    #df = df.loc[linhas_selecionadas , :]
    #st.dataframe( df )

    # Comando para remover o texto de números
    df_raw = df_raw.reset_index( drop=True )
    for i in range( len( df_raw ) ):
        df_raw.loc[i, 'Time_taken(min)'] = re.findall( r'\d+', df_raw.loc[i, 'Time_taken(min)'] )

    return df_raw

# ----------------- Starting the logical structure of the code -------------------------------
# -----------------
# Import dataset:
# -----------------
df_raw = pd.read_csv('ftc_train.csv')

# -------------------
# Cleaning DataFrame
# -------------------

df = clean_code (df_raw)

    
#======================================================================

# Side bar

#======================================================================


st.header('Marketplace - Restaurant Vision', divider='rainbow')

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

# Layout in Streamlit - to run, on the terminal press: streamlit run visao_empresa.py

#======================================================================

tab1, tab2, tab3 = st.tabs(['Management Vision' , 'Tactical Vision' , 'Geographic Vision'])

with tab1:
    with st.container():
        # Order Metric
        fig = order_metric(df)
        st.markdown('# Orders by day')
        st.plotly_chart(fig , use_container_width=True)
        
        
        
    with st.container():
        col1, col2 = st.columns( 2 )
        
        with col1:
            fig = traffic_order_share( df )
            st.header( "Orders by Road Traffic Density" )
            st.plotly_chart( fig, use_container_width=True )
     
        with col2:
            st.header('Orders by City and Type of Traffic')
            fig = traffic_order_city ( df )
            st.plotly_chart( fig , use_container_width=True)
            
with tab2:
    with st.container():
        st.markdown('Order by Week')
        fig = order_by_week ( df )
        st.plotly_chart (fig, use_container_width=True)
                   
    with st.container():
        st.markdown('Orders by Delivery Person by Week')
        fig = order_share_by_week ( df )
        st.plotly_chart ( fig , use_container_width=True)
        

with tab3:
    st.markdown('# Country Maps')
    country_maps  ( df )
    
    