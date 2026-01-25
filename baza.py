import streamlit as st
from supabase import create_client, Client
import pandas as pd
import altair as alt
import streamlit.components.v1 as components

# --- KONFIGURACJA POŁĄCZENIA ---
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(URL, KEY)

st.set_page_config(page_title="Magazyn Pro + Games", layout="wide")

# Funkcja do aktualizacji ilości w bazie
def update_stock(product_id, new_count):
    if new_count >= 0:
        supabase.table("produkty").update({"liczba": new_count}).eq("id", product_id).execute()
        st.rerun()

# --- BOCZNE MENU ---
st.sidebar.title("📦 Magazyn System")
menu = ["Produkty & Dashboard", "Kategorie", "Przerwa na Snake'a", "Magazynier (Sokoban)"]
choice = st.sidebar.selectbox("Nawigacja", menu)

# --- 1. SEKCJA KATEGORII ---
if choice == "Kategorie":
    st.header("📂 Zarządzanie Kategoriami")
    with st.expander("➕ Dodaj nową kategorię"):
        nazwa_kat = st.text_input("Nazwa kategorii")
        if st.button("Zapisz"):
            if nazwa_kat:
                supabase.table("kategorie").insert({"nazwa": nazwa_kat}).execute()
                st.rerun()
    
    kat_res = supabase.table("kategorie").select("*").execute()
    if kat_res.data:
        for k in kat_res.data:
            c1, c2 = st.columns([4, 1])
            c1.write(f"**{k['nazwa']}**")
            if c2.button("Usuń", key=f"k_{k['id']}"):
                supabase.table("kategorie").delete().eq("id", k['id']).execute()
                st.rerun()

# --- 2. SEKCJA SNAKE ---
elif choice == "Przerwa na Snake'a":
    st.header("🐍 Snake: Warehouse Edition")
    snake_code = """
    <div style="display: flex; flex-direction: column; align-items: center;">
        <canvas id="gc" width="400" height="400" style="border:5px solid #1f77b4; background-image: url('https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=400&h=400&auto=format&fit=crop'); background-size: cover;"></canvas>
        <p>Używaj strzałek. Zbieraj czerwone palety!</p>
    </div>
    <script>
    window.onload=function() {
        canv=document.getElementById("gc"); ctx=canv.getContext("2d");
        document.addEventListener("keydown",keyPush);
        setInterval(game,1000/12);
    }
    px=py=10; gs=20; tc=20; ax=ay=15; xv=yv=0; trail=[]; tail=5;
    function game() {
        px+=xv; py+=yv;
        if(px<0) px=tc-1; if(px>tc-1) px=0; if(py<0) py=tc-1; if(py>tc-1) py=0;
        ctx.fillStyle="rgba(0,0,0,0.5)"; ctx.fillRect(0,0,canv.width,canv.height);
        ctx.fillStyle="#00FF00";
        for(var i=0;i<trail.length;i++) {
            ctx.fillRect(trail[i].x*gs,trail[i].y*gs,gs-2,gs-2);
            if(trail[i].x==px && trail[i].y==py) tail=5;
        }
        trail.push({x:px,y:py});
        while(trail.length>tail) { trail.shift(); }
        if(ax==px && ay==py) { tail++; ax=Math.floor(Math.random()*tc); ay=Math.floor(Math.random()*tc); }
        ctx.fillStyle="#FF4500"; ctx.fillRect(ax*gs,ay*gs,gs-2,gs-2);
    }
    function keyPush(evt) {
        switch(evt.keyCode) {
            case 37: xv=-1;yv=0; break; case 38: xv=0;yv=-1; break;
            case 39: xv=1;yv=0; break; case 40: xv=0;yv=1; break;
        }
    }
    </script>
    """
    components.html(snake_code, height=500)

# --- 3. SEKCJA SOKOBAN (Z RESETEM) ---
elif choice == "Magazynier (Sokoban)":
    st.header("📦 Sokoban: Wyzwanie Logistyczne")
    st.info("Jeśli zablokujesz skrzynię, użyj przycisku RESET pod grą.")

    sokoban_html = """
    <div style="display: flex; flex-direction: column; align-items: center;">
        <canvas id="sokoCanvas" width="400" height="320" style="border:3px solid #333; background: #eee;"></canvas>
        <br>
        <button onclick="resetGame()" style="padding: 10px 20px; background: #1f77b4; color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: bold;">🔄 RESETUJ POZIOM</button>
    </div>
