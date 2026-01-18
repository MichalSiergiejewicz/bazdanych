import streamlit as st
from supabase import create_client, Client
import pandas as pd
import altair as alt

# --- KONFIGURACJA POŁĄCZENIA ---
# Dane pobierane z st.secrets w Streamlit Cloud
# Upewnij się, że w Settings -> Secrets masz SUPABASE_URL i SUPABASE_KEY
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]

supabase: Client = create_client(URL, KEY)

st.set_page_config(page_title="Magazyn Supabase", layout="wide")
st.title("📊 System Zarządzania Magazynem")

# Menu boczne
menu = ["Produkty & Wykres", "Kategorie"]
choice = st.sidebar.selectbox("Nawigacja", menu)

# --- 1. SEKCJA KATEGORII ---
if choice == "Kategorie":
    st.header("Zarządzanie Kategoriami")
    
    with st.expander("➕ Dodaj nową kategorię"):
        nazwa_kat = st.text_input("Nazwa kategorii")
        opis_kat = st.text_area("Opis")
        if st.button("Zapisz kategorię"):
            if nazwa_kat:
                supabase.table("kategorie").insert({"nazwa": nazwa_kat, "opis": opis_kat}).execute()
                st.success("Kategoria dodana!")
                st.rerun()

    st.subheader("Lista kategorii")
    kategorie = supabase.table("kategorie").select("*").execute()
    if kategorie.data:
        for kat in kategorie.data:
            col1, col2 = st.columns([4, 1])
            col1.write(f"**{kat['nazwa']}** — {kat['opis'] or 'Brak opisu'}")
            if col2.button("Usuń", key=f"kat_{kat['id']}"):
                supabase.table("kategorie").delete().eq("id", kat["id"]).execute()
                st.rerun()
    else:
        st.info("Brak kategorii.")

# --- 2. SEKCJA PRODUKTÓW I WYKRESU ---
elif choice == "Produkty & Wykres":
    st.header("Stan Magazynowy")
    
    # Pobranie kategorii do formularza dodawania
    kat_res = supabase.table("kategorie").select("id, nazwa").execute()
    kat_opcje = {k["nazwa"]: k["id"] for k in kat_res.data}

    with st.expander("➕ Dodaj nowy produkt"):
        if not kat_opcje:
