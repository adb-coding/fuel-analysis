from helper import load_df, extract_oil, extract_countries, calculate_last_price, calculate_pct_change, construct_average, calculate_correlation, extract_events, calculate_volatility, extract_inflation, get_oil
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from dash import Dash, html, dcc, Output, Input, callback, register_page, dash_table
import dash_bootstrap_components as dbc
import datetime
import pandas as pd


countries = extract_countries()

last_price = calculate_last_price(countries)

colors = {
    'Gas':'green',
    'Diesel':'black'
}


color_map = {
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

iso2_to_iso3 = {
    "AT": "AUT", "BE": "BEL", "BG": "BGR", "CY": "CYP", "CZ": "CZE",
    "DE": "DEU", "DK": "DNK", "EE": "EST", "ES": "ESP", "FI": "FIN",
    "FR": "FRA", "GR": "GRC", "HR": "HRV", "HU": "HUN", "IE": "IRL",
    "IT": "ITA", "LT": "LTU", "LU": "LUX", "LV": "LVA", "MT": "MLT",
    "NL": "NLD", "PL": "POL", "PT": "PRT", "RO": "ROU", "SE": "SWE",
    "SI": "SVN", "SK": "SVK"
}

last_price['ISO3'] = [iso2_to_iso3.get(i) for i in last_price['country']]


# register the page
register_page(__name__, name="Home", path="/")


events_df = extract_events(country='IT')


# Layout
layout = dbc.Container([
    html.Div([
        html.H4([
            "Price Chart", html.I(className="fa-solid fa-circle-question ms-2 fa-xs", id="help-icon-price", style={"cursor":"pointer", "color":["#0d6efd"]})
        ]),
        dbc.Tooltip("Historical prices (in €/L) extracted from the European Commission's weekly report.\n The weekly price is the average fuel price reported by domestic government. The methodology may change across Countries. Only gasoline (euro95) and diesel fuels are considered. Brent prices are retrieved from Yahoo Finance",
                    target="help-icon-price",
                    placement="right"),
        dcc.Store(id='df', storage_type='session'),
        dcc.Store(id='brent', storage_type='session'),
        dbc.Row([
            dbc.Col([
                html.Span("Select Country"),
                dcc.Dropdown(countries, ['IT'], id='dropdown-selection', multi=True, searchable=False, style={'padding':8, 'flex': 1}),  
            ],
                width=3
                ),
            dbc.Col([
                html.Span("Select Fuel Type"),
                dcc.Dropdown(['Diesel','Gas'], ['Gas','Diesel'], id='fuel-selection', searchable=False, multi=True, style={'padding':8, 'flex': 1}),
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
        dbc.Row([
            dcc.Checklist(options=[{'label':'Show Oil Chart', 'value':'Show Brent'},
                          {'label':'EU average','value':'Show EU'},
                          {'label':'Events','value':'Show Events'}], inline=True, id='checkbox'),
            dcc.Loading(
                dcc.Graph(id='graph-content'),
            )
        ]),
        html.H4(id="section2-title"),
        dbc.Row([
                dcc.RadioItems(options=[{'label':'Price change','value':'price change'},
                                        {'label':'Compare with EU average', 'value':'average'},
                                       {'label':'Standard Deviation', 'value':'std'}], 
                             value='price change', id='checkbox-average', inline=True),
                dcc.Loading(
                    dcc.Graph(id='graph-content2'),
                ),
            ]),
        dbc.Accordion([
            dbc.AccordionItem(
            title=[html.I(className="fa-solid fa-circle-info ms-4 fa-xl", style={'color':['#0d6efd']}), "  Info and Methodology"],
            children=[
                html.P([html.Strong("Price change: "), "Weekly percentage variation calculated on the historical prices."]),
                html.P([html.Strong("Compare with EU average: "), "Comparison between the national average against the EU average, set at 0."]),
                html.P([html.Strong("Standard Deviation: "), "Volatility measure to compare the fluctuations of the prices during the period analyzed."])
            ]
        ),
        ], start_collapsed=True, className="pd-1 mb-3"),
        html.H4(['Correlation', html.I(className="fa-solid fa-circle-question fa-xs ms-2", id="help-icon-corr", style={'cursor':'point','color':['#d6efd']})]),
        dbc.Tooltip("Correlation is the statistical relation of two variables and their tendency to move together. Dots closer to the line indicates higher correlation, either negative or positive. Here is reported the Pearson's statistical correlation of the price charts. Note that correlation does not imply statistical causation.",
                    target="help-icon-corr",
                    placement="right"),
        dcc.Store(id='corr-df'),
        dbc.Row([
            dbc.Col([
                html.Span("X-axis"),
                dcc.Dropdown(
                              multi=False, id='x-dropdown'),
            ]),
            dbc.Col([
                html.Span("Y-axis"),
                dcc.Dropdown(multi=False, id='y-dropdown'),
            ]),
            html.Div("Correlation", id='date-output'),
            dcc.Loading([
                dcc.Graph(id='correlation-plot'),
                dcc.Graph(id='corr-heatmap', style={"width":"100%"})
            ]),
            # html.Div("Correlation Table", id='correlation-tab'),
        ], className="mb-4"),
        html.H4(["Inflation", html.I(className="fa-solid fa-circle-question fa-xs ms-2", id="help-icon-infl", style={'cursor':'pointer','color':['#0d6edf']})]),
        dbc.Tooltip(
            "Annual inflation data extracted form the European Central Bank report, reported monthly. The direct comparison with fuel prices is not yet possible, and the graph is provided only for reference and qualitative analysis.",
            target="help-icon-infl",
            placement="right"
        ),
        dcc.Store(id='inflation-df'),
        dbc.Row([
            dbc.Col([
                html.Span('Compare with'),
                dcc.Dropdown(countries, value=[], multi=True, id='inflation-dropdown')
            ]),
            dbc.Col([
                html.Span('Fuel'),
                dcc.Dropdown(['Gas','Diesel'], value=['Gas','Diesel'], multi=True, id='fuel-inflation-dropdown')
            ]),
        ]),
        dbc.Row([
            html.Div(id='inflation-tab'),
            dcc.Graph(id='inflation-plot')
            ])
        ]),
    ], fluid=True
)

    
# Callbacks
@callback(
    Output('price-date-picker','min_date_allowed'),  
    Output('price-date-picker','max_date_allowed'),  
    Output('price-date-picker','start_date'),  
    Output('price-date-picker','end_date'),
    Output('df','data'),
    Output('brent','data'),
    Input('dropdown-selection','value')  
)
def update_price_date(value):
    
    df = load_df(value)
    brent = get_oil()
    
    df['Date'] = pd.to_datetime(df['Date'])
    min_date = df['Date'].min().date()
    max_date = df['Date'].max().date()


    return min_date, max_date, min_date, max_date, df.to_dict('records'), brent.to_dict('records')


@callback(
    Output('graph-content','figure'),
    Input('df','data'),
    Input('brent','data'),
    Input('dropdown-selection','value'),
    Input('price-date-picker','start_date'),
    Input('price-date-picker','end_date'),
    Input('fuel-selection','value'),
    Input('checkbox','value'),
    Input('price-selection','value')
)
def update_price_data(data, brent_df, value, min_date, max_date, fuel, check, price):
    
    df = pd.DataFrame(data)
    brent = pd.DataFrame(brent_df)

    df['Date'] = pd.to_datetime(df['Date'])
    # brent['Date'] = pd.to_datetime(df['Date'])

    # filter on the date range
    df = df.loc[(df['Date'] >= min_date) & (df['Date'] <= max_date)]
    brent = brent.loc[(brent['Date'] >= min_date) & (brent['Date'] <= max_date)]


    series = []

    if isinstance(value, list):
        for i in value:
            for j in fuel:
                if price == 'Full Price':
                    series.append(f"{i}_{j}")
                elif price == 'Pre-Tax Price':
                    series.append(f"{i}_{j}_wo_tax")
                elif price == 'Tax Component':
                    series.append(f"{i}_{j}_tax_comp")
    else:
        series = value[0]


    fig = make_subplots(specs=[[{"secondary_y":True}]])

    fig1 = px.line(df, x="Date", y=series, 
                  title=f'{value} Diesel and Gasoline prices',
                #   color_discrete_sequence=line_colors,
                  labels={'value':'Fuel'})

    fig1.for_each_trace(
        lambda trace: trace.update(line=dict(dash="dash")) if 'Diesel' in trace.name else ()
    )
    fig1.for_each_trace(
        lambda trace: trace.update(line=dict(color=color_map.get(trace.name.split('_')[0]))) if trace.name.split('_')[0] in color_map.keys() else ()
    )

    if check and 'Show Events' in check:

        filtered_events = events_df.loc[(events_df['date'] >= min_date) & (events_df['date'] <= max_date)]
        for i in range(len(filtered_events)):
            fig.add_trace(go.Scatter(
                x=[filtered_events['date'].iloc[i], filtered_events['date'].iloc[i]],
                y=[0,1],
                yaxis="y3",
                mode="lines",
                line=dict(color="red", dash="dash"),
                hoverinfo="text",
                hovertext=filtered_events['hover'].iloc[i],
                showlegend=False,
                name="Event",
                fillcolor="white"
            ))

    if check and 'Show EU' in check:
        EU_series = []
        # Plot only the fuel selected
        for i in fuel:
            EU_series.append(f'EU_{i}')

        eu_fig = px.line(df, x="Date", y=EU_series)
        eu_fig.update_traces(line=dict(dash="dashdot", color="red"))
        fig1.add_traces(eu_fig.data)

    # plot the oil chart
    if check and 'Show Brent' in check:
        fig2 = px.line(brent, x='Date', y='Oil')
        fig2.update_traces(yaxis="y2", name="Brent",
                             line=dict(color="black", dash="dot"))
        # for trace in fig1.data:
        #     fig.add_trace(trace, secondary_y=False)
        # for trace in fig2.data:
        #     fig.add_trace(trace, secondary_y=True)
        fig.add_traces(fig1.data + fig2.data)
        fig.update_yaxes(title_text="Oil €/L", secondary_y=True)


    else:
        fig.add_traces(fig1.data)

    fig.update_yaxes(title_text="Fuel €/L", secondary_y=False)
    fig.update_layout(
        yaxis3=dict(overlaying="y", range=[0, 1], visible=False),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15
        ),
        height=500,
        )
    
    return fig


@callback(
        Output('graph-content2','figure'),
        Output('section2-title','children'),
        Input('dropdown-selection','value'),
        Input('brent','data'),
        Input('fuel-selection','value'),
        Input('checkbox','value'),
        Input('checkbox-average', 'value'),    
        Input('price-date-picker','start_date'),
        Input('price-date-picker','end_date'),
        
)
def update_pct_graph(value, brent_df, fuel, check, checkbox_value, start_date, end_date):

    title_map = {
        'price change':'Weekly Price Change',
        'average':'Difference to EU Average',
        'std':'Standard Deviation'
    }

    brent = pd.DataFrame(brent_df)
    pct_change = calculate_pct_change(value, brent)
    pct_change = pct_change.dropna()
    brent = brent.loc[(brent['Date'] >= start_date) & (brent['Date'] <= end_date)]
    brent_change = round(brent.sort_index(ascending=False)['Oil'].pct_change().dropna()*100, 3)
    brent_change.index = brent.iloc[1:]['Date']
    pct_change = pct_change.loc[(pct_change['Date'] >= start_date) & (pct_change['Date'] <= end_date)]

    series = []

    if checkbox_value and 'average' in checkbox_value:
        df = construct_average(value)
        df = df.loc[(df['Date'] >= start_date) & (df['Date'] <= end_date)]

        if isinstance(value, list):
            for i in value:
                for j in fuel:
                    series.append(f"{i}_{j.lower()}_diff")
        else:
            series = value[0]
        fig = px.line(df, x="Date", y=series)
        fig.add_hline(y=0, line=dict(dash="dash", color="black", width=3))
        fig.for_each_trace(
            lambda trace: trace.update(line=dict(dash="dash")) if 'diesel' in trace.name else ()
        )
        fig.for_each_trace(
            lambda trace: trace.update(line=dict(color=color_map.get(trace.name.split('_')[0]))) if trace.name.split('_')[0] in color_map.keys() else ()
        )

    elif checkbox_value and 'std' in checkbox_value:
        vol_df = calculate_volatility(countries)
        vol_df = vol_df.loc[(vol_df['Date'] >= start_date)&(vol_df['Date'] <= end_date)]
        
        if type(value) == list:
            for i in value:
                for j in fuel:
                    series.append(f"{i}_{j.lower()}")
        
        fig = px.line(vol_df, x='Date', y=series)

        fig.for_each_trace(
            lambda trace: trace.update(line=dict(dash="dash")) if 'diesel' in trace.name else ()
        )
        fig.for_each_trace(
            lambda trace: trace.update(line=dict(color=color_map.get(trace.name.split('_')[0]))) if trace.name.split('_')[0] in color_map.keys() else ()
        )


    elif checkbox_value and 'price change' in checkbox_value:
        if type(value) == list:
            for i in value:
                for j in fuel:
                    series.append(f"{i}_{j.lower()}_change")
        else:
            series = value[0]
        fig = make_subplots(specs=[[{"secondary_y":True}]])

        fig1 = px.line(pct_change, x='Date', y=series
                    )

        fig1.for_each_trace(
           lambda trace: trace.update(line=dict(dash="dash")) if 'diesel_change' in trace.name else ()
        )
        fig1.for_each_trace(
            lambda trace: trace.update(line=dict(color=color_map.get(trace.name.split('_')[0]))) if trace.name.split('_')[0] in color_map.keys() else ()
        )

        if check and 'Show Brent' in check: 
            fig2 = px.line(brent_change, y='Oil')
            fig2.update_traces(yaxis="y2",
                            line=dict(color="black", dash="dot"))
            fig.add_traces(fig1.data + fig2.data)
            fig.update_yaxes(title_text="Oil % Change", secondary_y=True)
            

        else:
            fig.add_traces(fig1.data)

        fig.add_hline(y=0, line=dict(dash='dash', color='red', width=2.5))
        fig.update_yaxes(title_text='% Change')

    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15
        ),
        height=500
        )

    section2_title = title_map.get(checkbox_value)

    return fig, section2_title


@callback(
    Output('date-output', 'children'),
    Output('x-dropdown','options'),
    Output('y-dropdown','options'),
    Output('x-dropdown','value'),
    Output('y-dropdown','value'),
    Output('corr-heatmap','figure'),
    Output('corr-df','data'),
    Input('brent','data'),   
    Input('df','data'),   
    Input('price-date-picker', 'start_date'),
    Input('price-date-picker','end_date'),
    Input('dropdown-selection', 'value'),


)
def extract_date_correlation(brent_df, data, start_date, end_date, country):
    map_axis = {'Diesel':'Diesel',
                'Gasoline':'Gas',
                'Oil':'Oil'}

    brent = pd.DataFrame(brent_df)
    brent['Date'] = pd.to_datetime(brent['Date'])
    df = pd.DataFrame(data)
    df['Date'] = pd.to_datetime(df['Date'])

    corr_df = calculate_correlation(country, brent, df, start_date, end_date)
 
    string = f"Period selected {start_date}, {end_date}"
    # corr_tab = dbc.Table.from_dataframe(corr_df.corr())
    correlation = corr_df.corr()
    
    fig2 = px.imshow(correlation,
                     zmin=-1,
                     zmax=1,
                     text_auto=True,
                     color_continuous_scale='RdBu_r',
                     labels=dict(color='correlation'),
                     aspect="auto")
    fig2.update_layout(
        autosize=True,
        margin=dict(l=4, r=4, t=30, b=4),
        height=600
    )
    corr_tab = dash_table.DataTable(
        correlation.to_dict('records'), 
        columns=[{'name':i, 'id':i} for i in correlation.columns],
        
        style_table={'overflowX':'auto', 'margin-left':'2', 'margin-right':'4'}
    )
    return string, corr_df.columns, corr_df.columns, corr_df.columns[0], corr_df.columns[1], fig2, corr_df.to_dict('records')


@callback(
    Output('correlation-plot','figure'),
    Input('corr-df','data'),
    Input('x-dropdown','value'),
    Input('y-dropdown','value'),
)
def update_correlation_plot(corr_df, x_value, y_value):

    corr = pd.DataFrame(corr_df)
    fig = px.scatter(corr_df, x=x_value, y=y_value, trendline="ols")

    return fig


@callback(
    Output('inflation-df','data'),
    Input('inflation-tab','id')
)
def load_inflation(_):
    inflation_df = extract_inflation()

    return inflation_df.to_dict('records')


@callback(
    Output('inflation-plot','figure'),
    Input('inflation-dropdown','value'),
    Input('fuel-inflation-dropdown','value'),
    Input('inflation-df','data'),
    Input('brent', 'data')
)
def inflation_plot(value, fuel, inflation_df, brent_df):

    inflation = pd.DataFrame(inflation_df)
    
    brent = pd.DataFrame(brent_df)
    
    
    fig = make_subplots(specs=[[{"secondary_y":True}]])
    fig1 = px.line(inflation, x='Date', y='inflation')

    data = load_df(value)
    
    if value != []:
        series = []
        for country in value:
            for element in fuel:
                series.append(f'{country}_{element}')

            if country != 'Oil':
                fig2 = px.line(
                    data, x='Date', y=series
                )  
                fig2.update_traces(yaxis="y2", line=dict(color=color_map.get(country)))
                fig2.for_each_trace(lambda t: t.update(line=dict(dash='dash')) if 'Diesel' in t.name else ())
                fig.add_traces(fig1.data + fig2.data)
    
    else:

        fig.add_traces(fig1.data)

    return fig
