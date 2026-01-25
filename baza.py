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

<script>
function updateClock() {
    const now = new Date();
    const h = String(now.getHours()).padStart(2, '0');
    const m = String(now.getMinutes()).padStart(2, '0');
    const s = String(now.getSeconds()).padStart(2, '0');
    document.getElementById('clock').innerText = h + ":" + m + ":" + s;
}
setInterval(updateClock, 1000);
updateClock();
</script>
"""
with st.sidebar:
    components.html(clock_html, height=100)

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
    components.html(snake_code, height=450)

# --- 3. SEKCJA SOKOBAN ---
elif choice == "Magazynier (Sokoban)":
    st.header("📦 Sokoban: Wyzwanie Logistyczne")
    sokoban_html = """
    <div style="display: flex; flex-direction: column; align-items: center;">
        <canvas id="sokoCanvas" width="400" height="320" style="border:3px solid #333; background: #eee;"></canvas>
        <br>
        <button onclick="resetGame()" style="padding: 10px 20px; background: #1f77b4; color: white; border: none; border-radius: 5px; cursor: pointer;">🔄 RESETUJ POZIOM</button>
    </div>
    <script>
        const canvas = document.getElementById('sokoCanvas'); const ctx = canvas.getContext('2d'); const size = 40;
        const initialMap = [[1,1,1,1,1,1,1,1,1,1],[1,0,0,0,1,0,0,0,2,1],[1,0,3,0,0,0,3,0,0,1],[1,0,2,1,1,1,0,0,0,1],[1,0,0,0,4,0,0,3,0,1],[1,1,1,0,0,0,1,1,0,1],[1,2,0,0,3,0,0,0,0,1],[1,1,1,1,1,1,1,1,1,1]];
        let map, p;
        function resetGame() { map = JSON.parse(JSON.stringify(initialMap)); p = {x: 4, y: 4}; draw(); }
        function draw() {
            ctx.clearRect(0,0,400,320);
            for(let y=0; y<map.length; y++) {
                for(let x=0; x<map[y].length; x++) {
                    if(map[y][x] == 1) ctx.fillStyle = '#555';
                    else if(map[y][x] == 2) ctx.fillStyle = '#ffcccc';
                    else if(map[y][x] == 3) ctx.fillStyle = '#8B4513';
                    else if(map[y][x] == 4) ctx.fillStyle = '#1f77b4';
                    else ctx.fillStyle = '#fff';
                    if(map[y][x] !== 0) ctx.fillRect(x*size, y*size, size-2, size-2);
                }
            }
        }
        window.addEventListener('keydown', e => {
            let dx=0, dy=0;
            if(e.key === 'ArrowUp') dy=-1; if(e.key === 'ArrowDown') dy=1;
            if(e.key === 'ArrowLeft') dx=-1; if(e.key === 'ArrowRight') dx=1;
            let nx = p.x + dx, ny = p.y + dy;
            if(map[ny][nx] === 0 || map[ny][nx] === 2) {
                map[p.y][p.x] = (initialMap[p.y][p.x] === 2) ? 2 : 0;
                p.x = nx; p.y = ny; map[ny][nx] = 4;
            } else if(map[ny][nx] === 3) {
                let nnx = nx + dx, nny = ny + dy;
                if(map[nny][nnx] === 0 || map[nny][nnx] === 2) {
                    map[nny][nnx] = 3; map[ny][nx] = 4;
                    map[p.y][p.x] = (initialMap[p.y][p.x] === 2) ? 2 : 0;
                    p.x = nx; p.y = ny;
                }
            }
            draw(); e.preventDefault();
        });
        resetGame();
    </script>
    """
    components.html(sokoban_html, height=450)

# --- 4. SEKCJA PRODUKTY & DASHBOARD ---
else:
    res = supabase.table("produkty").select("*, kategorie(nazwa)").execute()
    df = pd.DataFrame(res.data) if res.data else pd.DataFrame()

    if not df.empty:
        val_total = (df['liczba'] * df['cena']).sum()
        low_stock = df[df['liczba'] < 30].shape[0]
        c1, c2, c3 = st.columns(3)
        c1.metric("Produkty", len(df))
        c2.metric("Wartość", f"{val_total:,.2f} PLN")
        c3.metric("Niski stan", low_stock, delta=-low_stock, delta_color="inverse")

        st.divider()
        st.subheader("📈 Stan magazynowy")
        df['kolor'] = df['liczba'].apply(lambda x: 'red' if x < 30 else '#1f77b4')
        chart = alt.Chart(df).mark_bar().encode(
            x=alt.
