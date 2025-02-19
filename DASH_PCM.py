import dash
from dash import html, dash_table
import pandas as pd
import os

# Charger le fichier Excel depuis un chemin relatif ou en ligne
file_path = "02_INPUTS/_20230301_inputs_projet_pcm.xlsx"

# Vérification que le fichier existe
if not os.path.exists(file_path):
    raise FileNotFoundError(f"Le fichier {file_path} est introuvable !")

# Charger les données Excel
df = pd.read_excel(file_path, sheet_name="CYCLISTS")

# Ajout d'une colonne "carac_moy" pour l'analyse
df["carac_moy"] = round(((df['carac_plaine'] + df['carac_montagne'] + df['carac_descente'] +
                          df['carac_paves'] + df['carac_clm'] + df['carac_prologue'] + df['carac_sprint'] +
                          df['carac_acceleration'] + df['carac_endurance'] + df['carac_resistance'] +
                          df['carac_recuperation'] + df['carac_vallon'] + df['carac_baroudeur']) / 13), 2)

# Création de l'application Dash
app = dash.Dash(__name__)

# Mise en page de l'application
app.layout = html.Div([
    html.H1("Tableau interactif - Classification des Cyclistes"),
    dash_table.DataTable(
        id='table-data',
        data=df.to_dict('records'),
        columns=[{"name": col, "id": col} for col in df.columns],
        page_size=10,
        sort_action="native",
        filter_action="native",
        style_table={'overflowX': 'auto'},
        style_header={'backgroundColor': 'lightgrey', 'fontWeight': 'bold'},
        style_cell={'textAlign': 'left'}
    )
])

# Définir server pour Gunicorn
server = app.server  

# Récupération du port attribué par Render (ou 8050 par défaut en local)
port = int(os.environ.get("PORT", 8050))

if __name__ == "__main__":
    app.run_server(debug=False, host="0.0.0.0", port=port)
