import dash
from dash import dcc, html, dash_table, Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# Charger le fichier Excel depuis un chemin relatif ou en ligne
file_path = "02_INPUTS/_20230301_inputs_projet_pcm.xlsx"

# Vérification que le fichier existe
if not os.path.exists(file_path):
    raise FileNotFoundError(f"Le fichier {file_path} est introuvable !")

# Charger les données Excel
df = pd.read_excel(file_path, sheet_name="CYCLISTS")

df=df[['IDcyclist','Nom','Prenom','Prenom_nom','ID_team','fklDregion','Date_de_naissance','Popularite','value_f_potentiel','taille_coureur','poids_coureur','carac_plaine','carac_montagne','carac_descente','carac_paves','carac_clm','carac_prologue','carac_sprint','carac_acceleration','carac_endurance','carac_resistance','carac_recuperation','carac_vallon','carac_baroudeur','prendra_sa_retraite','Coureur_champion','gene_ilist_flkDfavorite_races','value_i_yearneopro','gene_i_nb_victory','gene_i_nb_tdf','gene_i_nb_giro','gene_i_nb_vuelta','gene_i_nb_sanremo','gene_i_nb_flandres','gene_i_nb_roubaix','gene_i_nb_liege','gene_i_nb_lombardia']]

# Ajout d'une colonne "carac_moy" pour l'analyse
df["carac_moy"] = round(((df['carac_plaine'] + df['carac_montagne'] + df['carac_descente'] +
                          df['carac_paves'] + df['carac_clm'] + df['carac_prologue'] + df['carac_sprint'] +
                          df['carac_acceleration'] + df['carac_endurance'] + df['carac_resistance'] +
                          df['carac_recuperation'] + df['carac_vallon'] + df['carac_baroudeur']) / 13), 2)

# Convertir Date_de_naissance en format date YYYY-MM-DD
df["Date_de_naissance"] = pd.to_datetime(df["Date_de_naissance"])
#df["Date_de_naissance"] = df["Date_de_naissance"].dt.strftime('%Y-%m-%d')


# Initialisation de l'application Dash
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("📊 Dashboard des Cyclistes", style={"textAlign": "center", "color": "white"}),
    
    dcc.Dropdown(
        id="cyclist-dropdown",
        options=[{"label": f"{row.Prenom_nom} ({row.IDcyclist})", "value": row.IDcyclist} for _, row in df.iterrows()],
        value=df.loc[0, "IDcyclist"],
        clearable=False,
        style={"width": "50%", "margin": "auto"}
    ),
    
    dash_table.DataTable(
        id="table-data",
        data=df.to_dict("records"),
        columns=[{"name": col, "id": col} for col in df.columns],
        page_size=5,  # ✅ Limitation à 5 lignes affichées
        style_table={"overflowX": "auto"},
        style_header={"backgroundColor": "lightgrey", "fontWeight": "bold"},
        style_cell={"textAlign": "left"}
    ),

    dcc.Graph(id="radar-chart"),

    html.Div(id="profile-card", style={
        "backgroundColor": "#065464",  # ✅ Fond bleu foncé
        "padding": "20px",
        "borderRadius": "10px",
        "color": "white",
        "width": "50%",
        "margin": "auto",
        "marginTop": "20px",
        "textAlign": "center"
    })
], style={"backgroundColor": "#85c3cf", "padding": "20px", "minHeight": "100vh"})

@app.callback(
    [Output("radar-chart", "figure"), Output("profile-card", "children")],
    [Input("cyclist-dropdown", "value")]
)
def update_chart_and_profile(selected_id):
    cyclist_data = df[df["IDcyclist"] == selected_id].iloc[0]
    categories = ["carac_plaine", "carac_montagne", "carac_paves", "carac_clm", "carac_sprint", "carac_endurance"]
    values = cyclist_data[categories].tolist()
    values += values[:1]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories + [categories[0]],
        fill="toself",
        name=f"{cyclist_data.Prenom_nom}"
    ))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True)), showlegend=True)

    profile_info = html.Div([
        html.H3(f"Profil : {cyclist_data.Prenom_nom}"),
        html.P(f"🏆 Équipe : {cyclist_data.ID_team}"),
        html.P(f"📅 Naissance : {cyclist_data.Date_de_naissance}"),
        html.P(f"⭐ Popularité : {cyclist_data.Popularite}"),
        html.P(f"📊 Moyenne caractéristiques : {cyclist_data.carac_moy}")
    ])

    return fig, profile_info

# Définir server pour Gunicorn
server = app.server  

# Récupération du port attribué par Render (ou 8050 par défaut en local)
port = int(os.environ.get("PORT", 8050))

if __name__ == "__main__":
    app.run_server(debug=False, host="0.0.0.0", port=port)
