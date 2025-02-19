import dash
from dash import dcc, html, dash_table, Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Création du DataFrame
data = {
    "IDcyclist": [366, 5963, 5962, 6688, 2544, 2696, 2695, 2543, 2542, 2450,
                  3053, 3065, 2801, 3033, 632, 703, 927, 802, 872],
    "Prenom_nom": ["Dupont H.", "Vincent L.", "Gaudu D.", "Paret-Peintre A.", "Démare A.",
                   "Sinkeldam R.", "Ludvigsson T.", "Bardet R.", "Molard R.", "Bagdonas G.",
                   "Vuillermoz A.", "Reichenbach S.", "Preidler G.", "Domont A.", "Bonnet W.",
                   "Morabito S.", "Bakelants J.", "Guarnieri J.", "Dumoulin S."],
    "ID_team": ["Ag2r La Mondiale", "Groupama - FDJ", "Groupama - FDJ", "Ag2r La Mondiale", "Groupama - FDJ",
                "Groupama - FDJ", "Groupama - FDJ", "Ag2r La Mondiale", "Groupama - FDJ", "Ag2r La Mondiale",
                "Ag2r La Mondiale", "Groupama - FDJ", "Groupama - FDJ", "Ag2r La Mondiale", "Groupama - FDJ",
                "Groupama - FDJ", "Ag2r La Mondiale", "Groupama - FDJ", "Ag2r La Mondiale"],
    "Date_de_naissance": [29538, 35009, 35348, 35122, 33476, 32548, 33291, 33186, 32768, 31407,
                          32295, 32656, 33041, 33092, 30127, 30346, 31457, 32003, 29453],
    "Popularite": [44.19, 18.72, 40.53, 12.25, 55.53, 33.20, 30.20, 76.20, 35.53, 20.53,
                   65.20, 39.87, 20.53, 14.82, 41.20, 34.87, 63.20, 25.20, 60.20],
    "carac_plaine": [64, 64, 68, 62, 79, 75, 73, 69, 71, 76, 66, 69, 70, 65, 74, 74, 73, 74, 69],
    "carac_montagne": [75, 74, 77, 67, 59, 55, 72, 82, 72, 58, 76, 78, 72, 69, 55, 75, 72, 55, 62],
    "carac_paves": [55, 62, 58, 60, 77, 76, 60, 65, 55, 67, 57, 60, 55, 54, 70, 66, 64, 68, 63],
    "carac_clm": [59, 65, 63, 61, 67, 65, 76, 67, 64, 68, 63, 70, 72, 60, 70, 72, 69, 57, 59],
    "carac_sprint": [61, 63, 56, 62, 80, 74, 59, 63, 63, 72, 62, 60, 65, 57, 70, 60, 59, 74, 75],
    "carac_endurance": [68, 63, 70, 60, 78, 69, 66, 77, 74, 69, 71, 70, 67, 63, 73, 67, 70, 72, 69]
}

df = pd.DataFrame(data)
df["carac_moy"] = df.iloc[:, 5:].mean(axis=1).round(2)  # Moyenne des caractéristiques

# Initialisation de l'application Dash
app = dash.Dash(__name__)

# Mise en page de l'application
app.layout = html.Div([
    html.H1("📊 Dashboard des Cyclistes"),
    
    # Sélecteur d'ID Cyclist
    dcc.Dropdown(
        id="cyclist-dropdown",
        options=[{"label": f"{row.Prenom_nom} ({row.IDcyclist})", "value": row.IDcyclist} for _, row in df.iterrows()],
        value=df.loc[0, "IDcyclist"],  # Valeur par défaut
        clearable=False
    ),

    # Tableau des 5 premières lignes
    dash_table.DataTable(
        id="table-data",
        data=df.head(5).to_dict("records"),
        columns=[{"name": col, "id": col} for col in df.columns],
        page_size=5,
        style_table={"overflowX": "auto"},
        style_header={"backgroundColor": "lightgrey", "fontWeight": "bold"},
        style_cell={"textAlign": "left"}
    ),
    
    # Graphique radar
    dcc.Graph(id="radar-chart"),
    
    # Encadré Profil Cycliste
    html.Div(id="profile-card", style={"border": "1px solid black", "padding": "10px", "margin-top": "20px"})
])

# Callback pour mettre à jour le graphique radar et l'encart profil
@app.callback(
    [Output("radar-chart", "figure"), Output("profile-card", "children")],
    [Input("cyclist-dropdown", "value")]
)
def update_chart_and_profile(selected_id):
    cyclist_data = df[df["IDcyclist"] == selected_id].iloc[0]
    
    # Graphique Radar
    categories = ["carac_plaine", "carac_montagne", "carac_paves", "carac_clm", "carac_sprint", "carac_endurance"]
    values = cyclist_data[categories].tolist()
    values += values[:1]  # Boucler sur le premier point pour fermer le radar

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories + [categories[0]],  # Boucle sur la première valeur
        fill="toself",
        name=f"{cyclist_data.Prenom_nom}"
    ))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True)), showlegend=True)

    # Encadré Profil
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
