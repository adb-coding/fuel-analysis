from helper import load_df, extract_countries, calculate_last_price, construct_average, calculate_date_price
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, html, dcc, Input, Output, callback, register_page
import dash_bootstrap_components as dbc
import datetime
import pandas as pd


countries = extract_countries()

register_page(__name__, name="Overview", path="/overview")

color_map = {
    "EU": "#0909BE",
    "AT": "#FA0101",
    "BE": "#553811",
    "BG": "#404040",
    "CY": "#0000FF",
    "CZ": "#008000",
    "DE": "#B39B13",
    "DK": "#FF0000",
    "EE": "#000000",
    "ES": "#FFFF00",
    "FI": "#C0B6B6",
    "FR": "#180267",
    "GR": "#3428A7",
    "HR": "#FF8C00",
    "HU": "#00FFFF",
    "IE": "#22C91C",
    "IT": "#1B5FDD",
    "LT": "#0F3A0B",
    "LU": "#12A9CF",
    "LV": "#7CFC00",
    "MT": "#925420",
    "NL": "#E0850D",
    "PL": "#911616",
    "PT": "#097E09",
    "RO": "#841188",
    "SE": "#B49900",
    "SI": "#00FF00",
    "SK": "#FF00FF"
}

COLORS = {
    "country": "#2563A6",
    "eu": "#159A9C",
    "before": "#91A7B8",
    "recent": "#2563A6",
    "pretax": "#75B9D6",
    "tax": "#176B75",
    "text": "#243447",
    "muted": "#66788A",
    "grid": "#E8EEF3",
}


def style_figure(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="Arial, sans-serif",
            color=COLORS["text"],
            size=12
        ),
        legend=dict(
            title_text="",
            font=dict(color=COLORS['muted']),
        ),
        margin=dict(l=15, r=15, b=15, t=15)
    )

    fig.update_xaxes(
        showgrid=True,
        gridcolor=COLORS['grid'],
        zeroline=False
    )

    fig.update_yaxes(showgrid=True,
                     gridcolor=COLORS['grid'],
                     zeroline=False)

    return fig


layout = dbc.Container([
    # titles
    html.Div([
        html.H2(
            "Fuel prices in context"
        ),
        html.H4("How has the cost of a tank changed?")
    ]),
    # Filters and dropdown menus
    html.Div([
        dbc.Row([
            dbc.Col([
                html.Span("Select Country"),
                dcc.Dropdown(countries, 'IT', id="dropdown-selection", multi=False, searchable=True, style={'padding':8, 'flex':1}),
            ], width=3
            ),
            dbc.Col([
                html.Span("Select Fuel Type"),
                dcc.Dropdown(['Diesel','Gas'], 'Gas', id='fuel-selection', searchable=False, multi=False, style={'padding':8, 'flex': 1}),
            ],
                width=3
            ), 
            dbc.Col([
                html.Span("Select Price"),
                dcc.Dropdown(['Full Price','Pre-Tax Price','Tax Component'], 'Full Price', id='price-selection', searchable=False, multi=False, style={'padding':8, 'flex': 1}),
            ],
                width=3
            ), 
            dbc.Col([
                html.Span("Select Period"),
                dcc.DatePickerRange(id='price-date-picker', style={'padding':8, 'flex': 1}),
            ],
                width=3
            ),
        ]),
        ]),
    html.Div([
        dbc.Row([
        # Card 1
        dbc.Col([
            dbc.Card([
                dbc.CardBody(
                    html.Div([
                        html.Div(
                            html.I(className="fa-solid fa-gas-pump",
                                   style={"fontSize":"28px"}, **{"aria-hidden":"true"}),
                            className=(
                                "d-flex align-items-center justify-content-center "
                                "pe-3 me-3 border-end"
                            ),
                            style={
                                "minWidth":"60px",
                                "minHeight": "60px",
                            }
                        ),
                        html.Div([
                            html.P("Fuel price", className="mb-1 text-secondary"),
                            html.P(id="card-fuel-price", className="fw-bold fs-4 mb-0"),
                        ], className="text-start",
                        )
                    ], className="d-flex align-items-center")
                )
                ]),
            ], width=3),
        # Card 2
        dbc.Col([
            dbc.Card([
                dbc.CardBody(
                    html.Div([
                        html.Div(
                            html.I(className="fa-solid fa-coins",
                                   style={"fontSize":"28px"}, **{"aria-hidden":"true"}),
                            className=(
                                "d-flex align-items-center justify-content-center "
                                "pe-3 me-3 border-end"
                            ),
                            style={
                                "minWidth":"60px",
                                "minHeight": "60px",
                            }
                        ),
                        html.Div([
                            html.P("Tax component", className="mb-1 text-secondary"),
                            html.P(id="card-tax-component", className="fw-bold fs-4 mb-0"),
                        ], className="text-start",
                        )
                    ], className="d-flex align-items-center")
                )
                ]),
            ], width=3),
        # Card 3
        dbc.Col([
            dbc.Card([
                dbc.CardBody(
                    html.Div([
                        html.Div(
                            html.I(className="fa-solid fa-gauge-high",
                                   style={"fontSize":"28px"}, **{"aria-hidden":"true"}),
                            className=(
                                "d-flex align-items-center justify-content-center "
                                "pe-3 me-3 border-end"
                            ),
                            style={
                                "minWidth":"60px",
                                "minHeight": "60px",
                            }
                        ),
                        html.Div([
                            html.P("50-liter tank", className="mb-1 text-secondary"),
                            html.P(id="card-50-liter", className="fw-bold fs-4 mb-0"),
                        ], className="text-start",
                        )
                    ], className="d-flex align-items-center")
                )
                ]),
            ], width=3),
        # Card 4
        dbc.Col([
            dbc.Card([
                dbc.CardBody(
                    html.Div([
                        html.Div(
                            html.I(className="fa-solid fa-scale-balanced",
                                   style={"fontSize":"28px"}, **{"aria-hidden":"true"}),
                            className=(
                                "d-flex align-items-center justify-content-center "
                                "pe-3 me-3 border-end"
                            ),
                            style={
                                "minWidth":"60px",
                                "minHeight": "60px",
                            }
                        ),
                        html.Div([
                            html.P("Difference vs EU", className="mb-1 text-secondary"),
                            html.P(id="card-comparison", className="fw-bold fs-4 mb-0"),
                        ], className="text-start",
                        )
                    ], className="d-flex align-items-center")
                )
                ]),
            ], width=3),     
        ]),
    # Main section
    dcc.Store(id='last-price-df'),
    dcc.Store(id='df-data'),
    dcc.Store(id='pre-war-df'),
    html.Div(
        dbc.Row([
        # Figure 1 - Fuel price over time around the event
            dbc.Col([
                html.Div([
                    html.H4("Fuel Prices over time"), # might change this
                    html.P(id='subtitle-ma'),
                    dcc.Graph(id='plot-ma')
                ], className='chart-card')
            ], width=6),
        
        # Figure 2 - Breakdown of pump prices
            dbc.Col([
                html.Div([
                    html.H4("Breakdown of pump price"),
                    dcc.Graph(id='pump-breakdown-plot'),
                    html.P("Pre and post tax components")
            ], className="chart-card"),
            ], width=6),
        ])

    ),
    # Second section
    html.Div(
        dbc.Row([
            # Figure 3 - Cost of 50 liters
            dbc.Col([
                html.Div([
                    html.H4("Cost of 50 litres"),
                    html.P(id="subtitle-50-liters"),
                    dcc.Graph(id='plot-50-liters')
                ], className='chart-card'),
            ], width=6),
            # Figure 4 - Comparison with EU
            dbc.Col([
                html.Div([
                    html.H4(id="comparison-eu-title"),
                        html.P("Fuel price comparison, Euro95, in €/litre"),
                        dcc.Graph(id='plot-eu-comparison')
                    ], className="chart-card"),
            ], width=6)
        ]),
    className="g-3 mt-1"),
    # Key insights
    dbc.Row([
        html.Div(
            dbc.Card([
                dbc.CardBody([
                    html.Div(
                        html.I(className="fa-solid fa-lightbulb", style={"fontSize":"28px"}, **{"aria-hidden":"true"}),
                        className=(
                                "d-flex align-items-center justify-content-center "
                                "pe-3 me-3 border-end"
                            ),
                            style={
                                "minWidth":"60px",
                                "minHeight": "60px",
                            }
                    ),
                    html.Div([
                            html.P("Key Insight", className="mb-1 text-secondary"),
                            html.P(id="card-key-insight", className="fw-bold fs-4 mb-0"),
                        ], className="text-start",
                    ),
                ], className="d-flex align-items-center")
            ])
        )
    ]),
    ]), 
], fluid=True, className='overview-page')



# Populate the cards
@callback(
    Output('card-fuel-price','children'),
    Output('card-tax-component','children'),
    Output('card-50-liter','children'),
    Output('card-comparison','children'),
    Output('df-data', 'data'),
    Input('dropdown-selection','value'),
    Input('fuel-selection','value'),
)
def update_card_title(country, fuel):
    print(f'{country}_{fuel}')
    df = load_df([country])

    fuel_price = round(df.iloc[-1][f'{country}_{fuel}'], 3)
    fuel_wo_tax = round(df.iloc[-1][f'{country}_{fuel}_wo_tax'], 3)
    tax_component = f"€{round(fuel_price - fuel_wo_tax, 3)}"
    tank_50_liters = f"€{round(fuel_price*50, 2)}"
    eu_comp = f"€{round((fuel_price - df.iloc[-1][f'EU_{fuel}']), 2)}" 

    return f"€{fuel_price}", tax_component, tank_50_liters, eu_comp, df.to_dict('records')


@callback(
    Output('plot-ma','figure'),
    Output('subtitle-ma', 'children'),
    Output('pre-war-df', 'data'),
    Input('df-data', 'data'),
    Input('dropdown-selection','value'),
    Input('fuel-selection','value')
)
def plot_ma(df, country, fuel):
    data = pd.DataFrame(df)
    data['Date'] = pd.to_datetime(data['Date'])
    # Define the variables and construct the moving average
    date_event = pd.to_datetime("2026-02-28")
    date_end = pd.to_datetime(datetime.datetime.today().date())
    delta = (date_end - date_event).days
    print(delta)
    delta_elapsed = date_event - (date_end - date_event)
    pre_event_period = data.loc[(data['Date'] >= delta_elapsed)&(data['Date'] <= date_event)]
    post_event_period = data.loc[(data['Date'] >= date_event)&(data['Date'] <= date_end)]

    window_size = 4

    pre_event_ma = pre_event_period[f'{country}_{fuel}'].rolling(window=window_size).mean().dropna().to_frame().reset_index(drop=True)
    post_event_ma = post_event_period[f'{country}_{fuel}'].rolling(window=window_size).mean().dropna().to_frame().reset_index(drop=True)
    print("=== Pre WAR ===")
    print(pre_event_ma)
    print("=== Post WAR ===")
    print(type(post_event_ma))

    fig = px.line(
        pre_event_ma, y=f'{country}_{fuel}',
        color_discrete_sequence=["red"], labels={f"{country}_{fuel}":"Pre event MA"}
    )
    fig.add_traces(
        px.line(
            post_event_ma, y=f'{country}_{fuel}', labels={f"{country}_{fuel}":"Post event MA"}, color_discrete_sequence=["orange"]
        ).data
    )
    fig.for_each_trace(
        lambda trace: trace.update(line=dict(width=2))
    )
    fig.data[0].name = "Pre event MA"
    fig.data[1].name = "Post event MA"
    fig.data[0].update(line_color=COLORS['before'])
    fig.data[1].update(line_color=COLORS['recent'])

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(
            orientation='h',
            y=-.02,
            yanchor='bottom',
            xanchor='right',
            title_text=''
        ),
        margin=dict(l=5, r=5, t=20, b=10)
    )
    fig.update_yaxes(title_text="€/L")
    fig.update_xaxes(title_text="Window")

    fig = style_figure(fig)

    return fig, f"{delta} days", pre_event_period.to_dict('records')


# Plot the tax component breakdown
@callback(
    Output('pump-breakdown-plot', 'figure'),
    Output('last-price-df','data'),
    Input('dropdown-selection', 'value'),
    Input('fuel-selection','value'),
)
def pump_plot(country, fuel):

    last_price = calculate_last_price([country])
    last_price[f'{fuel}_tax_comp'] = last_price[fuel] - last_price[f'{fuel}_pretax']

    fig = px.bar(
        last_price, x=[f'{fuel}_pretax', f'{fuel}_tax_comp'], y='country',
        orientation='h',
        color_discrete_map={f'{fuel}_pretax':COLORS['pretax'], f'{fuel}_tax_comp':COLORS['tax']},
        labels={f'{fuel}_pretax':'Pre tax', f'{fuel}_tax_comp':'Tax component'},
    )
    fig.data[0].name = 'Pre tax'
    fig.data[1].name = 'Tax component'
    fig.update_traces(width=0.4, texttemplate='<b>€ %{x:.3f}</b>', textposition='inside', insidetextanchor='middle')
    fig.update_layout(
        legend=dict(
            orientation='h', yanchor='bottom', y=-0.2, 
        ),
        legend_title_text = "",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=5, r=5, t=10, b=15)
    )
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    
    fig = style_figure(fig)

    return fig, last_price.to_dict('records'), 


@callback(
    Output('subtitle-50-liters', 'children'),
    Output('plot-50-liters', 'figure'),
    Input('last-price-df', 'data'),
    Input('df-data','data'),
    Input('dropdown-selection','value'),
    Input('fuel-selection','value'),
    Input('pre-war-df', 'data'),
)
def plot_tank(last_price_df, df, country, fuel, pre_war_df):
    last_price = pd.DataFrame(last_price_df)
    df = pd.DataFrame(df)
    pre_war_df = pd.DataFrame(pre_war_df)
    df['Date'] = pd.to_datetime(df['Date'])
    subtitle = f"Total cost of 50 litres of {fuel}, in €"

    last_price[fuel] = last_price[fuel]*50

    pre_war_tank = pre_war_df[f'{country}_{fuel}'].mean()*50

    last_price['pre_war_avg'] = pre_war_tank
    last_price_long = last_price.melt()

    fig = px.bar(
        last_price_long.loc[(last_price_long['variable'] == 'pre_war_avg') | (last_price_long['variable'] == f'{fuel}')], 
        x='value', y='variable',
        orientation="h",
        color='variable',
        color_discrete_map={'pre_war_avg':COLORS['before'],
                            f'{fuel}':COLORS['recent']},
        labels={"pre_war_avg":"Pre conflict average",
                f"{fuel}":"Latest available week"},
    )
    fig.update_traces(width=0.4, texttemplate='<b>€ %{x:.2f}</b>', textposition="outside")
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        margin=dict(
            l=5, r=5, t=10, b=10
        )
    )
    fig.update_yaxes(title_text="",
                     tickvals=['pre_war_avg',f'{fuel}'],
                     ticktext=['Pre conflict average','Last available week'])
    fig.update_xaxes(title_text="")

    fig = style_figure(fig)

    return subtitle, fig

@callback(
    Output('plot-eu-comparison','figure'),
    Output('comparison-eu-title', 'children'),
    Input('df-data','data'),
    Input('dropdown-selection','value'),
    Input('fuel-selection','value')
)
def ue_comparison(df, country, fuel):
    '''
    Show the prices against the EU average
    '''
    df = pd.DataFrame(df)

    comparison_df = df.iloc[-1].reset_index()
    comparison_df.columns = ['Key','Value']
    comparison_df['Country'] = comparison_df['Key'].str.extract(rf'^(EU|{country})')
    comparison_df['Metric'] = (comparison_df['Key']
    .str.replace(rf'^(EU|{country})_', '', regex=True)
    .str.replace('_',' ')
    .str.title())

    title = f'{country} vs EU'

    fig = px.bar(
        comparison_df,
        x='Metric',
        y='Value',
        color='Country',
        barmode='group',
        color_discrete_map=color_map
    )
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(
            yanchor='bottom',
            y=-0.2,
            orientation='h'
        ),
    )
    fig.update_yaxes(title_text="€/L")
    fig.update_xaxes(title_text="")
    
    fig = style_figure(fig)

    return fig, title


@callback(
    Output("plot-ranking", "figure"),
    Output("ranking-summary", "children"),
    Input("dropdown-selection", "value"),
    Input("fuel-selection", "value"),
)
def update_ranking(country, fuel):

    def empty_result(message):
        fig = go.Figure()
        fig.add_annotation(
            text=message,
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
            showarrow=False,
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis_visible=False,
            yaxis_visible=False,
        )
        return fig, message

    if not country or fuel not in ("Gas", "Diesel"):
        return empty_result("Select a country and a fuel type.")

    event_date = pd.Timestamp("2026-02-28")
    n_weeks = 4

    # Escludiamo EU: è una media di riferimento, non un paese.
    country_codes = [code for code in countries if code != "EU"]

    # Per il ranking servono i dati di tutti i paesi.
    data = load_df(country_codes).copy()
    data["Date"] = pd.to_datetime(data["Date"], errors="coerce")
    data = data.dropna(subset=["Date"]).sort_values("Date")

    before = data.loc[data["Date"] < event_date].tail(n_weeks)
    recent = data.loc[data["Date"] >= event_date].tail(n_weeks)

    if len(before) < n_weeks or len(recent) < n_weeks:
        return empty_result(
            "Not enough observations for the selected periods."
        )

    eu_column = f"EU_{fuel}"

    country_columns = {
        code: f"{code}_{fuel}"
        for code in country_codes
        if f"{code}_{fuel}" in data.columns
    }

    if eu_column not in data.columns:
        return empty_result("EU average is not available.")

    columns = list(country_columns.values()) + [eu_column]

    # Conversione prudente: eventuali valori non numerici diventano NaN.
    before_values = before[columns].apply(
        pd.to_numeric, errors="coerce"
    )
    recent_values = recent[columns].apply(
        pd.to_numeric, errors="coerce"
    )

    # Media e numero di osservazioni per ogni serie.
    averages = pd.DataFrame(
        {
            "before": before_values.mean(),
            "recent": recent_values.mean(),
            "n_before": before_values.count(),
            "n_recent": recent_values.count(),
        }
    )

    # Usiamo lo stesso insieme di serie complete nei due periodi.
    averages = averages.loc[
        (averages["n_before"] == n_weeks)
        & (averages["n_recent"] == n_weeks)
    ]

    if eu_column not in averages.index:
        return empty_result(
            "EU data is incomplete for one of the periods."
        )

    eu_before = averages.loc[eu_column, "before"]
    eu_recent = averages.loc[eu_column, "recent"]

    ranking = averages.drop(index=eu_column).copy()

    # Da nome colonna, es. IT_Gas, a codice paese IT.
    column_to_country = {
        column: code
        for code, column in country_columns.items()
    }
    ranking.index = [
        column_to_country[column]
        for column in ranking.index
    ]

    if ranking.empty or country not in ranking.index:
        return empty_result(
            f"Complete data for {country} is not available "
            "in both periods."
        )

    # 1 = prezzo più alto. A parità di prezzo, stessa posizione.
    ranking["rank_before"] = (
        ranking["before"]
        .rank(method="min", ascending=False)
        .astype(int)
    )

    ranking["rank_recent"] = (
        ranking["recent"]
        .rank(method="min", ascending=False)
        .astype(int)
    )

    # Scarto rispetto alla media UE, in €/litro.
    ranking["gap_before"] = ranking["before"] - eu_before
    ranking["gap_recent"] = ranking["recent"] - eu_recent

    fig = go.Figure()

    # Disegniamo prima gli altri paesi e per ultimo quello selezionato,
    # così la sua linea rimane in evidenza.
    ordered_countries = sorted(
        ranking.index,
        key=lambda code: code == country,
    )

    for code in ordered_countries:
        row = ranking.loc[code]
        selected = code == country

        fig.add_trace(
            go.Scatter(
                x=["Before event", "Latest available"],
                y=[row["rank_before"], row["rank_recent"]],
                mode="lines+markers",
                name=code,
                showlegend=False,
                line=dict(
                    color=(
                        COLORS["country"]
                        if selected
                        else "#CBD5E1"
                    ),
                    width=4 if selected else 1.5,
                ),
                marker=dict(
                    size=10 if selected else 5,
                    color=(
                        COLORS["country"]
                        if selected
                        else "#A8B8C8"
                    ),
                ),
                customdata=[
                    [row["before"], row["gap_before"]],
                    [row["recent"], row["gap_recent"]],
                ],
                hovertemplate=(
                    f"<b>{code}</b><br>"
                    "Rank: %{y}<br>"
                    "Average price: €%{customdata[0]:.3f}/L<br>"
                    "Difference vs EU: "
                    "€%{customdata[1]:+.3f}/L"
                    "<extra></extra>"
                ),
            )
        )

    fig.update_layout(
        height=520,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=COLORS["text"]),
        hovermode="closest",
    )

    fig.update_yaxes(
        title_text="Rank — 1 = highest price",
        autorange="reversed",
        dtick=1,
        gridcolor=COLORS["grid"],
        zeroline=False,
    )

    fig.update_xaxes(
        title_text="",
        showgrid=False,
    )

    selected = ranking.loc[country]
    total_countries = len(ranking)

    before_start = before["Date"].min().strftime("%d %b %Y")
    before_end = before["Date"].max().strftime("%d %b %Y")
    recent_start = recent["Date"].min().strftime("%d %b %Y")
    recent_end = recent["Date"].max().strftime("%d %b %Y")

    summary = (
        f"{country}: rank {selected['rank_before']} → "
        f"{selected['rank_recent']} out of {total_countries} countries. "
        f"Difference vs EU: "
        f"€{selected['gap_before']:+.3f}/L → "
        f"€{selected['gap_recent']:+.3f}/L. "
        f"Before: {before_start}–{before_end}; "
        f"latest: {recent_start}–{recent_end}."
    )

    return fig, summary