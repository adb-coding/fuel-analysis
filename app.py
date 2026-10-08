from dash import Dash, dcc, html, Input, Output, callback, page_registry, page_container
import dash_bootstrap_components as dbc
from helper import extract_date


app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP, dbc.icons.FONT_AWESOME])

theme = {
    'dark':True,
    
}

navbar = dbc.Navbar(
    dbc.Container([
        dbc.NavbarBrand([html.I(className="fa-solid fa-droplet"), " European Fuel Prices"], href="/"),
        dbc.Nav([
            dbc.NavItem(dbc.NavLink(
                [html.I(className="fa-solid fa-arrow-trend-up ms-2"), ' Price Chart'], href="/", active="exact")),
            dbc.NavItem(dbc.NavLink(
                [html.I(className="fa-solid fa-map ms-2"), ' Map'], href="/map", active="exact")),
            dbc.NavItem(dbc.NavLink(
                [html.I(className="fa-regular fa-calendar ms-2"), ' Events'], href="/events", active="exact")),
        ],
        navbar=True,
        className="ms-auto d-flex align-items-center gap-2",
        pills=True
        ),], 
        fluid=True),

    className="border-bottom shadow-sm py-2 mb-4 bg-dark"
)

footer = html.Footer([
    html.Hr(className='my-4'),
    dbc.Container(
    children=[
        html.Div([
            dbc.Row([
                dbc.Col([
                    html.A(['Adb Coding | Github', html.I(className="fa-brands fa-github ms-2 fa-xl", id="help-icon", style={"cursor":"pointer","color":"#0d6efd"})],
                    href="/", className="text-decoration-none")], align="center"),
                dbc.Col(html.P(id="last-update"), align="center"),
                dbc.Col([
                    html.P([
                        "Data source: ",
                        html.A("European Commission", href="https://energy.ec.europa.eu/data-and-analysis/weekly-oil-bulletin_en",
                               target="_blank", className="text-decoration-none")
                    ], className="mb-0"),
                ], width=12, md=4),
            ])
        ], className="ms-6"),
    ],
    className="footer",
    fluid=True
    ),        
])
    
@callback(
    Output('last-update','children'),
    Input('last-update','id')
)
def update_last_date(_):
    last_date = "Last update: " + extract_date()

    return last_date


app.layout = html.Div([   
    navbar,
    page_container,
    footer
])


if __name__ == '__main__':
    app.run(debug=True)