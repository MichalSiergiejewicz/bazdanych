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
    <script>
        const canvas = document.getElementById('sokoCanvas'); const ctx = canvas.getContext('2d'); const size = 40;
        const initialMap = [
            [1,1,1,1,1,1,1,1,1,1], [1,0,0,0,1,0,0,0,2,1], [1,0,3,0,0,0,3,0,0,1],
            [1,0,2,1,1,1,0,0,0,1], [1,0,0,0,4,0,0,3,0,1], [1,1,1,0,0,0,1,1,0,1],
            [1,2,0,0,3,0,0,0,0,1], [1,1,1,1,1,1,1,1,1,1]
        ];
        let map, p;

        function resetGame() {
            map = JSON.parse(JSON.stringify(initialMap));
            p = {x: 4, y: 4};
            draw();
        }

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
            if(dx===0 && dy===0) return;
            
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
    components.html(sokoban_html, height=480)

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
            x=alt.X('nazwa:N', sort='-y'), y='liczba:Q',
            color=alt.Color('kolor:N', scale=None), tooltip=['nazwa', 'liczba']
        ).properties(height=350)
        line = alt.Chart(pd.DataFrame({'y': [30]})).mark_rule(color='red', strokeDash=[5,5]).encode(y='y:Q')
        st.altair_chart(chart + line, use_container_width=True)

        st.divider()
        with st.expander("➕ Dodaj produkt"):
            kat_res = supabase.table("kategorie").select("id, nazwa").execute()
            kat_opcje = {k["nazwa"]: k["id"] for k in kat_res.data}
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
                c1, c2, c3, c4 = st.columns([3, 2, 1, 1])
                c1.write(f"**{row['nazwa']}**")
                m, v, p = c2.columns([1,2,1])
                if m.button("➖", key=f"m_{row['id']}"): update_stock(row['id'], row['liczba']-1)
                v.write(f"{row['liczba']} szt.")
                if p.button("➕", key=f"p_{row['id']}"): update_stock(row['id'], row['liczba']+1)
                c3.write(f"{row['cena']:.2f} zł")
                if c4.button("🗑️", key=f"d_{row['id']}"):
                    supabase.table("produkty").delete().eq("id", row['id']).execute()
                    st.rerun()
    else:
        st.warning("Baza jest pusta. Dodaj kategorie i produkty!")
