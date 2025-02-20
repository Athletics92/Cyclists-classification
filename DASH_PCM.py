import dash
from dash import dcc, html, Input, Output, dash_table
import pandas as pd
import numpy as np
import io
import base64
import os
import plotly.graph_objects as go

from datetime import datetime
from datetime import date

DTJ=date.today()
print(DTJ)

current_year = DTJ.strftime("%Y")
print("Année actuelle =", current_year)


# Charger le fichier Excel depuis un chemin relatif ou en ligne
file_path = "02_INPUTS/_20230301_inputs_projet_pcm.xlsx"

# Vérification que le fichier existe
if not os.path.exists(file_path):
    raise FileNotFoundError(f"Le fichier {file_path} est introuvable !")

# Charger les données Excel
df = pd.read_excel(file_path, sheet_name="CYCLISTS")


df["Age"] =(((pd.to_datetime("today") - pd.to_datetime(df["Date_de_naissance"])).dt.days) / 365.25).astype(int)
df["Annees_exp"]=int(current_year)-df["value_i_yearneopro"]
df.head()


df=df[['IDcyclist','Nom','Prenom','Prenom_nom','ID_team','Age','Annees_exp','fklDregion','Date_de_naissance','Popularite','value_f_potentiel','taille_coureur','poids_coureur','carac_plaine','carac_montagne','carac_descente','carac_paves','carac_clm','carac_prologue','carac_sprint','carac_acceleration','carac_endurance','carac_resistance','carac_recuperation','carac_vallon','carac_baroudeur','prendra_sa_retraite','Coureur_champion','gene_ilist_flkDfavorite_races','value_i_yearneopro','gene_i_nb_victory','gene_i_nb_tdf','gene_i_nb_giro','gene_i_nb_vuelta','gene_i_nb_sanremo','gene_i_nb_flandres','gene_i_nb_roubaix','gene_i_nb_liege','gene_i_nb_lombardia']]

# Ajout d'une colonne "carac_moy" pour l'analyse
df["carac_moy"] = round(((df['carac_plaine'] + df['carac_montagne'] + df['carac_descente'] +
                          df['carac_paves'] + df['carac_clm'] + df['carac_prologue'] + df['carac_sprint'] +
                          df['carac_acceleration'] + df['carac_endurance'] + df['carac_resistance'] +
                          df['carac_recuperation'] + df['carac_vallon'] + df['carac_baroudeur']) / 13), 2)

# Convertir Date_de_naissance en format date YYYY-MM-DD
df["Date_de_naissance"] = pd.to_datetime(df["Date_de_naissance"])
#df["Date_de_naissance"] = df["Date_de_naissance"].dt.strftime('%Y-%m-%d')

# Calcul des moyennes des caractéristiques pour tous les coureurs
moyenne_caracs = df[['carac_plaine', 'carac_montagne', 'carac_paves',
                     'carac_clm', 'carac_sprint', 'carac_endurance']].mean()

print(df.shape)
print(df["Date_de_naissance"].dtype)
df.head()


# Calcul des moyennes globales de toutes les caractéristiques
moyennes_globale = df[["carac_plaine", "carac_montagne", "carac_paves", "carac_clm", "carac_sprint", "carac_endurance"]].mean().tolist()

# Création de l'application Dash
app = dash.Dash(__name__)

# Mise en page de l'application avec image de fond
app.layout = html.Div(style={
    'backgroundColor': '#f0f0f0',  # Fond gris clair pour toute la page
    'height': '100vh',  # Pleine hauteur de la page
    'padding': '20px'
}, children=[

    # Nouveau titre global pour le report (plus petit et plus proche du haut)
    html.H1("Outil de profil des coureurs cyclistes", 
            style={
                'textAlign': 'center', 
                'color': 'black', 
                'fontSize': '24px',  # Réduire la taille du titre
                'marginTop': '10px'   # Réduire la marge au-dessus
            }),

    # Tableau interactif filtrable
    dash_table.DataTable(
        id='table-data',
        data=df.to_dict('records'),
        columns=[{"name": col, "id": col} for col in df.columns],
        page_size=5,
        sort_action="native",
        filter_action="native",
        style_table={'width': '100%', 'marginBottom': '20px'},
        style_header={'backgroundColor': '#d3d3d3', 'fontWeight': 'bold'},  # Gris pour l'en-tête
        style_cell={'textAlign': 'left', 'fontSize': '12px', 'padding': '5px'}
    ),

    html.Br(),

    # Disposition Radar à gauche et Profil à droite
    html.Div(style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center'}, children=[

        # Partie Gauche : Graphique Radar (moins haut)
        html.Div(style={'width': '45%'}, children=[
            dcc.Dropdown(
                id='cyclist-dropdown',
                options=[{'label': name, 'value': name} for name in df["Prenom_nom"]],
                value=df["Prenom_nom"].iloc[0],
                clearable=False,
                style={'fontSize': '12px', 'width': '100%'}
            ),
            dcc.Graph(id='radar-chart', style={'height': '250px'})  # Réduire la hauteur du radar
        ]),

        # Partie Droite : Encart Profil (fond semi-transparent)
        html.Div(id='profil-card', style={
            'width': '45%', 'backgroundColor': 'rgba(6, 84, 100, 0.8)',  # Semi-transparent
            'padding': '10px', 'borderRadius': '10px', 'color': 'white',
            'fontSize': '12px', 'textAlign': 'left'
        })
    ])
])

# Callback pour mettre à jour le graphique Radar et le Profil
@app.callback(
    [dash.dependencies.Output('radar-chart', 'figure'),
     dash.dependencies.Output('profil-card', 'children')],
    [dash.dependencies.Input('cyclist-dropdown', 'value')]
)
def update_radar_and_profile(selected_cyclist):
    cyclist_data = df[df["Prenom_nom"] == selected_cyclist].iloc[0]

    categories = ["carac_plaine", "carac_montagne", "carac_paves", "carac_clm", "carac_sprint", "carac_endurance"]
    values = [cyclist_data[cat] for cat in categories]

    # Utilisation des moyennes globales pour le second niveau (moyennes de tous les coureurs)
    values_moyenne = moyennes_globale

    # Graphique Radar
    radar_chart = go.Figure()

    # Ajouter la ligne pour le coureur sélectionné
    radar_chart.add_trace(go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill='toself',
        name=f'{selected_cyclist} (Coureur)',
        line=dict(color='blue')
    ))

    # Ajouter la ligne pour la moyenne globale
    radar_chart.add_trace(go.Scatterpolar(
        r=values_moyenne + [values_moyenne[0]],
        theta=categories + [categories[0]],
        fill='toself',
        name='Moyenne Globale',
        line=dict(color='red', dash='dot')
    ))

    radar_chart.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=True,
        margin=dict(l=20, r=20, t=20, b=20),
        plot_bgcolor='#f0f0f0',  # Fond gris clair pour l'intérieur du radar
        paper_bgcolor='#f0f0f0',  # Fond gris clair pour la zone extérieure du radar
        legend=dict(x=0.85, y=0.95)  # Position de la légende
    )

    profile_card = html.Div([
        html.H4(f"Profil de {selected_cyclist}", style={'marginBottom': '5px'}),
        html.P(f"Équipe : {cyclist_data['ID_team']}", style={'marginBottom': '2px'}),
        html.P(f"Age : {cyclist_data['Age']}", style={'marginBottom': '2px'}),
        html.P(f"Annees d'expérience : {cyclist_data['Annees_exp']}", style={'marginBottom': '2px'}),
        html.P(f"Popularité : {cyclist_data['Popularite']}", style={'marginBottom': '2px'}),
        html.P(f"Caractéristique moyenne : {cyclist_data['carac_moy']}", style={'marginBottom': '2px'})
    ])

    return radar_chart, profile_card


# Définir server pour Gunicorn
server = app.server  

# Récupération du port attribué par Render (ou 8050 par défaut en local)
port = int(os.environ.get("PORT", 8050))

if __name__ == "__main__":
    app.run_server(debug=False, host="0.0.0.0", port=port)
