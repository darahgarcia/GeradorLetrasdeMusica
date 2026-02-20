from mod_Generator import *
import streamlit as st
import pandas as pd
import re


# Config
st.set_page_config(page_title="🎤 Lyric Generator", layout="wide")

# Nav
page = st.sidebar.selectbox("Selecione: ", ["Gerador de Letras", "Análises"])

# Utilidades

def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = text.replace("\r", "\n")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# Upload de dados
st.sidebar.header("Carregar CSV")
file = st.sidebar.file_uploader("Envie o arquivo CSV com letras", type=["csv"])

if not file:
    st.info("Carregue um CSV para continuar.")
    st.stop()

try:
    df = pd.read_csv(file)
    col = next((c for c in df.columns if "lyric" in c.lower()), None)
    if not col:
        st.error("Não encontrei coluna de letras.")
        st.stop()
    df[col] = df[col].astype(str).apply(clean_text)
except Exception as e:
    st.error(f"Erro ao ler CSV: {e}")
    st.stop()

# Página --------------------- Gerador
if page == "Gerador de Letras":
    st.title("🎶 Gerador de Letras")
    model = SimpleMarkov()
    model.train(df[col].dropna().tolist())
    st.success("Modelo treinado!")

    seed = st.text_input("Palavra inicial (opcional)")
    max_words = st.slider("Número de palavras", 20, 200, 60)

    if st.button("Gerar Letra"):
        lyric = model.generate(max_words=max_words, seed=seed if seed else None)
        st.subheader("Letra Gerada")
        st.write(lyric)
        st.download_button("Baixar como .txt", data=lyric, file_name="letra.txt")

# Página --------------------- Análises

if page == "Análises":
    st.title("📊 Análises do Dataset")

    # Identificar colunas
    album_col = next((c for c in df.columns if "album" in c.lower()), None)
    lyrics_col = next((c for c in df.columns if "lyrics" in c.lower()), None)
    members = ["Harry", "Liam", "Louis", "Niall", "Zayn"]

    # Filtros
    col1, col2 = st.columns(2)
    with col1:
        selected_member = st.selectbox("Filtrar por membro", ["Todos"] + members)
    with col2:
        if album_col:
            albuns = sorted(df[album_col].dropna().unique().tolist())
            selected_album = st.selectbox("Filtrar por álbum", ["Todos"] + albuns)
        else:
            selected_album = "Todos"

    # Aplicação de filtros
    df_filtered = df.copy()
    if selected_album != "Todos" and album_col:
        df_filtered = df_filtered[df_filtered[album_col] == selected_album]

    st.subheader("Informações gerais")
    st.write(f"Total de músicas: {len(df_filtered)}")

    # Contagem por álbum
    if album_col:
        album_counts = df_filtered[album_col].value_counts()
        if not album_counts.empty:
            st.write("Álbum com mais músicas:", album_counts.idxmax(), "-", album_counts.max())
            st.bar_chart(album_counts)

    # Contagem de menções a membros da banda
    if lyrics_col:
        member_counts = {m: df_filtered[lyrics_col].fillna("").str.count(m, flags=re.IGNORECASE).sum() for m in members}
        st.subheader("Menções a membros (total)")
        st.bar_chart(pd.Series(member_counts))

        # Presença de membro por álbum
        if selected_member != "Todos" and album_col:
            st.subheader(f"📌 Presença de {selected_member} por álbum")
            member_album_counts = (
                df_filtered.groupby(album_col)[lyrics_col]
                .apply(lambda x: x.str.count(selected_member, flags=re.IGNORECASE).sum())
            )
            st.bar_chart(member_album_counts)

        # Análise por música em gráfico de barras quando um álbum é selecionado
        if selected_album != "Todos":
            st.subheader(f"🔍 Análise por música - {selected_album}")
            music_counts = {}
            for idx, row in df_filtered.iterrows():
                
                # Usar coluna 'Song' para o título
                title = row.get('Song', f'Música {idx+1}')
                text = row[lyrics_col] if pd.notna(row[lyrics_col]) else ""
                if selected_member != "Todos":
                    count = len(re.findall(selected_member, text, flags=re.IGNORECASE))
                else:
                    count = len(text.split())  # total de palavras
                    music_counts[title] = count

        st.bar_chart(pd.Series(music_counts))



