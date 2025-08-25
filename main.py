import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta

MY_API_KEY = "INSERT_YOUR_API_KEY_HERE" # API for exchangerate site

st.set_page_config(page_title="💱 Currency Converter", layout="wide")

st.title("💱 Currency Converter Dashboard")
st.write("Convert currencies with real-time exchange rates and view historical trends.")

st.sidebar.header("Settings")

if 'base_currency' not in st.session_state:
    st.session_state.base_currency = 'USD'
    
st.sidebar.markdown("Adjust preferences here for a personalized experience.")

#Just some mock example becuase you need paid subs for relevant data
@st.cache_data
def fetch_historical(from_curr, to_curr, days=30):
    dates = pd.date_range(end=pd.Timestamp.now(), periods=days)
    rates = np.random.uniform(0.9, 1.1, days) 
    return pd.DataFrame({'Date': dates, 'Rate': rates}).set_index('Date')

@st.cache_data
def fetch_latest_rates(base: str):
    
    url = f"https://v6.exchangerate-api.com/v6/{MY_API_KEY}/latest/{base}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get('conversion_rates', {})
    else:
        st.error("API fetch failed. Using fallback.")
        
    return {"USD": 1.0, "EUR": 0.9, "GBP": 0.78, "JPY": 145.0, "RUB": 92.0}


with st.spinner("Loading exchange rates..."):
    rates = fetch_latest_rates(st.session_state.base_currency)

currencies = list(rates.keys())

with st.form(key='converter_form'):
    col1, col2 = st.columns(2)
    from_currency = col1.selectbox("From", currencies, index=currencies.index(st.session_state.base_currency))
    to_currency = col2.selectbox("To", currencies, index=currencies.index('EUR') if 'EUR' in currencies else 0)
        
    amount = col1.number_input("Amount", min_value=0.0, value=100.0)
    submit = st.form_submit_button("Convert")
    
if submit:
    if from_currency == to_currency:
        st.warning("Please select different currencies")
    elif from_currency not in rates or to_currency not in rates:
        st.error("Invalid currency selected.")
    else:
        rate = rates[to_currency] / rates[from_currency]
        converted = amount * rate
        st.metric(
            label=f"{amount:,.2f} {from_currency}",
            value=f"{converted:,.2f} {to_currency}",
            delta=f"Rate: {rate:.4f}"
        )
        
with st.expander("Historical Rate Trend"):
    if submit:
        historical_df = fetch_historical(from_currency, to_currency)
        st.line_chart(historical_df)
    else:
        st.info("Submit a conversion to view history.")

st.markdown("---")
st.caption("Built with Streamlit: caching, forms, charts, session state, and API integration.")

