import streamlit as st
from supabase import create_client, Client
import pandas as pd
import altair as alt
import streamlit.components.v1 as components

# --- KONFIGURACJA POŁĄCZENIA ---
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(URL, KEY)

st.set_page_config(page_title="Magazyn Pro + Tło", layout="wide")

# --- KOD CSS DLA TŁA OBRAZKOWEGO ---
# Obrazek z Unsplash (duży magazyn, wolna licencja)
background_image_url = "https://images.unsplash.com/photo-1627384113717-4020a7b05421?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"

st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url({background_image_url});
        background-size: cover;
        background-attachment: fixed; /* Tło pozostaje w miejscu przy przewijaniu */
        background-position: center;
    }}
    /* Dodatkowe style, aby treść była czytelna na tle */
    .stApp > header, .stApp > div {{
        background-color: rgba(0, 0, 0, 0.5); /* Półprzezroczyste tło dla czytelności */
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 10px;
    }}
    .st-emotion-cache-18ni7ap {{ /* Sidebar background */
        background-color: rgba(15, 15, 20, 0.85); /* Ciemniejsze i bardziej przezroczyste tło sidebara */
    }}
    h1, h2, h3, h4, h5, h6, p, .stMarkdown, .stSelectbox, .stNumberInput, .stTextInput, .stTextArea {{
        color: white !important; /* Biały tekst dla lepszej czytelności */
        text-shadow: 1px 1px 3px rgba(0,0,0,0.8); /* Lekki cień dla tekstu */
    }}
    .stButton > button {{
        background-color: #1f77b4; /* Kolor przycisków */
        color: white;
    }}
    .stButton > button:hover {{
        background-color: #2e8fd8; /* Kolor przycisków po najechaniu */
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# --- KONIEC KODU CSS ---


# Funkcja pomocnicza do aktualizacji ilości
def update_stock(product_id, new_count):
    if new_count >= 0:
        supabase.table("produkty").update({"liczba": new_count}).eq("id", product_id).execute()
        st.rerun()

# --- BOCZNE MENU ---
st.sidebar.title("📦 Magazyn System")

# 1. Mapa Warszawy
st.sidebar.subheader("📍 Lokalizacja")
warszawa_coords = pd.DataFrame({'lat': [52.2297], 'lon': [21.0122]})
st.sidebar.map(warszawa_coords, zoom=9)

# 2. Nawigacja
menu = ["Produkty & Dashboard", "Kategorie", "Przerwa na Snake'a", "Magazynier (Sokoban)"]
choice = st.sidebar.selectbox("Nawigacja", menu)

# 3. DUŻY ZEGAR (na dole sidebaru)
st.sidebar.markdown("---")
st.sidebar.subheader("🕒 Czas systemowy")
clock_html = """
<div id="clock" style="
    background-color: #1f77b4; 
    color: white; 
    font-family: 'Courier New', Courier, monospace; 
    font-size: 35px; 
    font-weight: bold; 
    text-align: center; 
    padding: 15px; 
    border-radius: 10px; 
    border: 3px solid #0e1117;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
">00:00:00</div>
