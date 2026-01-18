import streamlit as st
from supabase import create_client, Client
import pandas as pd
import altair as alt

# --- KONFIGURACJA POŁĄCZENIA ---
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(URL, KEY)

st.set_page_config(page_title="Magazyn Pro", layout="wide")

# Funkcja pomocnicza do aktualizacji ilości
def update_stock(product_id, new_count):
    if new_count >= 0:
        supabase.table("produkty").update({"liczba": new_count}).eq("id", product_id).execute()
        st.rerun()

st.title("🚀 Panel Zarządzania Magazynem")

menu = ["Produkty & Dashboard", "Kategorie"]
choice = st.sidebar.selectbox("Nawigacja", menu)

# --- 1. KATEGORIE ---
if choice == "Kategorie":
    st.header("Zarządzanie Kategoriami")
    with st.expander("➕ Dodaj nową kategorię"):
        nazwa_kat = st.text_input("Nazwa")
        if st.button("Zapisz"):
            supabase.table("kategorie").insert({"nazwa": nazwa_kat}).execute()
            st.rerun()
    
    kat_res = supabase.table("kategorie").select("*").execute()
    for k in kat_res.data:
        c1, c2 = st.columns([4, 1])
        c1.write(f"**{k['nazwa']}**")
        if c2.button("Usuń", key=f"k_{k['id']}"):
            supabase.table("kategorie").delete().eq("id", k['id']).execute()
            st.rerun()

# --- 2. PRODUKTY & DASHBOARD ---
else:
    # Pobranie danych
    res = supabase.table("produkty").select("*, kategorie(nazwa)").execute()
    df = pd.DataFrame(res.data) if res.data else pd.DataFrame()

    if not df.empty:
        # --- SEKCJA KPI (STATYSTYKI) ---
        total_value = (df['liczba'] * df['cena']).sum()
        low_stock_items = df[df['liczba'] < 30].shape[0]
        
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Liczba Produktów", len(df))
        col_b.metric("Wartość Magazynu", f"{total_value:,.2f} PLN")
        col_c.metric("Niski stan ( < 30 )", low_stock_items, delta=-low_stock_items, delta_color="inverse")

        st.divider()

        # --- WYKRES Z INTELIGENTNYM KOLOREM ---
        st.subheader("📈 Wizualizacja Stanów")
        
        # Dodajemy kolumnę koloru do wykresu
        df['kolor'] = df['liczba'].apply(lambda x: 'red' if x < 30 else '#1f77b4')

        chart = alt.Chart(df).mark_bar().encode(
            x=alt.X('nazwa:N', title='Produkt', sort='-y'),
            y=alt.Y('liczba:Q', title='Sztuki'),
            color=alt.Color('kolor:N', scale=None), # scale=None pozwala użyć kolorów z kolumny
            tooltip=['nazwa', 'liczba', 'cena']
        ).properties(height=350)

        # Czerwona linia progowa
        line = alt.Chart(pd.DataFrame({'y': [30]})).mark_rule(color='red', strokeDash=[5,5]).encode(y='y:Q')
        
        st.altair_chart(chart + line, use_container_width=True)

        st.divider()

        # --- EDYTOWALNA LISTA PRODUKTÓW ---
        st.subheader("📦 Zarządzanie Ilością")
        
        # Formularz dodawania (w expanderze żeby nie zajmował miejsca)
        with st.expander("➕ Dodaj nowy produkt"):
            kat_res = supabase.table("kategorie").select("id, nazwa").execute()
            kat_opcje = {k["nazwa"]: k["id"] for k in kat_res.data}
            if kat_opcje:
                n_col1, n_col2, n_col3 = st.columns(3)
                new_n = n_col1.text_input("Nazwa")
                new_l = n_col2.number_input("Ilość", min_value=0, value=0)
                new_c = n_col3.number_input("Cena", min_value=0.0, value=0.0)
                new_k = st.selectbox("Kategoria", list(kat_opcje.keys()))
                if st.button("Dodaj Produkt"):
                    supabase.table("produkty").insert({"nazwa": new_n, "liczba": new_l, "cena": new_c, "kategoria_id": kat_opcje[new_k]}).execute()
                    st.rerun()

        # Tabela edycji
        for index, row in df.iterrows():
            with st.container():
                c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
                kat_name = row['kategorie']['nazwa'] if row['kategorie'] else "Brak"
                c1.write(f"**{row['nazwa']}** ({kat_name})")
                
                # Przyciski +/- do szybkiej edycji
                col_minus, col_num, col_plus = c2.columns([1,2,1])
                if col_minus.button("➖", key=f"min_{row['id']}"):
                    update_stock(row['id'], row['liczba'] - 1)
                col_num.write(f"**{row['liczba']}** szt.")
                if col_plus.button("➕", key=f"plus_{row['id']}"):
                    update_stock(row['id'], row['liczba'] + 1)
                
                c3.write(f"{row['cena']:.2f} PLN")
                if c4.button("🗑️", key=f"del_{row['id']}"):
                    supabase.table("produkty").delete().eq("id", row['id']).execute()
                    st.rerun()
                st.write("---")
    else:
        st.warning("Baza produktów jest pusta. Dodaj kategorie, a potem produkty!")
