import streamlit as st
from supabase import create_client, Client
import pandas as pd
import altair as alt

# --- 1. KONFIGURACJA POŁĄCZENIA ---
# Dane pobierane z st.secrets (skonfiguruj to w panelu Streamlit!)
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]

supabase: Client = create_client(URL, KEY)

st.set_page_config(page_title="Magazyn i Wykresy", layout="wide")
st.title("📊 System Magazynowy z Wykresami")

# Boczne menu
menu = ["Produkty & Wykres", "Kategorie"]
choice = st.sidebar.selectbox("Nawigacja", menu)

# --- 2. LOGIKA KATEGORII ---
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
    for kat in kategorie.data:
        col1, col2 = st.columns([4, 1])
        col1.write(f"**{kat['nazwa']}**")
        if col2.button("Usuń", key=f"kat_{kat['id']}"):
            supabase.table("kategorie").delete().eq("id", kat["id"]).execute()
            st.rerun()

# --- 3. LOGIKA PRODUKTÓW I WYKRESU ---
elif choice == "Produkty & Wykres":
    st.header("Zarządzanie Produktami")
    
    # Pobranie kategorii do formularza
    kat_res = supabase.table("kategorie").select("id, nazwa").execute()
    kat_opcje = {k["nazwa"]: k["id"] for k in kat_res.data}

    with st.expander("➕ Dodaj nowy produkt"):
        if not kat_opcje:
            st.warning("Dodaj najpierw kategorię w sekcji Kategorie!")
        else:
            p_nazwa = st.text_input("Nazwa produktu")
            p_liczba = st.number_input("Ilość (liczba)", min_value=0, step=1)
            p_cena = st.number_input("Cena", min_value=0.0, step=0.01)
            p_kat = st.selectbox("Kategoria", options=list(kat_opcje.keys()))
            
            if st.button("Dodaj do bazy"):
                supabase.table("produkty").insert({
                    "nazwa": p_nazwa,
                    "liczba": p_liczba,
                    "cena": p_cena,
                    "kategoria_id": kat_opcje[p_kat]
                }).execute()
                st.success("Produkt dodany!")
                st.rerun()

    # POBIERANIE DANYCH DO TABELI I WYKRESU
    res = supabase.table("produkty").select("*, kategorie(nazwa)").execute()
    
    if res.data:
        df = pd.DataFrame(res.data)
        
        # --- SEKCJA WYKRESU ---
        st.subheader("📈 Wizualizacja stanu magazynowego")
        
        # Tworzenie wykresu słupkowego w Altair
        chart = alt.Chart(df).mark_bar(color='#1f77b4').encode(
            x=alt.X('nazwa:N', title='Produkt', sort='-y'),
            y=alt.Y('liczba:Q', title='Ilość sztuk'),
            tooltip=['nazwa', 'liczba', 'cena']
        ).properties(height=400)
        
        st.altair_chart(chart, use_container_width=True)
        
        # --- SEKCJA LISTY ---
        st.subheader("📋 Lista produktów")
        for p in res.data:
            c1, c2, c3 = st.columns([3, 2, 1])
            kat_n = p.get('kategorie', {}).get('nazwa', 'Brak')
            c1.write(f"**{p['nazwa']}** ({kat_n})")
            c2.write(f"{p['liczba']} szt. | {p['cena']} PLN")
            if c3.button("Usuń", key=f"prod_{p['id']}"):
                supabase.table("produkty").delete().eq("id", p["id"]).execute()
                st.rerun()
    else:
        st.info("Baza produktów jest pusta.")
