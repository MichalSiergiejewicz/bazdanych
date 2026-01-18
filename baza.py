import streamlit as st
from supabase import create_client, Client

# --- KONFIGURACJA SUPABASE ---
# Dane pobierane z Secrets (bezpieczne wdrożenie)
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]

supabase: Client = create_client(URL, KEY)

st.set_page_config(page_title="Magazyn Supabase", layout="wide")
st.title("📦 System Zarządzania Magazynem")

menu = ["Produkty", "Kategorie"]
choice = st.sidebar.selectbox("Nawigacja", menu)

# --- LOGIKA KATEGORII ---
if choice == "Kategorie":
    st.header("Zarządzanie Kategoriami")
    
    # Formularz dodawania
    with st.expander("➕ Dodaj nową kategorię"):
        nazwa = st.text_input("Nazwa kategorii")
        opis = st.text_area("Opis")
        if st.button("Zapisz kategorię"):
            if nazwa:
                supabase.table("kategorie").insert({"nazwa": nazwa, "opis": opis}).execute()
                st.success("Dodano kategorię!")
                st.rerun()

    # Wyświetlanie listy
    st.subheader("Lista kategorii")
    kategorie = supabase.table("kategorie").select("*").execute()
    
    for kat in kategorie.data:
        col1, col2 = st.columns([4, 1])
        col1.write(f"**{kat['nazwa']}** — {kat['opis'] or 'Brak opisu'}")
        if col2.button("Usuń", key=f"del_kat_{kat['id']}"):
            supabase.table("kategorie").delete().eq("id", kat["id"]).execute()
            st.rerun()

# --- LOGIKA PRODUKTÓW ---
elif choice == "Produkty":
    st.header("Zarządzanie Produktami")
    
    # Pobranie kategorii do selectboxa
    kategorie_res = supabase.table("kategorie").select("id, nazwa").execute()
    kat_opcje = {k["nazwa"]: k["id"] for k in kategorie_res.data}

    # Formularz dodawania
    with st.expander("➕ Dodaj nowy produkt"):
        if not kat_opcje:
            st.warning("Najpierw dodaj kategorię!")
        else:
            p_nazwa = st.text_input("Nazwa produktu")
            p_liczba = st.number_input("Ilość", min_value=0, step=1)
            p_cena = st.number_input("Cena", min_value=0.0, step=0.01)
            p_kat_id = st.selectbox("Wybierz kategorię", options=list(kat_opcje.keys()))
            
            if st.button("Dodaj produkt"):
                supabase.table("produkty").insert({
                    "nazwa": p_nazwa,
                    "liczba": p_liczba,
                    "cena": p_cena,
                    "kategoria_id": kat_opcje[p_kat_id]
                }).execute()
                st.success("Produkt dodany!")
                st.rerun()

    # Wyświetlanie tabeli produktów
    st.subheader("Aktualny stan magazynowy")
    # Join z kategorią, aby wyświetlić nazwę zamiast ID
    produkty = supabase.table("produkty").select("*, kategorie(nazwa)").execute()
    
    if produkty.data:
        for p in produkty.data:
            col1, col2, col3 = st.columns([3, 1, 1])
            kat_name = p.get('kategorie', {}).get('nazwa', 'Brak')
            col1.write(f"**{p['nazwa']}** (Kat: {kat_name})")
            col2.write(f"{p['liczba']} szt. | {p['cena']} PLN")
            if col3.button("Usuń", key=f"del_prod_{p['id']}"):
                supabase.table("produkty").delete().eq("id", p["id"]).execute()
                st.rerun()
    else:
        st.info("Brak produktów w bazie.")
