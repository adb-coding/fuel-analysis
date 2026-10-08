from dash import Output, Input, callback, html, dcc, register_page
import dash_bootstrap_components as dbc
from helper import extract_countries, calculate_price_by_country, calculate_date_price
import plotly.express as px
import pandas as pd


# register the page
register_page(__name__, name="Map", path="/map")

countries = extract_countries()
# last_price = calculate_last_price(countries)
price_by_country = calculate_price_by_country(countries)


iso2_to_iso3 = {
    "AT": "AUT", "BE": "BEL", "BG": "BGR", "CY": "CYP", "CZ": "CZE",
    "DE": "DEU", "DK": "DNK", "EE": "EST", "ES": "ESP", "FI": "FIN",
    "FR": "FRA", "GR": "GRC", "HR": "HRV", "HU": "HUN", "IE": "IRL",
    "IT": "ITA", "LT": "LTU", "LU": "LUX", "LV": "LVA", "MT": "MLT",
    "NL": "NLD", "PL": "POL", "PT": "PRT", "RO": "ROU", "SE": "SWE",
    "SI": "SVN", "SK": "SVK"
}

# last_price['ISO3'] = [iso2_to_iso3.get(i) for i in last_price['country']]
slider_marks = {
    i: price_by_country.iloc[i]['Date'].date()
    for i in range(0, len(price_by_country), 50)
}

layout = dbc.Container([
    html.Div([
        html.H1(
            id='title'
        , style={'textAlign':'center'}),
        dcc.Store(id='last-price'),
        html.Div([
            dbc.Row([
            dbc.Col([
                dbc.Card([
                    html.H4("Average Diesel Price"),
                    html.P(id='card-diesel-price', className="fw-bold fs-4 mb-0")
                ], style={"padding":"2px", "textAlign":"center"})
            ], width=3),
            dbc.Col([
                dbc.Card([
                    html.H4('Average Gasoline Price'),
                    html.P(id='card-gas-price', className="fw-bold fs-4 mb-0")
                ], style={"padding":"2px", "textAlign":"center"})
            ], width=3),
                dbc.Col([
                dbc.Card([
                    html.H4('Increase of Diesel Price'),
                    html.P(id='card-diesel-increase', className="fw-bold fs-4 mb-0")
                ], style={"padding":"2px", "textAlign":"center"})
            ], width=3), 
                dbc.Col([
                dbc.Card([
                    html.H4('Increase of Gasoline Price'),
                    html.P(id='card-gas-increase', className="fw-bold fs-4 mb-0")
                ], style={"padding":"2px", "textAlign":"center"})
            ], width=3), 
            ], style={'padding-bottom':'8px'}),
            html.Div([
                dbc.Row([
                    dcc.Dropdown(['Diesel','Gas','Diesel Pre-tax','Gas Pre-tax','Diesel tax component','Gas tax component','Diesel % change','Gas % change'],
                                'Diesel', id="map-dropdown", multi=False, searchable=False,
                                className="ms-6 mb-3"),
                    dcc.Slider(min=0, max=price_by_country.index.max(), step=1, marks=slider_marks, 
                            value=price_by_country.index.max(), id='date-slider',
                            tooltip={"placement":"bottom","always_visible":False},
                            className="mb-3"),
                ]),
                dbc.Row([
                    dbc.Col([
                        dcc.Graph(id='plot1')
                    ], width=6),
                    dbc.Col([
                        dcc.Checklist(options=[{'label':'Decompose price components','value':'decompose'}], id='checkbox'),
                        dcc.Graph(id='plot2')
                    ], width=6)
                ])
            ])
        ])
    ])
], fluid=True)

@callback(
    Output('title','children'),
    Input('date-slider','value')
)
def update_title(value):
    date = price_by_country.iloc[value]['Date']
    # date = slider_marks.get(value)
    title_str = f"Price of Fuel at {date.date()}"
    return title_str


@callback(
    Output('last-price','data'),
    Output('card-diesel-price','children'),
    Output('card-gas-price','children'),
    Output('card-diesel-increase','children'),
    Output('card-gas-increase','children'),
    Input('date-slider','value')
)
def update_last_price(value):
    last_price = calculate_date_price(countries, value, price_by_country)

    last_price['ISO3'] = [iso2_to_iso3.get(i) for i in last_price['country']]
    diesel_price = round(last_price.loc[last_price['country'] == 'EU']['Diesel'], 3)
    gas_price = round(last_price.loc[last_price['country'] == 'EU']['Gas'], 3)
    diesel_increase =  round(last_price.loc[last_price['country'] == 'EU']['Diesel_change']*100, 2)
    gas_increase = round(last_price.loc[last_price['country'] == 'EU']['Gas_change']*100, 2)

    diesel_price = f"{diesel_price.values[0]} €"
    gas_price = f"{gas_price.values[0]} €"
    diesel_increase = f"{diesel_increase.values[0]:+} %"
    gas_increase = f"{gas_increase.values[0]:+} %"


    return last_price.to_dict('records'), diesel_price, gas_price, diesel_increase, gas_increase

value_map = {
    'Gas':'Gas',
    'Diesel':'Diesel',
    'Gas Pre-tax':'Gas_pretax',
    'Diesel Pre-tax':'Diesel_pretax',
    'Gas tax component':'Gas_tax_comp',
    'Diesel tax component':'Diesel_tax_comp',
    'Gas % change':'Gas_change',
    'Diesel % change':'Diesel_change'
}

@callback(
    Output('plot1', 'figure'),
    Input('map-dropdown','value'),
    Input('last-price','data'),
)
def compute_map(value, data):
    
    df = pd.DataFrame(data)

    if 'Gas' in value:
        color = 'greens'
    else:
        color = 'oranges'

    display_value = value_map.get(value)

    fig_map = px.choropleth(
        df,
        locations='ISO3',
        locationmode='ISO-3',
        color=display_value,
        scope='europe',
        color_continuous_scale=color
    )
    fig_map.update_layout(
        margin={"r":0, "l":1, "t":1, "b":2},
        height=600,
    )

    return fig_map

@callback(
        Output('plot2','figure'),
        Input('map-dropdown','value'),
        Input('last-price', 'data'),
        Input('checkbox','value')
)
def compute_bar_chart(value, data, checkbox):

    df = pd.DataFrame(data)

    display_value = value_map.get(value)


    if 'Gas' in value:
        color = ["green"]
    else:
        color = ["orange"]

    if checkbox and 'decompose' in checkbox:

        if 'Diesel' in value:
            x_series = ['Diesel_pretax','Diesel_tax_comp']
        else:
            x_series = ['Gas_pretax','Gas_tax_comp']
        fig_last_price = px.bar(
            df.sort_values(by=display_value.split("_")[0]), y='country', x=x_series,
            orientation='h',
            height=600
        )
        fig_last_price.update_layout(
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=-0.2,

            )
        )

    else:

        fig_last_price = px.bar(
            df.sort_values(by=display_value), x=display_value, y='country', orientation="h", 
            barmode="group",
            color_discrete_sequence=color*len(df),
            labels={'value':'Fuel'},
            height=600
        )

    fig_last_price.update_layout(
        bargap=0.2,
        bargroupgap=0.3
    )


    return fig_last_price

