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
            st.warning("Najpierw dodaj kategorię w zakładce Kategorie!")
        else:
            p_nazwa = st.text_input("Nazwa produktu")
            p_liczba = st.number_input("Ilość", min_value=0, step=1)
            p_cena = st.number_input("Cena", min_value=0.0, step=0.01)
            p_kat = st.selectbox("Kategoria", options=list(kat_opcje.keys()))
            
            if st.button("Dodaj produkt"):
                if p_nazwa:
                    supabase.table("produkty").insert({
                        "nazwa": p_nazwa,
                        "liczba": p_liczba,
                        "cena": p_cena,
                        "kategoria_id": kat_opcje[p_kat]
                    }).execute()
                    st.success("Produkt dodany!")
                    st.rerun()

    # Pobranie danych do tabeli i wykresu
    res = supabase.table("produkty").select("*, kategorie(nazwa)").execute()
    
    if res.data:
        df = pd.DataFrame(res.data)
        
        # --- WYKRES Z CZERWONĄ LINIĄ ---
        st.subheader("📈 Wykres dostępności produktów")
        
        # 1. Warstwa słupków
        bars = alt.Chart(df).mark_bar(color='#1f77b4').encode(
            x=alt.X('nazwa:N', title='Produkt', sort='-y'),
            y=alt.Y('liczba:Q', title='Ilość w sztukach'),
            tooltip=['nazwa', 'liczba', 'cena']
        )

        # 2. Warstwa czerwonej linii progowej (y=30)
        line = alt.Chart(pd.DataFrame({'y': [30]})).mark_rule(
            color='red', 
            strokeWidth=2, 
            strokeDash=[5, 5]
        ).encode(y='y:Q')

        # 3. Warstwa tekstu "Niski poziom"
        text = alt.Chart(pd.DataFrame({'y': [30], 't': ['Niski poziom']})).mark_text(
            align='left', dx=5, dy=-10, color='red', fontWeight='bold'
        ).encode(y='y:Q', text='t:N')

        # Złożenie wykresu
        st.altair_chart((bars + line + text).properties(height=400), use_container_width=True)
        
        # --- LISTA PRODUKTÓW ---
        st.subheader("📋 Szczegóły i edycja")
        for p in res.data:
            c1, c2, c3 = st.columns([3, 2, 1])
            kat_name = p.get('kategorie', {}).get('nazwa', 'Brak')
            c1.write(f"**{p['nazwa']}** (Kat: {kat_name})")
            c2.write(f"{p['liczba']} szt. | {p['cena']} PLN")
            if c3.button("Usuń", key=f"prod_{p['id']}"):
                supabase.table("produkty").delete().eq("id", p["id"]).execute()
                st.rerun()
    else:
        st.info("Brak produktów w bazie.")
