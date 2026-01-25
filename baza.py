import streamlit as st
from supabase import create_client, Client
import pandas as pd
import altair as alt
import streamlit.components.v1 as components

# --- KONFIGURACJA POŁĄCZENIA ---
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(URL, KEY)

st.set_page_config(page_title="Magazyn Pro + Snake", layout="wide")

# Funkcja pomocnicza do aktualizacji ilości
def update_stock(product_id, new_count):
    if new_count >= 0:
        supabase.table("produkty").update({"liczba": new_count}).eq("id", product_id).execute()
        st.rerun()

st.sidebar.title("🎮 Magazyn Menu")
menu = ["Produkty & Dashboard", "Kategorie", "Przerwa na Snake'a"]
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

# --- 2. PRZERWA NA SNAKE'A (NOWOŚĆ) ---
elif choice == "Przerwa na Snake'a":
    st.header("🐍 Chwila relaksu: Snake Game")
    st.write("Używaj strzałek na klawiaturze, aby sterować.")
    
    snake_code = """
    <canvas id="gc" width="400" height="400" style="border:2px solid #1f77b4; display: block; margin: 0 auto;"></canvas>
    <script>
    window.onload=function() {
        canv=document.getElementById("gc");
        ctx=canv.getContext("2d");
        document.addEventListener("keydown",keyPush);
        setInterval(game,1000/15);
    }
    px=py=10; gs=20; tc=20; ax=ay=15; xv=yv=0; trail=[]; tail=5;
    function game() {
        px+=xv; py+=yv;
        if(px<0) px=tc-1; if(px>tc-1) px=0; if(py<0) py=tc-1; if(py>tc-1) py=0;
        ctx.fillStyle="black"; ctx.fillRect(0,0,canv.width,canv.height);
        ctx.fillStyle="lime";
        for(var i=0;i<trail.length;i++) {
            ctx.fillRect(trail[i].x*gs,trail[i].y*gs,gs-2,gs-2);
            if(trail[i].x==px && trail[i].y==py) tail=5;
        }
        trail.push({x:px,y:py});
        while(trail.length>tail) { trail.shift(); }
        if(ax==px && ay==py) { tail++; ax=Math.floor(Math.random()*tc); ay=Math.floor(Math.random()*tc); }
        ctx.fillStyle="red"; ctx.fillRect(ax*gs,ay*gs,gs-2,gs-2);
    }
    function keyPush(evt) {
        switch(evt.keyCode) {
            case 37: xv=-1;yv=0; break;
            case 38: xv=0;yv=-1; break;
            case 39: xv=1;yv=0; break;
            case 40: xv=0;yv=1; break;
        }
    }
    </script>
    """
    components.html(snake_code, height=450)
    st.info("Zadbaj o magazyn, a w nagrodę zjedz kilka czerwonych pikseli!")

# --- 3. PRODUKTY & DASHBOARD ---
else:
    res = supabase.table("produkty").select("*, kategorie(nazwa)").execute()
    df = pd.DataFrame(res.data) if res.data else pd.DataFrame()

    if not df.empty:
        total_value = (df['liczba'] * df['cena']).sum()
        low_stock_items = df[df['liczba'] < 30].shape[0]
        
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Liczba Produktów", len(df))
        col_b.metric("Wartość Magazynu", f"{total_value:,.2f} PLN")
        col_c.metric("Niski stan ( < 30 )", low_stock_items, delta=-low_stock_items, delta_color="inverse")

        st.divider()

        st.subheader("📈 Wizualizacja Stanów")
        df['kolor'] = df['liczba'].apply(lambda x: 'red' if x < 30 else '#1f77b4')

        chart = alt.Chart(df).mark_bar().encode(
            x=alt.X('nazwa:N', title='Produkt', sort='-y'),
            y=alt.Y('liczba:Q', title='Sztuki'),
            color=alt.Color('kolor:N', scale=None),
            tooltip=['nazwa', 'liczba', 'cena']
        ).properties(height=350)

        line = alt.Chart(pd.DataFrame({'y': [30]})).mark_rule(color='red', strokeDash=[5,5]).encode(y='y:Q')
        st.altair_chart(chart + line, use_container_width=True)

        st.divider()
        st.subheader("📦 Zarządzanie Ilością")
        
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

        for index, row in df.iterrows():
            with st.container():
                c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
                kat_name = row['kategorie']['nazwa'] if row['kategorie'] else "Brak"
                c1.write(f"**{row['nazwa']}** ({kat_name})")
                
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
