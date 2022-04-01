import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import unidecode
from datetime import datetime

st.set_page_config(page_title="My App",layout='wide')

# Function to load the data and cache it
@st.cache
def load_data():
    data = pd.read_csv('nat2020.csv', sep=';')
    return data

# Load data and cache it using Streamlit cache
df_raw = load_data()

# On supprime les valeurs de 'annais' == 'XXXX'
df_raw = df_raw[df_raw.annais != 'XXXX'].copy()
df_raw.annais = df_raw.annais.astype(int)
# Drop rows with nan values
df_raw.dropna(inplace=True)
# Apply lowercase to prénoms
df_raw.preusuel = df_raw.preusuel.apply(lambda x: x.lower())
# Suppression des accents
df_raw['preusuel'] = df_raw['preusuel'].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
# Aggrégation prénoms sans accents
df_nat = df_raw.groupby(['preusuel', 'annais', 'sexe']).agg(nombre=('nombre', sum)).reset_index()

# Choix du ou des sexes
st.write('Choisir le sexe')
girls = st.checkbox('Filles')
boys = st.checkbox('Garçons')
sexes = []
if girls:
    sexes.append(2)
if boys:
    sexes.append(1)
if len(sexes) == 0:
    sexes = [1, 2]

df_nat = df_nat[df_nat.sexe.isin(sexes)]
df_nat.columns = ['Prénom', 'Année', 'Sexe', 'Nombre']

# Create a Check box to display the raw data.
# if st.checkbox('Show raw data'):
st.subheader('Raw data')
load_state = st.text('Loading Data..')
st.write(df_nat.sample(5))
load_state.text('Loading Completed! Aperçu des données :')

row3_1, row3_2 = st.columns(2)

with row3_1:

    # Bar chart to show the total number of births through the years
    st.subheader(" Nombre total de naissances par année ")
    df_total_nais_annees = df_nat.groupby('Année').agg({'Nombre' : sum})
    fig = px.bar(df_total_nais_annees, y='Nombre', 
            labels={'Année': 'Année', 'Nombre': 'Nombre de naissances'},)
            # width=1000, height=400)
    st.plotly_chart(fig)


with row3_2:

    # Bar chart montrant le nombre total de prénoms différents attribués par années
    st.subheader(" Nombre de prénoms différents par année ")
    df_total_prenoms_annees = df_nat.groupby('Année').agg({'Prénom' : 'count'})
    fig = px.bar(df_total_prenoms_annees, y='Prénom', 
            labels={'Année': 'Année', 'Prénom': 'Nombre de prénoms'},)
            # width=1000, height=400)
    st.plotly_chart(fig)

prenom_input = st.text_input('Entrez un prénom', '')

prenom_input = unidecode.unidecode(prenom_input).lower()
st.write(prenom_input)

df_prenom = df_nat[(df_nat.Prénom == prenom_input)]

st.subheader(" Evolution du prénom {} ".format(prenom_input))

# Create figure with secondary y-axis
fig = make_subplots(specs=[[{"secondary_y": True}]])
# Add traces
fig.add_trace(
    go.Scatter(x=df_prenom[df_prenom.Sexe == 1].Année, y=df_prenom[df_prenom.Sexe == 1].Nombre, name='Garçons'),
    secondary_y=False,
)
fig.add_trace(
    go.Scatter(x=df_prenom[df_prenom.Sexe == 2].Année, y=df_prenom[df_prenom.Sexe == 2].Nombre, name='Filles'),
    secondary_y=True,
)
fig.update_layout(width=1000)
# Set x-axis title
fig.update_xaxes(title_text="Années")
# Set y-axes titles
fig.update_yaxes(title_text="Garçons", secondary_y=False)
fig.update_yaxes(title_text="Filles", secondary_y=True)
st.plotly_chart(fig)

# Popularité et évolution récente
st.subheader('Popularité et évolution récente des prénoms')

st.subheader("Année la plus récente disponible : {}".format(df_nat.Année.max()))

# Choix des périodes
st.write("Choisir la ou les périodes d'étude")
last3 = st.checkbox('3')
last5 = st.checkbox('5')
last10 = st.checkbox('10')
last20 = st.checkbox('20')

current_year = datetime.now().year

# Drop prenoms_rares
df_nat = df_nat[df_nat.Prénom != '_prenoms_rares']

periodes = []
df_compare = pd.DataFrame()
if last3:
    periodes.append(3)
    df_last_3 = df_nat[(df_nat.Année.isin([year for year in range(current_year - 3, current_year)])) & (df_nat.Sexe.isin(sexes))]
    df_gb_3 = df_last_3.groupby(['Prénom']).agg(last_3=('Nombre', sum)).sort_values(by='last_3', ascending=False).last_3.apply(lambda x: int(x / 3))
    df_compare = pd.concat((df_compare, df_gb_3), axis=1)
if last5:
    periodes.append(5)
    df_last_5 = df_nat[(df_nat.Année.isin([year for year in range(current_year - 5, current_year)])) & (df_nat.Sexe.isin(sexes))]
    df_gb_5 = df_last_5.groupby(['Prénom']).agg(last_5=('Nombre', sum)).sort_values(by='last_5', ascending=False).last_5.apply(lambda x: int(x / 5))
    df_compare = pd.concat((df_compare, df_gb_5), axis=1)
if last10:
    periodes.append(10)
    df_last_10 = df_nat[(df_nat.Année.isin([year for year in range(current_year - 10, current_year)])) & (df_nat.Sexe.isin(sexes))]
    df_gb_10 = df_last_10.groupby(['Prénom']).agg(last_10=('Nombre', sum)).sort_values(by='last_10', ascending=False).last_10.apply(lambda x: int(x / 10))
    df_compare = pd.concat((df_compare, df_gb_10), axis=1)
if last20:
    periodes.append(20)
    df_last_20 = df_nat[(df_nat.Année.isin([year for year in range(current_year - 20, current_year)])) & (df_nat.Sexe.isin(sexes))]
    df_gb_20 = df_last_20.groupby(['Prénom']).agg(last_20=('Nombre', sum)).sort_values(by='last_20', ascending=False).last_20.apply(lambda x: int(x / 20))
    df_compare = pd.concat((df_compare, df_gb_20), axis=1)
if len(periodes) == 0:
    periodes = [3, 5, 10, 20]
    df_last_3 = df_nat[(df_nat.Année.isin([year for year in range(current_year - 3, current_year)])) & (df_nat.Sexe.isin(sexes))]
    df_gb_3 = df_last_3.groupby(['Prénom']).agg(last_3=('Nombre', sum)).sort_values(by='last_3', ascending=False).last_3.apply(lambda x: int(x / 3))
    df_last_5 = df_nat[(df_nat.Année.isin([year for year in range(current_year - 5, current_year)])) & (df_nat.Sexe.isin(sexes))]
    df_gb_5 = df_last_5.groupby(['Prénom']).agg(last_5=('Nombre', sum)).sort_values(by='last_5', ascending=False).last_5.apply(lambda x: int(x / 5))
    df_last_10 = df_nat[(df_nat.Année.isin([year for year in range(current_year - 10, current_year)])) & (df_nat.Sexe.isin(sexes))]
    df_gb_10 = df_last_10.groupby(['Prénom']).agg(last_10=('Nombre', sum)).sort_values(by='last_10', ascending=False).last_10.apply(lambda x: int(x / 10))
    df_last_20 = df_nat[(df_nat.Année.isin([year for year in range(current_year - 20, current_year)])) & (df_nat.Sexe.isin(sexes))]
    df_gb_20 = df_last_20.groupby(['Prénom']).agg(last_20=('Nombre', sum)).sort_values(by='last_20', ascending=False).last_20.apply(lambda x: int(x / 20))
    df_compare = pd.concat((df_gb_3, df_gb_5, df_gb_10, df_gb_20), axis=1)


# n_display = 50

# st.dataframe(data=df_compare, width=1500, height=500)

headers =  ['Prénom'] + ["Moyenne sur {} ans".format(period) for period in periodes]
list(df_compare.columns)

# headerColor = 'grey'
# rowEvenColor = 'lightgrey'
# rowOddColor = 'white'

# Table rows colors
boyColor = 'lightskyblue'
girlColor = 'pink'
boyOrGirlColor = 'plum'
dict_colors = {1 : boyColor, 2 : girlColor, 3 : boyOrGirlColor}

# Get number of sexe by prenom
df_prenoms_sexes = df_nat.groupby(['Prénom', 'Sexe']).agg(nombre=('Nombre', sum)).reset_index().sort_values(by=['Prénom', 'nombre'], ascending=False)
# Get total number of prenom
df_prenoms_tot = df_prenoms_sexes.groupby('Prénom').agg(total=('nombre', sum)).reset_index()
# Get most frequent sexe proportion for prenom
df_prenom = pd.merge(df_prenoms_tot, df_prenoms_sexes, on='Prénom')
df_prenom['prop_sexe'] = df_prenom.nombre / df_prenom.total
df_prenom.drop_duplicates(subset=['Prénom'], inplace=True)
# Output color. Boy or Girl if 99% of prenom is given to one sexe. Else boy or girl if at least 1% is given to another sexe
df_prenom['number_color'] = df_prenom.apply(lambda row: row.Sexe if row.prop_sexe > 0.99 else 3, axis=1)
df_prenom['color'] = df_prenom.number_color.apply(lambda numcol: dict_colors[numcol])
# Output dictionnary
dict_prenom_color = dict(df_prenom.loc[:, ['Prénom', 'color']].values)

# Get number of sexes by Prénom
df_compare_prenoms = df_compare.reset_index()
df_compare_prenoms = df_compare_prenoms[['Prénom']]
df_compare_prenoms['color'] = df_compare_prenoms.Prénom.apply(lambda prenom: dict_prenom_color[prenom])
ar_colors = df_compare_prenoms.color.values.tolist()

# print(ar_colors)
# print(ar_colors * (len(periodes) + 1))

fig = go.Figure(data=[go.Table(
    header=dict(values=headers,
                # fill_color='paleturquoise',
                align = ['left'] + ['center'] * len(periodes),
                font = dict(size = 20),
                height = 30),
    cells=dict(values=[df_compare.index.values] + [df_compare.loc[:, 'last_{}'.format(period)] for period in periodes],
            #    fill_color='lavender',
                # fill_color = [[rowOddColor,rowEvenColor,rowOddColor, rowEvenColor,rowOddColor] * len(periodes)],
                fill_color = [ar_colors * (len(periodes) + 1)],
                align = ['left'] + ['center'] * len(periodes),
                font = dict(size = 20),
                height = 30
                        ))
                     ])

fig.update_layout(width=1000, height=1000)

st.write("Moyenne de naissances par an sur ces périodes :")

st.plotly_chart(fig)