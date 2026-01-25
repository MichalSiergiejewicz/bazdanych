import streamlit as st
from supabase import create_client, Client
import pandas as pd
import altair as alt
import streamlit.components.v1 as components

# --- KONFIGURACJA POŁĄCZENIA ---
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(URL, KEY)

st.set_page_config(page_title="Magazyn Pro", layout="wide")

# --- KOD CSS ---
background_image_url = "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2000&auto=format&fit=crop"

st.markdown(
    f"""
    <style>
    .stApp {{
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url("{background_image_url}") !important;
        background-size: cover !important;
        background-attachment: fixed !important;
    }}
    [data-testid="stSidebar"] {{ background-color: rgba(0, 0, 0, 0.9) !important; }}
    h1, h2, h3, p, label {{ color: white !important; text-shadow: 2px 2px 2px black; }}
    .stMetric {{ background: rgba(0,0,0,0.7); padding: 10px; border-radius: 10px; border: 1px solid #444; }}
    </style>
    """,
    unsafe_allow_html=True
)

def update_stock(product_id, new_count):
    if new_count >= 0:
        supabase.table("produkty").update({"liczba": new_count}).eq("id", product_id).execute()
        st.rerun()

# --- SIDEBAR ---
st.sidebar.title("📦 Menu")
menu = ["Dashboard", "Kategorie", "Snake", "Sokoban"]
choice = st.sidebar.selectbox("Wybierz", menu)

# --- DASHBOARD ---
if choice == "Dashboard":
    res = supabase.table("produkty").select("*, kategorie(nazwa)").execute()
    df = pd.DataFrame(res.data) if res.data else pd.DataFrame()

    if not df.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("📦 Produkty", len(df))
        c2.metric("💰 Wartość", f"{(df['liczba'] * df['cena']).sum():,.2f} PLN")
        c3.metric("⚠️ Niski stan", df[df['liczba'] < 30].shape[0])

        st.subheader("📊 Stan magazynowy")
        
        # --- ROZWIĄZANIE PROBLEMU WIDOCZNOŚCI ---
        df['kolor'] = df['liczba'].apply(lambda x: '#ff4b4b' if x < 30 else '#1f77b4')
        
        chart = alt.Chart(df).mark_bar(stroke="white", strokeWidth=0.5).encode(
            x=alt.X('nazwa:N', sort='-y', title="Produkt", 
                    axis=alt.Axis(labelColor='yellow', titleColor='white', labelFontSize=14, labelAngle=-45, labelPadding=10)),
            y=alt.Y('liczba:Q', title="Sztuki", 
                    axis=alt.Axis(labelColor='white', titleColor='white', grid=True, gridColor='#444')),
            color=alt.Color('kolor:N', scale=None),
            tooltip=['nazwa', 'liczba']
        ).properties(
            height=400,
            background='#111111' # Wymuszamy czarne tło pod samym wykresem
        ).configure_view(
            strokeWidth=0
        ).configure_axis(
            domainColor='white',
            tickColor='white'
        )
        
        st.altair_chart(chart, use_container_width=True)

        st.divider()
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

# --- SNAKE ---
elif choice == "Snake":
    st.header("🐍 Snake")
    # Naprawiony kod Snake'a - dodane "focus" i obsługa klawiszy
    snake_code = """
    <div style="display:flex;justify-content:center;flex-direction:column;align-items:center;">
        <canvas id="gc" width="400" height="400" style="border:5px solid #1f77b4;background:black;" tabindex="1"></canvas>
        <p style="color:yellow; font-size: 20px;">Kliknij w czarny kwadrat, aby zacząć sterować!</p>
    </div>
    <script>
    var c=document.getElementById("gc"), x=c.getContext("2d");
    var px=10, py=10, gs=20, tc=20, ax=15, ay=15, xv=0, yv=0, trail=[], tail=5;
    
    function game() {
        px+=xv; py+=yv;
        if(px<0)px=tc-1; if(px>tc-1)px=0; if(py<0)py=tc-1; if(py>tc-1)py=0;
        x.fillStyle="black"; x.fillRect(0,0,c.width,c.height);
        x.fillStyle="lime";
        for(var i=0;i<trail.length;i++) {
            x.fillRect(trail[i].x*gs,trail[i].y*gs,gs-2,gs-2);
            if(trail[i].x==px && trail[i].y==py) tail=5;
        }
        trail.push({x:px,y:py});
        while(trail.length>tail) trail.shift();
        if(ax==px && ay==py) { tail++; ax=Math.floor(Math.random()*tc); ay=Math.floor(Math.random()*tc); }
        x.fillStyle="red"; x.fillRect(ax*gs,ay*gs,gs-2,gs-2);
    }
    document.onkeydown=function(e) {
        switch(e.keyCode) {
            case 37: if(xv!=1){xv=-1;yv=0;} break;
            case 38: if(yv!=1){xv=0;yv=-1;} break;
            case 39: if(xv!=-1){xv=1;yv=0;} break;
            case 40: if(yv!=-1){xv=0;yv=1;} break;
        }
    };
    setInterval(game, 100);
    c.focus();
    </script>
    """
    components.html(snake_code, height=500)

# --- POZOSTAŁE SEKCJE ---
elif choice == "Kategorie":
    st.header("📂 Kategorie")
    nazwa_kat = st.text_input("Nowa kategoria")
    if st.button("Dodaj"):
        supabase.table("kategorie").insert({"nazwa": nazwa_kat}).execute()
        st.rerun()
    res = supabase.table("kategorie").select("*").execute()
    for k in (res.data or []):
        st.write(f"- {k['nazwa']}")

elif choice == "Sokoban":
    st.header("📦 Sokoban")
    sokoban_html = """<div style="text-align:center"><canvas id="s" width="400" height="320" style="border:2px solid white;background:#eee;"></canvas><br><button onclick="r()" style="margin-top:10px;padding:10px">RESET</button></div><script>const c=document.getElementById('s').getContext('2d');const sz=40;const iM=[[1,1,1,1,1,1,1,1,1,1],[1,0,0,0,1,0,0,0,2,1],[1,0,3,0,0,0,3,0,0,1],[1,0,2,1,1,1,0,0,0,1],[1,0,0,0,4,0,0,3,0,1],[1,1,1,0,0,0,1,1,0,1],[1,2,0,0,3,0,0,0,0,1],[1,1,1,1,1,1,1,1,1,1]];let m,p;function r(){m=JSON.parse(JSON.stringify(iM));p={x:4,y:4};d()}function d(){c.clearRect(0,0,400,320);for(let y=0;y<m.length;y++)for(let x=0;x<m[y].length;x++){if(m[y][x]==1)c.fillStyle='#555';else if(m[y][x]==2)c.fillStyle='#fcc';else if(m[y][x]==3)c.fillStyle='#841';else if(m[y][x]==4)c.fillStyle='#17b';else c.fillStyle='#fff';if(m[y][x]!=0)c.fillRect(x*sz,y*sz,sz-2,sz-2)}}window.onkeydown=e=>{let dx=0,dy=0;if(e.key=='ArrowUp')dy=-1;if(e.key=='ArrowDown')dy=1;if(e.key=='ArrowLeft')dx=-1;if(e.key=='ArrowRight')dx=1;let nx=p.x+dx,ny=p.y+dy;if(m[ny][nx]==0||m[ny][nx]==2){m[p.y][p.x]=(iM[p.y][p.x]==2)?2:0;p.x=nx;p.y=ny;m[ny][nx]=4}else if(m[ny][nx]==3){let nnx=nx+dx,nny=ny+dy;if(m[nny][nnx]==0||m[nny][nnx]==2){m[nny][nnx]=3;m[ny][nx]=4;m[p.y][p.x]=(iM[p.y][p.x]==2)?2:0;p.x=nx;p.y=ny}}d();e.preventDefault()};r()</script>"""
    components.html(sokoban_html, height=450)
