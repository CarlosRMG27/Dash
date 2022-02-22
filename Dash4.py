from email.policy import default
from turtle import width
from matplotlib import markers
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import seaborn as sns
import plotly.graph_objects as go
from plotly.subplots import make_subplots


#Leemos el csv
df=pd.read_csv(r'C:\Users\rodrigo.revilla\OneDrive - SINTEC\POC Promotoría\data\prueba.csv',encoding = 'unicode_escape', engine ='python')

#Renombramos una columna problemática
df=df.rename({'Nombre Cadena':'Cadena'},axis=1)
df=df.dropna()
df['NTiendaPivote']=df['NTiendaPivote'].astype(str)
df['NTienda']=df['NTienda'].astype(str)

#Damos estilo
sns.set_style('darkgrid')

st.set_page_config(page_title='POC Promotoría',
                  layout="wide") 



# --- Main page ---

st.title('Dashboard')
st.markdown('##')



#------------Sidebar
st.sidebar.header('Filtros')

region=st.sidebar.multiselect('Región',
options=df['Cluster'].unique(),
default=df['Cluster'].unique()[0]
)

df_selection=df.query(
    'Cluster==@region'
)

pivote=st.sidebar.multiselect('Tienda pivote',
options=df_selection['NTiendaPivote'].unique(),
default=df_selection['NTiendaPivote'].unique()[0:2]
)

df_selection2=df_selection.query(
    'NTiendaPivote==@pivote'
)


ID=st.sidebar.multiselect('ID de tienda',
options=df_selection2['NTienda'].unique(),
default=df_selection2['NTienda'].unique()
)

df_selection3=df_selection2.query(
    'NTienda==@ID'
)



num_cols=df.select_dtypes(['float64','float32','int32','int64'])
num_cols=num_cols.columns

    #------------Bar chart--------------

st.header('Promedios de las variables')
st.sidebar.subheader('Setup del bar chart plot')
df_bar=df.drop('NTiendaPivote',axis=1).groupby('NTienda').mean()
df_bar.columns='Promedio de '+num_cols



ind=num_cols.to_list().index('productividad')
resumen=st.sidebar.selectbox(label='Característica a mostrar',options='Promedio de '+num_cols,
index=ind)
tiendas=df_selection3['NTienda'].unique()

df_bar=df_bar.sort_values(by=resumen)
tiendas2=df_bar.loc[tiendas].sort_values(by=resumen).index




#color_discrete_sequence
cds=[]
cat=[]
for item in tiendas2.to_list():
    if item in list(df_selection2['NTiendaPivote'].unique()):
        cds.append('rgb(255,0,0)')
        cat.append('Pivote')
    else:
        cds.append('rgb(0,0,255)')
        cat.append('Vecina')

df_bar2=df_bar.sort_values(by=resumen).loc[tiendas2]
df_bar2['category']=cat

fig = px.bar(
        #df_bar.sort_values(by=resumen),
        df_bar2,     
        y = tiendas2,
        x = df_bar.loc[tiendas2][resumen],
        color='category',
        #color_discrete_sequence=cds,
        orientation = 'h', #Optional Parameter,
        height=700,
        width=1050,
    ).update_layout(xaxis_title=resumen,yaxis_title='ID de Tiendas')

#Recordar que este promedio solo toma en cuenta 
#aquellas tiendas elegidas
M=df_bar.loc[tiendas2][resumen].mean()#Promedio de promedios
df_bar['Promedio']=[M for i in range(len(df_bar))]

#Máximo
M_x=df_bar.loc[tiendas2][resumen].max()
df_bar['Máximo']=[M_x for i in range(len(df_bar))]
#Mediana
M_n=df_bar.loc[tiendas2][resumen].median()
df_bar['Mediana']=[M_n for i in range(len(df_bar))]
#Cuartiles
df_bar2['QR']= pd.qcut(df_bar2[resumen],
                             q = 4, labels = False)
M_q=df_bar2[df_bar2['QR']==2].dropna()
M_q=M_q[resumen][0]
df_bar['Tercer cuartil']=[M_q for i in range(len(df_bar))]

#Botón con opciones de estadística
opciones_func=['Promedio','Máximo','Mediana','Tercer cuartil']
func=st.sidebar.selectbox(label='Función estadística',options=opciones_func)

trace=go.Line(
    x=df_bar.loc[tiendas2][func],
    y=tiendas2,
    mode='lines',
    line = dict(color='royalblue', width=4),
    showlegend=False,
    name=func
)

fig.add_trace(trace)

st.plotly_chart(fig)


prod_obj = df_bar.loc[tiendas2][func][0]
abc = df_bar.filter(items = pivote, axis=0)
prod_real = abc["Promedio de productividad"].mean()
delta_prod = prod_obj-prod_real

st.info("Diferencia de productividad: {:.0f}".format(delta_prod))
st.write("\n")
st.write("\n")
st.write("\n")

st.header('Tiendas menos productivas')

df_def=df_bar.sort_values(by='Promedio de productividad').iloc[0:10] #dataframe deficiente
df_def.drop(['Promedio de distancia','Promedio','Máximo','Tercer cuartil','Mediana',"Promedio de compEntregaNCB","Promedio de compEntregaCSD","Promedio de no_herramientas"],axis=1,inplace=True)
st.table(df_def)

st.write("\n")
st.write("\n")
st.write("\n")
st.header('Variables visualizadas')


st.sidebar.subheader('Setup del scatter plot')

cat2=[]
for item in df_bar.index.to_list():
    if item in list(df_selection2['NTiendaPivote'].unique()):
        cat2.append('Pivote')
    elif item in df_bar2.index.to_list():
        cat2.append('Vecina')
    else:
        cat2.append('Otra')

df_bar['category']=cat2

select_box_x=st.sidebar.selectbox(label='Eje x',options='Promedio de '+num_cols)
select_box_y=st.sidebar.selectbox(label='Eje y',options='Promedio de '+num_cols)

fig3 = px.scatter(
        #df_bar.sort_values(by=resumen),
        df_bar,     
        y = select_box_y,
        x = select_box_x,
        color='category',
        #color_discrete_sequence=cds,
        orientation = 'h', #Optional Parameter
        height=700,
        width=1050,
    ).update_layout(xaxis_title=select_box_x,yaxis_title=select_box_y)

st.plotly_chart(fig3)



#cd "C:\Users\rodrigo.revilla\OneDrive - SINTEC\POC Promotoría"
#streamlit run Dash4.py