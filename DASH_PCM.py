import dash
from dash import dcc, html, dash_table, Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

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

df=df[['IDcyclist','Nom','Prenom','Prenom_nom','ID_team','fklDregion','Date_de_naissance','Popularite','value_f_potentiel','taille_coureur','poids_coureur','carac_plaine','carac_montagne','carac_descente','carac_paves','carac_clm','carac_prologue','carac_sprint','carac_acceleration','carac_endurance','carac_resistance','carac_recuperation','carac_vallon','carac_baroudeur','prendra_sa_retraite','Coureur_champion','gene_ilist_flkDfavorite_races','value_i_yearneopro','gene_i_nb_victory','gene_i_nb_tdf','gene_i_nb_giro','gene_i_nb_vuelta','gene_i_nb_sanremo','gene_i_nb_flandres','gene_i_nb_roubaix','gene_i_nb_liege','gene_i_nb_lombardia']]

# Convertir Date_de_naissance en format date YYYY-MM-DD
df["Date_de_naissance"] = pd.to_datetime(df["Date_de_naissance"])
#df["Date_de_naissance"] = df["Date_de_naissance"].dt.strftime('%Y-%m-%d')

# Calcul du niveau moyen par coureur
df["carac_moy"]=round(((df['carac_plaine'] + df['carac_montagne'] + df['carac_descente'] +
df['carac_paves'] + df['carac_clm'] + df['carac_prologue'] + df['carac_sprint'] +
df['carac_acceleration'] + df['carac_endurance'] + df['carac_resistance'] + 
df['carac_recuperation'] + df['carac_vallon'] + df['carac_baroudeur'])/(13)),2)

print(df.shape)
print(df["Date_de_naissance"].dtype)
df.head()

df["carac_moy"] = df.iloc[:, 5:].mean(axis=1).round(2)  # Moyenne des caractéristiques

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
