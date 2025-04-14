import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import hashlib
import uuid
import re
from PIL import Image

# ----------------------------- CONFIGURACAO BASICA ----------------------------- #
st.set_page_config(page_title="ORION PDV - Importador", layout="wide")

API_KEY = "AIzaSyAKibc0A3TerDdfQeZBLePxU01PbK_53Lw"
URLS = {
    "grupo": "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0r3XE4DpzlYJjZwjc2c_pW_K3euooN9caPedtSq-nH_aEPnvx1jrcd9t0Yhg8fqXfR3j5jM2OyUQQ/pub?gid=528868130&single=true&output=csv",
    "marcas": "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0r3XE4DpzlYJjZwjc2c_pW_K3euooN9caPedtSq-nH_aEPnvx1jrcd9t0Yhg8fqXfR3j5jM2OyUQQ/pub?gid=832596780&single=true&output=csv",
    "cliente": "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0r3XE4DpzlYJjZwjc2c_pW_K3euooN9caPedtSq-nH_aEPnvx1jrcd9t0Yhg8fqXfR3j5jM2OyUQQ/pub?gid=1645177762&single=true&output=csv",
    "produto": "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0r3XE4DpzlYJjZwjc2c_pW_K3euooN9caPedtSq-nH_aEPnvx1jrcd9t0Yhg8fqXfR3j5jM2OyUQQ/pub?gid=1506891785&single=true&output=csv",
    "pgto": "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0r3XE4DpzlYJjZwjc2c_pW_K3euooN9caPedtSq-nH_aEPnvx1jrcd9t0Yhg8fqXfR3j5jM2OyUQQ/pub?gid=1061064660&single=true&output=csv",
    "venda": "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0r3XE4DpzlYJjZwjc2c_pW_K3euooN9caPedtSq-nH_aEPnvx1jrcd9t0Yhg8fqXfR3j5jM2OyUQQ/pub?gid=1817416820&single=true&output=csv"
}
SPREADSHEET_ID = URLS["produto"].split("/d/e/")[1].split("/")[0]

# ----------------------------- ESTADO INICIAL ----------------------------- #
if 'produtos_db' not in st.session_state:
    st.session_state.produtos_db = {}

if 'vendas_db' not in st.session_state:
    st.session_state.vendas_db = []

if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

if 'clientes_db' not in st.session_state:
    st.session_state.clientes_db = []

if 'ultimo_codigo' not in st.session_state:
    st.session_state.ultimo_codigo = None

if 'autenticado' not in st.session_state:
    st.session_state.autenticado = True

# ----------------------------- FUNCAO DE IMPORTACAO ----------------------------- #
def importar_produtos_csv():
    st.title("📥 Importar Produtos via Planilha")

    st.markdown("""
    1. Baixe o [modelo CSV](https://raw.githubusercontent.com/jesusmjunior/pdv2022/main/modelo_importacao.csv)
    2. Preencha com até 100 produtos
    3. Envie abaixo e confirme a importação

    **Colunas obrigatórias:**
    - nome
    - codigo_barras
    - grupo
    - marca
    - preco
    - estoque
    - foto (opcional)
    """)

    arquivo = st.file_uploader("📎 Enviar Arquivo CSV", type=["csv", "txt"])

    if arquivo:
        try:
            df = pd.read_csv(arquivo, sep=None, engine='python')
            df = df.fillna("")
            obrigatorias = ["nome", "codigo_barras", "grupo", "marca", "preco", "estoque"]
            if not all(col in df.columns for col in obrigatorias):
                st.error("⚠️ O arquivo está faltando colunas obrigatórias.")
                return

            st.success("Pré-visualização dos dados:")
            st.dataframe(df.head())

            if st.button("🚀 Importar para o Sistema"):
                novos_produtos = {}
                for _, row in df.iterrows():
                    codigo = str(row["codigo_barras"]).strip()
                    novos_produtos[codigo] = {
                        "nome": str(row["nome"]),
                        "codigo_barras": codigo,
                        "grupo": str(row["grupo"]),
                        "marca": str(row["marca"]),
                        "preco": float(row["preco"]),
                        "estoque": int(row["estoque"]),
                        "foto": str(row["foto"]) if row["foto"] else "https://via.placeholder.com/150"
                    }

                st.session_state.produtos_db.update(novos_produtos)
                st.success(f"{len(novos_produtos)} produtos importados com sucesso!")

                # Atualizar Google Sheets
                url = f"https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}/values/Produtos!A1:append?valueInputOption=USER_ENTERED&key={API_KEY}"
                headers = {"Content-Type": "application/json"}

                valores = [["nome", "codigo_barras", "grupo", "marca", "preco", "estoque", "foto"]]
                for p in novos_produtos.values():
                    valores.append([p["nome"], p["codigo_barras"], p["grupo"], p["marca"], p["preco"], p["estoque"], p["foto"]])

                payload = {"values": valores}
                response = requests.post(url, headers=headers, json=payload)

                if response.status_code == 200:
                    st.success("Google Sheets atualizado com sucesso!")
                else:
                    st.warning(f"Erro ao enviar dados para Google Sheets: {response.status_code}")

        except Exception as e:
            st.error(f"Erro ao processar o arquivo: {e}")

# ----------------------------- EXECUCAO ----------------------------- #
if __name__ == "__main__":
