import streamlit as st
import pandas as pd
import requests
import base64
import json
import re
from datetime import datetime
import uuid
import hashlib
from PIL import Image
import io

# Configuração da página
st.set_page_config(page_title="ORION PDV I.A. 🔐 OCR via Google Vision", layout="wide")

# Inicialização da sessão
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
if 'usuario' not in st.session_state:
    st.session_state.usuario = None
if 'produtos_db' not in st.session_state:
    st.session_state.produtos_db = {}
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []
if 'vendas_db' not in st.session_state:
    st.session_state.vendas_db = []
if 'ultimo_codigo' not in st.session_state:
    st.session_state.ultimo_codigo = None
if 'clientes_db' not in st.session_state:
    st.session_state.clientes_db = []

# Carregamento da chave do Google Vision
try:
    with open("zeta-bonbon-424022-b5-691a49c9946f.json") as f:
        google_vision_credentials = json.load(f)
except FileNotFoundError:
    st.error("Arquivo de credenciais do Google Vision não encontrado. Algumas funcionalidades estarão indisponíveis.")
    google_vision_credentials = {"private_key_id": ""}

# URLs das planilhas externas
URLS = {
    "grupo": "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0r3XE4DpzlYJjZwjc2c_pW_K3euooN9caPedtSq-nH_aEPnvx1jrcd9t0Yhg8fqXfR3j5jM2OyUQQ/pub?gid=528868130&single=true&output=csv",
    "marcas": "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0r3XE4DpzlYJjZwjc2c_pW_K3euooN9caPedtSq-nH_aEPnvx1jrcd9t0Yhg8fqXfR3j5jM2OyUQQ/pub?gid=832596780&single=true&output=csv",
    "cliente": "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0r3XE4DpzlYJjZwjc2c_pW_K3euooN9caPedtSq-nH_aEPnvx1jrcd9t0Yhg8fqXfR3j5jM2OyUQQ/pub?gid=1645177762&single=true&output=csv",
    "produto": "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0r3XE4DpzlYJjZwjc2c_pW_K3euooN9caPedtSq-nH_aEPnvx1jrcd9t0Yhg8fqXfR3j5jM2OyUQQ/pub?gid=1506891785&single=true&output=csv",
    "pgto": "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0r3XE4DpzlYJjZwjc2c_pW_K3euooN9caPedtSq-nH_aEPnvx1jrcd9t0Yhg8fqXfR3j5jM2OyUQQ/pub?gid=1061064660&single=true&output=csv",
    "venda": "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0r3XE4DpzlYJjZwjc2c_pW_K3euooN9caPedtSq-nH_aEPnvx1jrcd9t0Yhg8fqXfR3j5jM2OyUQQ/pub?gid=1817416820&single=true&output=csv"
}

# IMPORTAÇÃO DIRETA DAS FUNÇÕES EM VEZ DE MÓDULOS EXTERNOS
from types import SimpleNamespace

def modulo_upload_documento():
    st.header("📄 Upload de Documento - Nota Fiscal ou Cupom")
    st.markdown("""
    <div style="background-color:#f9f9f9; padding:15px; border-left:4px solid #2196f3; margin-bottom:20px;">
        <b>Instruções:</b><br>
        1. Faça upload de uma imagem (JPG/PNG)<br>
        2. O sistema usará <i>Google Vision</i> para extrair o texto<br>
        3. Verifique e edite os dados extraídos conforme necessário
    </div>
    """, unsafe_allow_html=True)

    imagem_upload = st.file_uploader("📌 Enviar Imagem da Nota/Cupom", type=["jpg", "jpeg", "png"])

    if imagem_upload:
        try:
            img_preview = Image.open(imagem_upload)
            st.image(img_preview, caption="📷 Pré-visualização da Imagem", use_column_width=True)

            with st.spinner("🔍 Extraindo texto via Google Vision..."):
                texto_extraido = extrair_texto_google_vision(img_preview)

            if texto_extraido:
                st.success("✅ Texto extraído com sucesso!")
                with st.expander("📜 Texto OCR Extraído"):
                    st.text_area("Conteúdo Detectado:", value=texto_extraido, height=250)

                tipo_documento = st.selectbox("Tipo de Documento", ["Imagem de Nota", "Cupom"])

                if st.button("Analisar Produtos"):
                    st.info("Chamaria interface_importar_produtos(texto_extraido, tipo_documento)")
            else:
                st.warning("⚠️ Nenhum texto detectado na imagem.")
        except Exception as e:
            st.error(f"Erro ao processar imagem: {str(e)}")

def extrair_texto_google_vision(imagem_pil):
    buffered = io.BytesIO()
    imagem_pil.save(buffered, format="JPEG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode()

    payload = {
        "requests": [{
            "image": {"content": img_base64},
            "features": [{"type": "TEXT_DETECTION"}]
        }]
    }

    try:
        response = requests.post(
            url="https://vision.googleapis.com/v1/images:annotate",
            params={"key": google_vision_credentials["private_key_id"]},
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload)
        )

        data = response.json()
        if 'responses' in data and data['responses'] and 'textAnnotations' in data['responses'][0]:
            texto = data['responses'][0]['textAnnotations'][0]['description']
            return texto
        else:
            st.error("Não foi possível detectar texto na imagem.")
            return ""
    except Exception as e:
        st.error(f"Erro ao processar OCR com Google Vision: {str(e)}")
        return ""

def registrar_venda():
    st.warning("Função 'registrar_venda()' ainda não implementada neste script.")

def cadastro_produto():
    st.warning("Função 'cadastro_produto()' ainda não implementada neste script.")

def cadastro_cliente():
    st.warning("Função 'cadastro_cliente()' ainda não implementada neste script.")

def painel_financeiro():
    st.header("\U0001F4CA Painel Financeiro")

    vendas_combinadas = []
    try:
        df_ext = pd.read_csv(URLS["venda"])
        df_ext["DATA"] = pd.to_datetime(df_ext["DATA"], errors="coerce")
        vendas_combinadas.extend(df_ext.to_dict(orient="records"))
        st.success(f"\u2705 {len(df_ext)} vendas externas carregadas")
    except Exception as e:
        st.warning(f"\u26a0\ufe0f Dados externos n\u00e3o acess\u00edveis: {str(e)}")

    vendas_combinadas.extend(st.session_state.vendas_db)

    if not vendas_combinadas:
        st.info("\U0001F4AC Nenhuma venda registrada ainda.")
        return

    vendas_df = pd.DataFrame([
        {
            "ID": v.get("id", ""),
            "DATA": pd.to_datetime(v.get("data", ""), errors="coerce"),
            "CLIENTE": v.get("cliente", ""),
            "PGTO": v.get("forma_pgto", ""),
            "TOTAL": v.get("total", 0)
        } for v in vendas_combinadas
    ])

    vendas_df.dropna(subset=["DATA"], inplace=True)

    total_vendas = len(vendas_df)
    soma_total = vendas_df["TOTAL"].sum()
    ticket_medio = vendas_df["TOTAL"].mean()

    col1, col2, col3 = st.columns(3)
    col1.metric("\U0001F9FE Total de Vendas", f"{total_vendas}")
    col2.metric("\U0001F4B0 Faturamento", f"R$ {soma_total:.2f}")
    col3.metric("\U0001F4C8 Ticket M\u00e9dio", f"R$ {ticket_medio:.2f}")

    with st.expander("\U0001F4C5 Vendas Registradas"):
        st.dataframe(vendas_df.sort_values("DATA", ascending=False).reset_index(drop=True))

# Menu Principal
menu = st.sidebar.radio("🔺 Menu", [
    "Upload de Documento",
    "Registrar Venda",
    "Cadastro de Produto",
    "Cadastro de Cliente",
    "Painel Financeiro"
])

if menu == "Upload de Documento":
    modulo_upload_documento()
elif menu == "Registrar Venda":
    registrar_venda()
elif menu == "Cadastro de Produto":
    cadastro_produto()
elif menu == "Cadastro de Cliente":
    cadastro_cliente()
elif menu == "Painel Financeiro":
    painel_financeiro()
