import pandas as pd
import yfinance as yf
import datetime
import json
import os
from pathlib import Path

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
df_path = os.path.join(BASE_DIR, "data", "Weekly_Oil_Bulletin_Prices_History_maticni_4web.xlsx")
json_path = os.path.join(BASE_DIR, "data", "fuel_price_events_2007_2026.json")
inflation_path = os.path.join(BASE_DIR, "data", "HICP.csv")
today = str(datetime.datetime.today().date())

# Prices dataframe 
df = pd.read_excel(df_path, sheet_name="Prices with taxes")
df.rename(columns={'Consumer prices of petroleum products inclusive of duties and taxes':'Date'}, inplace=True)
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
df = df.dropna(subset='Date')
df = df.sort_values(by='Date', ascending=True)
df = df.reset_index(drop=True)
# Prices without tax
df_tax = pd.read_excel(df_path, sheet_name="Prices wo taxes")
df_tax.rename(columns={'Consumer prices of petroleum products net of duties and taxes':'Date'}, inplace=True)
df_tax['Date'] = pd.to_datetime(df_tax['Date'], errors='coerce')
df_tax = df_tax.dropna(subset='Date')
df_tax = df_tax.sort_values(by='Date', ascending=True)
df_tax = df_tax.reset_index(drop=True)



def load_df(countries):
    """Extract the fuel price for the countries selected in the main app"""

    prices = pd.DataFrame({'Date':df['Date']})

    prices['EU_Gas'] = df['EU_price_with_tax_euro95'] / 1000
    prices['EU_Diesel'] = df['EU_price_with_tax_diesel'] / 1000
    prices['EU_Gas_wo_tax'] = df_tax['EU_price_wo_tax_euro95'] / 1000
    prices['EU_Diesel_wo_tax'] = df_tax['EU_price_wo_tax_diesel'] / 1000
    prices['EU_Gas_tax_comp'] = prices['EU_Gas'] - prices['EU_Gas_wo_tax']
    prices['EU_Diesel_tax_comp'] = prices['EU_Diesel'] - prices['EU_Diesel_wo_tax']
    
    for country in countries:
        # get the diesel and gas prices
        prices[f'{country}_Gas'] = df[f'{country}_price_with_tax_euro95'] / 1000
        prices[f'{country}_Diesel'] = df[f'{country}_price_with_tax_diesel'] / 1000
        
        # get the diesel and gas pre-tax prices
        prices[f'{country}_Gas_wo_tax'] = df_tax[f'{country}_price_wo_tax_euro95'] / 1000
        prices[f'{country}_Diesel_wo_tax'] = df_tax[f'{country}_price_wo_tax_diesel'] / 1000

        # get the tax component
        prices[f'{country}_Gas_tax_comp'] = prices[f'{country}_Gas'] - prices[f'{country}_Gas_wo_tax'] 
        prices[f'{country}_Diesel_tax_comp'] = prices[f'{country}_Diesel'] - prices[f'{country}_Diesel_wo_tax'] 


    return prices


def extract_oil():
    """Download the oil price and the USD/EUR conversion from Yahoo Finance"""

    brent = yf.download("BZ=F", start="2005-01-01", end=today, interval="1wk")
    usdeur = yf.download("EUR=X", start="2005-01-01", end=today, interval="1d")

    # merge the two df
    brent = brent['Close'].merge(usdeur['Close'], left_index=True, right_index=True, how="inner")
 
    brent['Oil'] = (brent['BZ=F'] * brent['EUR=X']) / 158.987

    brent = brent.reset_index()
    brent['Date'] = pd.to_datetime(brent['Date'])

    return brent 


brent_cached = extract_oil()

def get_oil():
    return brent_cached.copy()

def extract_countries():
    """Gets the country code from the price dataframe"""
    country_code = []

    for i in range(len(df.columns)):
        if 'CTR' in df.columns[i]:
            if df[df.columns[i]].isna()[2] == False:
                country_code.append(df[df.columns[i]][2].strip('_'))

    return country_code


# extract the last country price and last 10 week average
def calculate_last_price(country_code):

    last_price = pd.DataFrame({'country':country_code})

    last_diesel = []
    average_diesel = []
    last_gas = []
    average_gas = []
    last_diesel_pretax = []
    last_gas_pretax = []

    for i in range(len(last_price)):
        last_diesel.append(df[f"{last_price.iloc[i,0]}_price_with_tax_diesel"].iloc[-1]/1000)
        average_diesel.append(df[f"{last_price.iloc[i,0]}_price_with_tax_diesel"][len(df)-10:len(df)].mean() / 1000)
        last_diesel_pretax.append(df_tax[f"{last_price.iloc[i,0]}_price_wo_tax_diesel"].iloc[-1]/1000)
        last_gas.append(df[f"{last_price.iloc[i,0]}_price_with_tax_euro95"].iloc[-1]/1000)
        average_gas.append(df[f"{last_price.iloc[i,0]}_price_with_tax_euro95"][len(df)-10:len(df)].mean() / 1000)
        last_gas_pretax.append(df_tax[f"{last_price.iloc[i,0]}_price_wo_tax_euro95"].iloc[-1]/1000)


    last_price['Gas'] = last_gas
    last_price['Diesel'] = last_diesel
    last_price['AvgGas'] = average_gas
    last_price['AvgDiesel'] = average_diesel
    last_price['Gas_pretax'] = last_gas_pretax
    last_price['Diesel_pretax'] = last_diesel_pretax
    last_price['IncreaseGas'] = round((last_price['Gas'] - last_price['AvgGas'])/ last_price['AvgGas'] * 100, 2)
    last_price['IncreaseDiesel'] = round((last_price['Diesel'] - last_price['AvgDiesel'])/ last_price['AvgDiesel'] * 100, 2)

    return last_price


def calculate_date_price(country_code, date, df):
    date_price = pd.DataFrame({'country':country_code})
    diesel = [] 
    gas = []
    diesel_pretax = []
    gas_pretax = []
    diesel_comp = []
    gas_comp = []
    diesel_change = []
    gas_change = []
    row = df.iloc[date]

    for country in country_code:
        diesel.append(row[f'{country}_diesel'])
        gas.append(row[f'{country}_gas'])
        diesel_pretax.append(row[f'{country}_wo_tax_diesel'])
        gas_pretax.append(row[f'{country}_wo_tax_gas'])
        diesel_comp.append(row[f'{country}_comp_diesel'])
        gas_comp.append(row[f'{country}_comp_gas'])
        diesel_change.append(row[f'{country}_diesel_change'])
        gas_change.append(row[f'{country}_gas_change'])
        

    date_price['Diesel'] = diesel
    date_price['Gas'] = gas
    date_price['Diesel_pretax'] = diesel_pretax
    date_price['Gas_pretax'] = gas_pretax
    date_price['Diesel_tax_comp'] = diesel_comp
    date_price['Gas_tax_comp'] = gas_comp
    date_price['Diesel_change'] = diesel_change
    date_price['Gas_change'] = gas_change
    date_price.dropna()

    return date_price


def calculate_pct_change(country_code, brent):
    # Calculate the weekly percentage change of the fuels' price
    pct_change = pd.DataFrame({'Date':df['Date']})
    
    for i in country_code:
        pct_change[f'{i}_gas_change'] = round(df.sort_values(by='Date', ascending=False)[f'{i}_price_with_tax_euro95'].pct_change(fill_method=None).dropna()*100, 3)
        pct_change[f'{i}_diesel_change'] = round(df.sort_values(by='Date', ascending=False)[f'{i}_price_with_tax_diesel'].pct_change(fill_method=None).dropna()*100, 3) 


    return pct_change


def calculate_price_by_country(country_code):
    df_sorted = df.sort_values(by='Date', ascending=True).reset_index(drop=True)
    df_tax_sorted = df_tax.sort_values(by='Date', ascending=True).reset_index(drop=True)
    price_by_country = pd.DataFrame({'Date':df_sorted['Date']})
    
    new_cols = {}
    for country in country_code:
        diesel = df_sorted[f'{country}_price_with_tax_diesel'] / 1000
        gas = df_sorted[f'{country}_price_with_tax_euro95'] / 1000
        wo_tax_diesel = df_tax_sorted[f'{country}_price_wo_tax_diesel'] / 1000 
        wo_tax_gas = df_tax_sorted[f'{country}_price_wo_tax_euro95'] / 1000
        comp_gas = gas - wo_tax_gas 
        comp_diesel = diesel - wo_tax_diesel 
        diesel_change = diesel.pct_change(fill_method=None)
        gas_change = gas.pct_change(fill_method=None)

        new_cols[f'{country}_diesel'] = diesel
        new_cols[f'{country}_gas'] = gas
        new_cols[f'{country}_wo_tax_gas'] = wo_tax_gas
        new_cols[f'{country}_wo_tax_diesel'] = wo_tax_diesel
        new_cols[f'{country}_comp_gas'] = comp_gas
        new_cols[f'{country}_comp_diesel'] = comp_diesel
        new_cols[f'{country}_diesel_change'] = diesel_change
        new_cols[f'{country}_gas_change'] = gas_change


    new_cols_df = pd.DataFrame(new_cols)
    price_by_country = pd.concat([price_by_country, new_cols_df], axis=1)
    price_by_country = price_by_country.sort_values(by='Date', ascending=True).reset_index(drop=True)

    return price_by_country


def construct_average(country_code):
    average_comparison = pd.DataFrame({'Date':df['Date']})

    for country in country_code:
        average_comparison[f'{country}_diesel_diff'] =  df[f'{country}_price_with_tax_diesel']/1000 - df['EU_price_with_tax_diesel']/1000
        average_comparison[f'{country}_gas_diff'] = df[f'{country}_price_with_tax_euro95']/1000 - df['EU_price_with_tax_euro95']/1000

    return average_comparison


def calculate_correlation(countries, brent, df, start_date, end_date):
    '''
    Function to calculate the correlation between the price of oil, gasoline and diesel
    '''

    # constuct the dataframe 
    df.set_index('Date')

    brent.set_index('Date')
    
    oil_fuel = pd.merge(left=brent['Oil'], left_index=True, right=df, right_index=True, how='inner')
    oil_fuel.set_index('Date', inplace=True)
    oil_fuel = oil_fuel.loc[(oil_fuel.index > start_date) & (oil_fuel.index < end_date)]
    
    return oil_fuel


def extract_events(country):
    # load the event dataset and use it to display the events
    with open(json_path, 'r') as f:
        events_df = json.load(f)

    events_df = pd.DataFrame(events_df['events'])
    
    # events_df['hover_text'] = f"<b>{events_df['title']}</b><br>Date: {events_df['date']}</br><br>Date: {events_df['type']}</br>"        
    events_name = []
    event_pricet0 = []
    event_pricet1 = []
    event_pct_change = []
    hover_text = []
    events_df['date'] = pd.to_datetime(events_df['date'])
    
    for idx, row in events_df.iterrows():
        events_name.append(row['event'])
        closest_date = (pd.to_datetime(df['Date']) - row['date']).abs().argmin()
        event_valuet0 = df[f'{country}_price_with_tax_euro95'].iloc[closest_date]

        event_pricet0.append(event_valuet0)
        
        try:
            event_valuet1 = df[f'{country}_price_with_tax_euro95'].iloc[closest_date + 1]
            event_pricet1.append(event_valuet1)
            event_pct_change.append((event_valuet1 - event_valuet0)/event_valuet0)
            
        except:
            # if (closest_date + 1) not in df.index:
                
            event_pricet1.append(None)
            event_pct_change.append(None)

        hover = f"<b>{row['event']}</b><br>Date: {row['date'].date()}</br><br>Type: {row['type']}</br>"
        hover_text.append(hover)


    events_df['price_gas_t0'] = event_pricet0
    events_df['price_gas_t1'] = event_pricet1
    events_df['pct_change'] = event_pct_change
    events_df['hover'] = hover_text

    return events_df


def adjust_for_inflation(data):
    pass


def extract_inflation():
    # load the inflation dataset
    inflation_df = pd.read_csv(inflation_path)
    inflation_df.rename(columns={'DATE':'Date',
                                'HICP Inflation rate - Total - Annual rate of change (HICP.M.U2.N.000000.4D0.ANR)':'inflation'},
                                inplace=True)
    inflation_df.dropna(inplace=True)

    return inflation_df


def calculate_volatility(countries):
    # calculate the volatility of the series
    vol = pd.DataFrame({'Date':df['Date']})
    
    for country in countries:
        vol[[f'{country}_gas',f'{country}_diesel']] = df[[f'{country}_price_with_tax_euro95',f'{country}_price_with_tax_diesel']].pct_change().dropna().rolling(4).std().dropna()

    return vol


def extract_date():
    '''
    Extract the last date registered to update the footer
    '''
    return str(df['Date'].max().date())


def calculate_event_price(date_event, date_end, df, brent, window_size=4):
    date_event = pd.to_datetime(date_event)
    date_end = pd.to_datetime(date_end)
    delta_elapsed = date_event - (date_end - date_event)

    df_pre_event = df.loc[(df['Date'] >= delta_elapsed)  & (df['Date'] <= date_event)]
    df_post_event = df.loc[(df['Date']>= date_event) & (df['Date'] <= date_end)]
    df_pre_event = df_pre_event.merge(brent['Close'], left_index=True, right_index=True, how="inner")
    df_post_event = df_post_event.merge(brent['Close'], left_index=True, right_index=True, how="inner")

    df_pre_ma = df_pre_event.rolling(window_size).mean().dropna().reset_index(drop=True)
    df_post_ma = df_post_event.rolling(window_size).mean().dropna().reset_index(drop=True)
