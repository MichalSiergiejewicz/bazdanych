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

# --- POPRAWIONY KOD CSS DLA TŁA ---
background_image_url = "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2000&auto=format&fit=crop"

st.markdown(
    f"""
    <style>
    .stApp {{
        background: linear-gradient(rgba(0,0,0,0.65), rgba(0,0,0,0.65)), url("{background_image_url}") !important;
        background-size: cover !important;
        background-attachment: fixed !important;
        background-position: center !important;
    }}
    [data-testid="stSidebar"] {{
        background-color: rgba(20, 20, 25, 0.9) !important;
        backdrop-filter: blur(10px);
    }}
    .stMetric, [data-testid="stExpander"], .stTable {{
        background-color: rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 10px;
    }}
    h1, h2, h3, p, span, label, .stMetric div {{
        color: white !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.7) !important;
    }}
    .stButton > button {{
        background-color: #1f77b4 !important;
        color: white !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# --- FUNKCJE POMOCNICZE ---
def update_stock(product_id, new_count):
    if new_count >= 0:
        supabase.table("produkty").update({"liczba": new_count}).eq("id", product_id).execute()
        st.rerun()

# --- BOCZNE MENU ---
st.sidebar.title("📦 Magazyn System")

# Mapa Warszawy
st.sidebar.subheader("📍 Lokalizacja")
warszawa_coords = pd.DataFrame({'lat': [52.2297], 'lon': [21.0122]})
st.sidebar.map(warszawa_coords, zoom=9)

menu = ["Produkty & Dashboard", "Kategorie", "Przerwa na Snake'a", "Magazynier (Sokoban)"]
choice = st.sidebar.selectbox("Nawigacja", menu)

# ZEGAR
st.sidebar.markdown("---")
clock_html = """
<div id="clock" style="background: #1f77b4; color: white; font-family: monospace; font-size: 30px; font-weight: bold; text-align: center; padding: 10px; border-radius: 8px;">00:00:00</div>
<script>
function updateClock() { document.getElementById('clock').innerText = new Date().toLocaleTimeString(); }
setInterval(updateClock, 1000); updateClock();
</script>
"""
with st.sidebar:
    components.html(clock_html, height=80)

# --- LOGIKA STRON ---
if choice == "Kategorie":
    st.header("📂 Zarządzanie Kategoriami")
    with st.expander("➕ Dodaj nową kategorię"):
        nazwa_kat = st.text_input("Nazwa kategorii")
        if st.button("Zapisz"):
            if nazwa_kat:
                supabase.table("kategorie").insert({"nazwa": nazwa_kat}).execute()
                st.rerun()
    
    kat_res = supabase.table("kategorie").select("*").execute()
    for k in (kat_res.data or []):
        c1, c2 = st.columns([4, 1])
        c1.write(f"**{k['nazwa']}**")
        if c2.button("Usuń", key=f"k_{k['id']}"):
            supabase.table("kategorie").delete().eq("id", k['id']).execute()
            st.rerun()

elif choice == "Przerwa na Snake'a":
    st.header("🐍 Snake: Warehouse Edition")
    snake_code = """<div style="display:flex;justify-content:center;"><canvas id="gc" width="400" height="400" style="border:5px solid #1f77b4;background:black;"></canvas></div><script>window.onload=function(){canv=document.getElementById("gc");ctx=canv.getContext("2d");document.addEventListener("keydown",keyPush);setInterval(game,1000/12)}px=py=10;gs=20;tc=20;ax=ay=15;xv=yv=0;trail=[];tail=5;function game(){px+=xv;py+=yv;if(px<0)px=tc-1;if(px>tc-1)px=0;if(py<0)py=tc-1;if(py>tc-1)py=0;ctx.fillStyle="black";ctx.fillRect(0,0,400,400);ctx.fillStyle="lime";for(var i=0;i<trail.length;i++){ctx.fillRect(trail[i].x*gs,trail[i].y*gs,gs-2,gs-2);if(trail[i].x==px&&trail[i].y==py)tail=5}trail.push({x:px,y:py});while(trail.length>tail)trail.shift();if(ax==px&&ay==py){tail++;ax=Math.floor(Math.random()*tc);ay=Math.floor(Math.random()*tc)}ctx.fillStyle="red";ctx.fillRect(ax*gs,ay*gs,gs-2,gs-2)}function keyPush(e){switch(e.keyCode){case 37:xv=-1;yv=0;break;case 38:xv=0;yv=-1;break;case 39:xv=1;yv=0;break;case 40:xv=0;yv=1;break}}</script>"""
    components.html(snake_code, height=450)

elif choice == "Magazynier (Sokoban)":
    st.header("📦 Sokoban")
    sokoban_html = """<div style="text-align:center"><canvas id="s" width="400" height="320" style="border:2px solid white;background:#eee;"></canvas><br><button onclick="r()" style="margin-top:10px;padding:10px">RESET</button></div><script>const c=document.getElementById('s').getContext('2d');const sz=40;const iM=[[1,1,1,1,1,1,1,1,1,1],[1,0,0,0,1,0,0,0,2,1],[1,0,3,0,0,0,3,0,0,1],[1,0,2,1,1,1,0,0,0,1],[1,0,0,0,4,0,0,3,0,1],[1,1,1,0,0,0,1,1,0,1],[1,2,0,0,3,0,0,0,0,1],[1,1,1,1,1,1,1,1,1,1]];let m,p;function r(){m=JSON.parse(JSON.stringify(iM));p={x:4,y:4};d()}function d(){c.clearRect(0,0,400,320);for(let y=0;y<m.length;y++)for(let x=0;x<m[y].length;x++){if(m[y][x]==1)c.fillStyle='#555';else if(m[y][x]==2)c.fillStyle='#fcc';else if(m[y][x]==3)c.fillStyle='#841';else if(m[y][x]==4)c.fillStyle='#17b';else c.fillStyle='#fff';if(m[y][x]!=0)c.fillRect(x*sz,y*sz,sz-2,sz-2)}}window.onkeydown=e=>{let dx=0,dy=0;if(e.key=='ArrowUp')dy=-1;if(e.key=='ArrowDown')dy=1;if(e.key=='ArrowLeft')dx=-1;if(e.key=='ArrowRight')dx=1;let nx=p.x+dx,ny=p.y+dy;if(m[ny][nx]==0||m[ny][nx]==2){m[p.y][p.x]=(iM[p.y][p.x]==2)?2:0;p.x=nx;p.y=ny;m[ny][nx]=4}else if(m[ny][nx]==3){let nnx=nx+dx,nny=ny+dy;if(m[nny][nnx]==0||m[nny][nnx]==2){m[nny][nnx]=3;m[ny][nx]=4;m[p.y][p.x]=(iM[p.y][p.x]==2)?2:0;p.x=nx;p.y=ny}}d();e.preventDefault()};r()</script>"""
    components.html(sokoban_html, height=450)

else:
    # DASHBOARD
    res = supabase.table("produkty").select("*, kategorie(nazwa)").execute()
    df = pd.DataFrame(res.data) if res.data else pd.DataFrame()

    if not df.empty:
        val_total = (df['liczba'] * df['cena']).sum()
        low_stock = df[df['liczba'] < 30].shape[0]
        
        c1, c2, c3 = st.columns(3)
        c1.metric("📦 Produkty", len(df))
        c2.metric("💰 Wartość", f"{val_total:,.2f} PLN")
        c3.metric("⚠️ Niski stan", low_stock, delta=-low_stock, delta_color="inverse")

        st.divider()
        st.subheader("📊 Stan magazynowy")
        
        # POPRAWKA WYKRESU: Usuwamy background='transparent' i używamy warstw Altair ostrożnie
        df['kolor'] = df['liczba'].apply(lambda x: 'red' if x < 30 else '#1f77b4')
        
        base = alt.Chart(df).encode(
            x=alt.X('nazwa:N', sort='-y', axis=alt.Axis(labelColor='white', titleColor='white')),
            y=alt.Y('liczba:Q', axis=alt.Axis(labelColor='white', titleColor='white'))
        )

        bars = base.mark_bar().encode(
            color=alt.Color('kolor:N', scale=None),
            tooltip=['nazwa', 'liczba']
        )

        rule = alt.Chart(pd.DataFrame({'y': [30]})).mark_rule(color='white', strokeDash=[5,5]).encode(y='y:Q')
        
        # Wyświetlamy wykres - Altair czasami gryzie się z nakładaniem warstw przy różnych źródłach danych, 
        # więc najbezpieczniej wyświetlić same słupki lub upewnić się, że oba wykresy są poprawnie skonfigurowane.
        st.altair_chart(bars + rule, use_container_width=True)

        st.divider()
        # Sekcja dodawania i listy produktów (pozostała bez zmian)
        with st.expander("➕ Dodaj produkt"):
            kat_res = supabase.table("kategorie").select("id, nazwa").execute()
            kat_opcje = {k["nazwa"]: k["id"] for k in (kat_res.data or [])}
            if kat_opcje:
                n1, n2, n3 = st.columns(3)
                name = n1.text_input("Nazwa")
                stock = n2.number_input("Ilość", min_value=0)
                price = n3.number_input("Cena", min_value=0.0)
                cat = st.selectbox("Kategoria", list(kat_opcje.keys()))
                if st.button("Dodaj"):
                    supabase.table("produkty").insert({"nazwa": name, "liczba": stock, "cena": price, "kategoria_id": kat_opcje[cat]}).execute()
                    st.rerun()

        for _, row in df.iterrows():
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
                col1.write(f"**{row['nazwa']}**")
                m, v, p = col2.columns([1,2,1])
                if m.button("➖", key=f"m_{row['id']}"): update_stock(row['id'], row['liczba']-1)
                v.write(f"{row['liczba']} szt.")
                if p.button("➕", key=f"p_{row['id']}"): update_stock(row['id'], row['liczba']+1)
                col3.write(f"{row['cena']:.2f} zł")
                if col4.button("🗑️", key=f"d_{row['id']}"):
                    supabase.table("produkty").delete().eq("id", row['id']).execute()
                    st.rerun()
    else:
        st.warning("Baza jest pusta!")
