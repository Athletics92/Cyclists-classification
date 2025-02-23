import dash
from dash import dcc, html, Input, Output, dash_table
import pandas as pd
import numpy as np
import io
import base64
import os
import plotly.graph_objects as go


import dash_core_components as dcc
import dash_html_components as html
import pandas as pd


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
df["Idpalmares_cyclist"] = df["Prenom"] + ' ' + df["Nom"]
print(df.shape)
df.head()


df=df[['IDcyclist','Idpalmares_cyclist','Nom','Prenom','Prenom_nom','ID_team','Age','Annees_exp','fklDregion','Date_de_naissance','Popularite','value_f_potentiel','taille_coureur','poids_coureur','carac_plaine','carac_montagne','carac_descente','carac_paves','carac_clm','carac_prologue','carac_sprint','carac_acceleration','carac_endurance','carac_resistance','carac_recuperation','carac_vallon','carac_baroudeur','prendra_sa_retraite','Coureur_champion','gene_ilist_flkDfavorite_races','value_i_yearneopro','gene_i_nb_victory','gene_i_nb_tdf','gene_i_nb_giro','gene_i_nb_vuelta','gene_i_nb_sanremo','gene_i_nb_flandres','gene_i_nb_roubaix','gene_i_nb_liege','gene_i_nb_lombardia']]

# Convertir Date_de_naissance en format date YYYY-MM-DD
df["Date_de_naissance"] = pd.to_datetime(df["Date_de_naissance"], errors='coerce')
#df["Date_de_naissance"] = df["Date_de_naissance"].dt.strftime('%Y-%m-%d')

# Calcul du niveau moyen par coureur
df["carac_moy"]=round(((df['carac_plaine'] + df['carac_montagne'] + df['carac_descente'] +
df['carac_paves'] + df['carac_clm'] + df['carac_prologue'] + df['carac_sprint'] +
df['carac_acceleration'] + df['carac_endurance'] + df['carac_resistance'] + 
df['carac_recuperation'] + df['carac_vallon'] + df['carac_baroudeur'])/(13)),2)


print(df.shape)
print(df["Date_de_naissance"].dtype)
df.head()



# Conservation des coureurs avec segments calculés précédemment
# Import du fichier Excel
classif = pd.read_excel("03_OUTPUTS/2025-02-20_classification_cyclists.xlsx",sheet_name="base")

print(classif.shape)
classif.head()

df=pd.merge(df,classif[["IDcyclist","HAC_label"]],on="IDcyclist",how="inner")

print(df.shape)
df.head()


# PALMARES
# Import du fichier Excel
palmares = pd.read_excel(file_path,sheet_name="PALMARES")

# Zoom sur certains types de résultats 
palmares = palmares[palmares["Idpalmares_type"].isin(["ETAPE","GENERAL_TEMPS","GENERAL_JEUNES","GENERAL_MONTAGNE","GENERAL_POINTS"])]


#palmares = palmares[palmares["Idpalmares_cyclist"].isin(["Alejandro Valverde"])].sort_values(by=["valeur","value_i_rank"],ascending=[False,True])


# Reformulation des libellés de résultats
    # Types de palmarès
palmares_labels = {
    "ETAPE": "d'une étape du ",
    "GENERAL_MONTAGNE": "du Classement Grimpeurs du ",
    "GENERAL_JEUNES": "du Classement Jeunes du ",
    "GENERAL_POINTS": "du Classement Sprinters du ",
    "GENERAL_TEMPS": "du Général de "
}
palmares["Idpalmares_label"] = palmares["Idpalmares_type"].map(palmares_labels)


    # Position
palmares["value_i_rank_lbl"] = palmares["value_i_rank"].apply(lambda x: "Vainqueur " if x == 1 else f"{x}ème ")

    # Phrase à afficher dans le Dash
palmares["palmares_lbl"] = palmares["value_i_rank_lbl"] + palmares["Idpalmares_label"] + palmares["ID_race"] + " " + palmares["Annee"].astype(str)

print(palmares.shape)
palmares.head()


# Déduplication
palmares_d = palmares.drop_duplicates(subset=["Idpalmares_cyclist", "ID_race", "Idpalmares_type"])
print(palmares_d.shape)
palmares_d.head()


# Conservation de 3 lignes de palmarès par type de palmarès (général, points, montagne etc...)

palmares_d2 = palmares_d.groupby(['Idpalmares_cyclist', 'Idpalmares_type']).head(3).sort_values(by=["Idpalmares_cyclist"])
print(palmares_d2.shape)
palmares_d2.head(n=15)



# Affichage d'un émoji selon la ligne de palmarès
emojis = {
    "medaille_or": "🥇",
    "medaille_argent": "🥈",
    "medaille_bronze": "🥉",
    "coupe": "🏆",
    "maillot_a_pois": "❤️⚪",
    "maillot_vert": "💚",
    "maillot_blanc": "🤍",
    "arc-en-ciel": "🌈"
}

# Fonction pour ajouter les émoticônes en fonction des résultats
def ajouter_emoticone(row):
    if row['Idpalmares_type'] == "ETAPE":
        if row['value_i_rank'] == 1:
            return f"{emojis['medaille_or']} {row['palmares_lbl']}"
        elif row['value_i_rank'] == 2:
            return f"{emojis['medaille_argent']} {row['palmares_lbl']}"
        elif row['value_i_rank'] == 3:
            return f"{emojis['medaille_bronze']} {row['palmares_lbl']}"
    elif row['Idpalmares_type'] == "GENERAL_TEMPS" and row['value_i_rank'] == 1:
        return f"{emojis['coupe']} {row['palmares_lbl']}"
    elif row['Idpalmares_type'] == "GENERAL_MONTAGNE" and row['value_i_rank'] == 1:
        return f"{emojis['maillot_a_pois']} {row['palmares_lbl']}"
    elif row['Idpalmares_type'] == "GENERAL_POINTS" and row['value_i_rank'] == 1:
        return f"{emojis['maillot_vert']} {row['palmares_lbl']}"
    elif row['Idpalmares_type'] == "GENERAL_JEUNES" and row['value_i_rank'] == 1:
        return f"{emojis['maillot_blanc']} {row['palmares_lbl']}"
    elif row['Idpalmares_type'] == "GENERAL_TEMPS" and row['value_i_rank'] == 1 and row['ID_race'] == "World Championships":
        return f"{emojis['arc-en-ciel']} {row['palmares_lbl']}"
    return row['palmares_lbl']

# Appliquer la fonction pour modifier 'palmares_lbl'
palmares_d2['palmares_lbl'] = palmares_d2.apply(ajouter_emoticone, axis=1)

palmares_d2=palmares_d2.sort_values(by=["Idpalmares_cyclist","value_i_rank"],ascending=[True,True])

print(palmares_d2.shape)
palmares_d2.head(n=15)


# Création d'un rang de palmarès pour chaque cycliste
palmares_d2['palmares_rank'] = palmares_d2.groupby('Idpalmares_cyclist').cumcount() + 1

# Transformation en colonnes avec pivot
df_pivot = palmares_d2.pivot(index="Idpalmares_cyclist", columns="palmares_rank", values="palmares_lbl")

# Renommer les colonnes en palmares1, palmares2, ..., palmares10
df_pivot.columns = [f"palmares{i}" for i in df_pivot.columns]

# Remettre l'index en colonne
df_pivot = df_pivot.reset_index()

# Si moins de 15 colonnes, on complète avec des colonnes vides
for i in range(1, 16):  # De palmares1 à palmares15
    if f"palmares{i}" not in df_pivot.columns:
        df_pivot[f"palmares{i}"] = None  # Ou ""

# Trier les colonnes pour respecter l'ordre
df_pivot = df_pivot[['Idpalmares_cyclist'] + [f"palmares{i}" for i in range(1, 16)]]

# Affichage du DataFrame final
print(df_pivot.shape)
df_pivot



print(df.shape)
df=pd.merge(df,df_pivot,on="Idpalmares_cyclist",how="left")

print(df.shape)
df.head(n=10)




# Calcul des moyennes globales de toutes les caractéristiques
moyennes_globale = df[["carac_plaine", "carac_montagne", "carac_paves", "carac_clm", "carac_sprint", "carac_endurance"]].mean().tolist()

# Dictionnaire des chemins d'images pour chaque équipe (Windows)
team_images = {
        "Groupama - FDJ": "groupama_fdj.jpg",
        "AG2R Citroën Team": "ag2r.jpg",
        "Team Arkéa - Samsic": "arkea.jpg",
        "Astana Qazaqstan Team": "astana.jpg",
        "Movistar Team": "movistar.jpg",
        "Alpecin-Deceuninck": "Alpecin-Deceuninck.jpg",
        "B&B HOTELS KTM": "b&b.jpg",
        "BORA - hansgrohe": "BORA_hansgrohe.jpg",
        "Bahrain Victorious": "bahrain_victorious.jpg",
        "Caja Rural - Seguros RGA": "Caja_Rural.jpg",
        "Cofidis": "cofidis.jpg",
        "EF Education-EasyPost": "education_first.jpg",
        "INEOS Grenadiers": "ineos.jpg",
        "Intermarché-Wanty-Gobert Matériaux": "intermarche_wanty.jpg",
        "Israël - Premier Tech": "israel_premier_tech.jpg",
        "Team BikeExchange - Jayco": "Jayco.jpg",
        "Team Jumbo - Visma": "jumbo_visma.jpg",
        "Lotto Soudal": "lotto_soudal.jpg",
        "Movistar Team": "movistar.jpg",
        "Quick-Step - Alpha Vinyl": "quick_step.jpg",
        "Team DSM": "Team_DSM.jpg",
        "Trek - Segafredo": "trek_segafredo.jpg",
        "UAE Team Emirates": "UAE.jpg",
        "Team TotalEnergies": "TotalEnergies.jpg",
        "Uno-X Pro Cycling Team": "uno_x.jpg",
        "Burgos HD": "burgos.jpg",
        "Team Arkéa - Samsic": "arkea.jpg",
        "Euskaltel - Euskadi": "Euskaltel.jpg"
        
}

# Création de l'application Dash
app = dash.Dash(__name__)

background_image = dash.get_asset_url("fonds_page.jpeg")
uci_logo = dash.get_asset_url("logo_uci.jpg")

app.layout = html.Div(
    style={
        'background-image': f'url("{background_image}")',
        'background-size': 'cover',
        'background-position': 'center',
        'height': '100vh',
        'width': '100vw',
        'padding': '20px'
    },
    children=[
        # Bandeau du haut
        html.Div(
            style={
                'display': 'flex',
                'alignItems': 'center',
                'justifyContent': 'space-between',
                'backgroundColor': '#333',
                'color': 'white',
                'padding': '10px',
                'border-radius': '10px',
                'margin-bottom': '20px'
            },
            children=[
                html.Img(src=uci_logo, style={'height': '50px', 'margin-right': '20px'}),

                # Bloc d'informations du coureur
                html.Div(id="cyclist-info", style={'display': 'flex', 'gap': '10px', 'flex-wrap': 'wrap'}),

                # Image du coureur
                html.Img(id="team-logo", src="", style={'height': '80px','border-radius': '10px','position': 'relative','right': '80px'})
            ]
        ),

        # Menus déroulants pour filtrer et sélectionner un coureur
        html.Div(
            style={'display': 'flex', 'justifyContent': 'center', 'gap': '20px', 'margin-bottom': '20px'},
            children=[
                # Filtre par type de coureur
                dcc.Dropdown(
                    id='filter-dropdown',
                    options=[{'label': label, 'value': label} for label in df['HAC_label'].unique()] + [{'label': "Tous les coureurs", 'value': "all"}],
                    placeholder="Filtrer par type de coureur...",
                    style={'width': '250px', 'color': 'black'}
                ),

                # Sélection d’un coureur
                dcc.Dropdown(
                    id='cyclist-dropdown',
                    options=[{'label': name, 'value': name} for name in df['Idpalmares_cyclist'].unique()] + [{'label': "Tous les coureurs", 'value': "all"}],
                    placeholder="Sélectionner un coureur...",
                    style={'width': '250px', 'color': 'black'}
                ),
            ]
        ),

        # Tableau des statistiques du coureur sélectionné
        html.Div(
            style={'display': 'flex', 'justifyContent': 'center','position': 'absolute','right': '120px'},
            children=[
                dash_table.DataTable(
                    id='cyclist-table',
                    columns=[
                        {"name": "Nom", "id": "Idpalmares_cyclist"},
                        {"name": "Victoires", "id": "gene_i_nb_victory"},
                        {"name": "Courses favorites", "id": "gene_ilist_flkDfavorite_races"}
                    ],
                    data=df.iloc[:3].to_dict('records'),  # 3 premières lignes par défaut
                    style_table={'width': '500px', 'margin-top': '10px'},
                    style_cell={
                        'textAlign': 'center',
                        'backgroundColor': 'black',
                        'color': 'white',
                        'padding': '5px',
                        'fontSize': '14px',
                        'border': '1px solid white'
                    },
                    style_header={
                        'backgroundColor': 'black',
                        'color': 'white',
                        'fontWeight': 'bold',
                        'border': '1px solid white'
                    }
                ),
            ]
        ),
        # Graphique Radar
                # Graphique Radar
        html.Div(
            style={
                'position': 'absolute',  # Position fixe en bas à droite
                'bottom': '0px',
                'right': '10px',
                'width': '350px',  # Taille réduite
                'height': '250px',
                'backgroundColor': 'black',  # Fond noir
                'padding': '10px',
                'borderRadius': '10px',  # Coins arrondis
                'boxShadow': '0px 0px 10px rgba(255, 255, 255, 0.3)',  # Légère ombre blanche
                'display': 'flex',
                'justifyContent': 'center',
                'alignItems': 'center'
            },
            children=[
                dcc.Graph(
                    id='radar-chart',
                    config={'displayModeBar': False},  # Cache la barre d'options
                    style={'width': '100%', 'height': '100%'}
                )
            ]
        ),
        
        # Encart des Palmarès sous le radar
        html.Div(
            id='palmares-box',
            style={
                'position': 'absolute',
                'bottom': '0px',        # Aligné en bas
                'left': '20px',        # Décalé pour être sous le radar
                'width': '500px',        # Largeur ajustable
                'backgroundColor': 'black',
                'color': 'white',
                'border': '2px solid white',
                'borderRadius': '10px',
                'padding': '10px',
                'textAlign': 'left',
                'fontSize': '14px',
                'whiteSpace': 'pre-line'  # Permet de garder les sauts de ligne
            }
        )

    ]
)

# Callback pour mettre à jour les infos du bandeau et la photo
@app.callback(
    [Output('cyclist-info', 'children'),
     Output('team-logo', 'src')],
    [Input('cyclist-dropdown', 'value')]
)
def update_bandeau(selected_cyclist):
    if selected_cyclist and selected_cyclist != "all":
        cyclist_data = df[df['Idpalmares_cyclist'] == selected_cyclist].iloc[0]
    else:
        cyclist_data = df.iloc[0]  # Par défaut, premier coureur du DataFrame

    # Charger l'image de l'équipe
    team_image_path = dash.get_asset_url(team_images.get(cyclist_data['ID_team'], 'logo_uci.jpg'))

    info_block = [
        html.Span(f"🏆 {cyclist_data['Idpalmares_cyclist']} | ", style={'font-size': '18px', 'font-weight': 'bold'}),
        html.Span(f"🎂 {cyclist_data['Age']} ans | "),
        html.Span(f"⏳ {cyclist_data['Annees_exp']} ans exp. | "),
        html.Span(f"🌍 {cyclist_data['fklDregion']} | "),
        html.Span(f"{cyclist_data['HAC_label']}")
    ]

    return info_block, team_image_path

# Callback pour filtrer les coureurs en fonction du type sélectionné
@app.callback(
    Output('cyclist-dropdown', 'options'),
    Input('filter-dropdown', 'value')
)
def update_cyclist_dropdown(selected_label):
    if selected_label and selected_label != "all":
        filtered_df = df[df['HAC_label'] == selected_label]
        return [{'label': name, 'value': name} for name in filtered_df['Idpalmares_cyclist']] + [{'label': "Tous les coureurs", 'value': "all"}]
    return [{'label': name, 'value': name} for name in df['Idpalmares_cyclist']] + [{'label': "Tous les coureurs", 'value': "all"}]

# Callback pour mettre à jour le tableau
@app.callback(
    Output('cyclist-table', 'data'),
    Input('cyclist-dropdown', 'value')
)
def update_table(selected_cyclist):
    if selected_cyclist and selected_cyclist != "all":
        filtered_df = df[df['Idpalmares_cyclist'] == selected_cyclist]
    else:
        filtered_df = df.head(3)

    return filtered_df.to_dict('records')

# Callback pour mettre à jour le graphique radar
@app.callback(
    Output('radar-chart', 'figure'),
    Input('cyclist-dropdown', 'value')
)


def update_radar_chart(selected_cyclist):
    if selected_cyclist and selected_cyclist != "all":
        cyclist_data = df[df['Idpalmares_cyclist'] == selected_cyclist].iloc[0]
    else:
        cyclist_data = df.iloc[0]  # Par défaut, premier coureur du DataFrame

    categories = ["carac_plaine", "carac_montagne", "carac_paves", "carac_clm", "carac_sprint", "carac_endurance"]
    values = [cyclist_data[cat] for cat in categories]
    values_moyenne = moyennes_globale

    radar_chart = go.Figure()

    # Trace du coureur sélectionné (en bleu)
    radar_chart.add_trace(go.Scatterpolar(
        r=values + [values[0]], 
        theta=categories + [categories[0]], 
        fill='toself', 
        name=f'{selected_cyclist}', 
        line=dict(color='blue')
    ))

    # Trace de la moyenne globale (en rouge, en pointillés)
    radar_chart.add_trace(go.Scatterpolar(
        r=values_moyenne + [values_moyenne[0]], 
        theta=categories + [categories[0]], 
        fill='toself', 
        name='Peloton', 
        line=dict(color='red', dash='dot')
    ))

    # Personnalisation du style
    radar_chart.update_layout(
        polar=dict(
            bgcolor="black",  # Fond du graphe en noir
            radialaxis=dict(visible=True, range=[0, 100], gridcolor="gray", color="white")
        ),
        showlegend=True,  # Affiche la légende
        legend=dict(
            orientation="h",  # Légende horizontale
            yanchor="top", y=-0.3,  # Position sous le radar
            xanchor="center", x=0.5,
            font=dict(color="white")  # Texte de la légende en blanc
        ),
        margin=dict(l=20, r=20, t=20, b=50),  # Marge ajustée pour la légende
        plot_bgcolor="black",  # Fond du graphique en noir
        paper_bgcolor="black",  # Fond extérieur en noir
        font=dict(color="white")  # Texte global en blanc
    )

    return radar_chart

@app.callback(
    Output('palmares-box', 'children'),
    Input('cyclist-dropdown', 'value')
)
def update_palmares(selected_cyclist):
    if selected_cyclist and selected_cyclist != "all":
        cyclist_data = df[df['Idpalmares_cyclist'] == selected_cyclist].iloc[0]
    else:
        cyclist_data = df.iloc[0]  # Par défaut, premier coureur

    # Liste des colonnes palmarès
    palmares_cols = [f'palmares{i}' for i in range(1, 16)]
    
    # Récupération des valeurs non nulles
    palmares_values = [str(cyclist_data[col]) for col in palmares_cols if pd.notna(cyclist_data[col]) and cyclist_data[col] != ""]

    # Si aucun palmarès, afficher un message par défaut
    if not palmares_values:
        return html.Div("Coureur sans palmarès", style={'fontWeight': 'bold'})

    # Affichage en ligne par ligne
    return html.Div([html.Div(p, style={'margin-bottom': '5px'}) for p in palmares_values])


# Définir server pour Gunicorn
server = app.server  

# Récupération du port attribué par Render (ou 8050 par défaut en local)
port = int(os.environ.get("PORT", 8050))

if __name__ == "__main__":
    app.run_server(debug=False, host="0.0.0.0", port=port)
