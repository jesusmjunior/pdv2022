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
    st.header("🧾 Nova Venda")

    abas = st.tabs(["🔍 Buscar Produto", "📷 Scanner"])

    with abas[0]:
        termo = st.text_input("Digite o nome ou código do produto")
        resultados = []
        if termo:
            for cod, prod in st.session_state.produtos_db.items():
                if termo.lower() in prod["nome"].lower() or termo in prod["codigo_barras"]:
                    resultados.append(prod)

        if resultados:
            for prod in resultados:
                with st.container():
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        st.image(prod["foto"], width=100)
                    with col2:
                        st.write(f"**{prod['nome']}** - R$ {prod['preco']:.2f}")
                        qtd = st.number_input(
                            f"Qtd ({prod['codigo_barras']})", 
                            min_value=1, 
                            max_value=prod["estoque"], 
                            step=1, 
                            key=f"qtd_{prod['codigo_barras']}"
                        )
                        if st.button(f"Adicionar {prod['nome']}", key=f"add_{prod['codigo_barras']}"):
                            adicionar_ao_carrinho(prod['codigo_barras'], qtd)

    with abas[1]:
        st.info("🔧 Scanner não implementado ainda nesta versão.")

    st.subheader("🛒 Carrinho")
    if not st.session_state.carrinho:
        st.info("Carrinho vazio")
    else:
        total = 0
        for i, item in enumerate(st.session_state.carrinho):
            st.write(f"{item['quantidade']}x {item['produto']} - R$ {item['total']:.2f}")
            total += item["total"]
            if st.button("❌ Remover", key=f"del_{i}"):
                remover_do_carrinho(i)

        st.metric("Total", f"R$ {total:.2f}")
        cliente = st.text_input("Cliente", value="Consumidor Final")
        pgto = st.selectbox("Forma de Pagamento", ["Dinheiro", "Pix", "Cartão", "Crediário"])
        if st.button("💳 Finalizar Venda"):
            venda_id = str(uuid.uuid4())[:6]
            registrar_venda_db(cliente, pgto, total)
            st.success(f"Venda {venda_id} concluída com sucesso!")

def adicionar_ao_carrinho(codigo_barras, qtd):
    produto = st.session_state.produtos_db[codigo_barras]
    if produto["estoque"] >= qtd:
        total = round(produto["preco"] * qtd, 2)
        st.session_state.carrinho.append({
            "codigo_barras": codigo_barras,
            "produto": produto["nome"],
            "quantidade": qtd,
            "preco_unit": produto["preco"],
            "total": total
        })
        st.session_state.produtos_db[codigo_barras]["estoque"] -= qtd
        st.success(f"{qtd}x {produto['nome']} adicionado(s) ao carrinho.")
    else:
        st.error("Estoque insuficiente.")

def remover_do_carrinho(index):
    item = st.session_state.carrinho[index]
    st.session_state.produtos_db[item["codigo_barras"]]["estoque"] += item["quantidade"]
    st.session_state.carrinho.pop(index)
    st.rerun()

def registrar_venda_db(cliente, forma_pgto, total):
    venda_id = str(uuid.uuid4())[:8].upper()
    nova_venda = {
        "id": venda_id,
        "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "cliente": cliente,
        "forma_pgto": forma_pgto,
        "itens": st.session_state.carrinho.copy(),
        "total": total
    }
    st.session_state.vendas_db.append(nova_venda)
    recibo = gerar_recibo_html(nova_venda)
    st.download_button("📄 Baixar Recibo", recibo, file_name=f"recibo_{venda_id}.html", mime="text/html")
    st.session_state.carrinho = []

def gerar_recibo_html(venda):
    html = f"""
    <!DOCTYPE html><html><head><meta charset=\"UTF-8\"><title>Recibo</title>
    <style>
        body {{ font-family: Arial; max-width:600px; margin:auto; padding:20px; }}
        .header {{ text-align:center; margin-bottom:20px; }}
        .linha {{ border-top:1px dashed #000; margin:10px 0; }}
        .total {{ font-weight:bold; font-size:1.2em; }}
        table {{ width:100%; border-collapse:collapse; margin:15px 0; }}
        th, td {{ padding:8px; text-align:left; border-bottom:1px solid #ddd; }}
        th {{ background-color:#f2f2f2; }}
        .footer {{ text-align:center; margin-top:30px; font-size:0.9em; color:#555; }}
    </style></head><body>
    <div class=\"header\">
        <h2>ORION PDV</h2><h3>RECIBO ELETRÔNICO</h3>
    </div>
    <div class=\"linha\"></div>
    <p><strong>Data:</strong> {venda['data']}</p>
    <p><strong>Cliente:</strong> {venda['cliente']}</p>
    <p><strong>Pagamento:</strong> {venda['forma_pgto']}</p>
    <div class=\"linha\"></div>
    <table><thead><tr><th>Produto</th><th>Qtd</th><th>Unit</th><th>Total</th></tr></thead><tbody>
    """
    for item in venda["itens"]:
        html += f"""
        <tr><td>{item['produto']}</td><td>{item['quantidade']}</td>
        <td>R$ {item['preco_unit']:.2f}</td><td>R$ {item['total']:.2f}</td></tr>"""
    html += f"""
    </tbody></table>
    <div class=\"linha\"></div>
    <p class=\"total\">Total: R$ {venda['total']:.2f}</p>
    <div class=\"linha\"></div>
    <div class=\"footer\">
        <p>Obrigado pela preferência!</p>
        <p><small>Gerado em: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}</small></p>
    </div>
    </body></html>
    """
    return html

def cadastro_produto():
    st.header("📦 Cadastro de Produto")

    try:
        grupo_df = pd.read_csv(URLS["grupo"])
        grupos = list(grupo_df["DESCRICAO"].dropna())
    except:
        grupos = ["Alimentos", "Higiene", "Limpeza", "Diversos"]

    try:
        marca_df = pd.read_csv(URLS["marcas"])
        marcas = list(marca_df["DESCRICAO"].dropna())
    except:
        marcas = ["Outras", "Genérica", "Não Informada"]

    usar_scanner = st.checkbox("📷 Usar scanner para obter o código")
    if usar_scanner:
        st.info("⚙️ Scanner ainda não implementado nesta versão.")
        cod_lido = ""
    else:
        cod_lido = ""

    with st.form("form_produto"):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome do Produto")
            codigo = st.text_input("Código de Barras", value=cod_lido or st.session_state.get("ultimo_codigo", ""))
            grupo = st.selectbox("Grupo", grupos)
        with col2:
            preco = st.number_input("Preço de Venda", min_value=0.01, step=0.01)
            estoque = st.number_input("Estoque Inicial", min_value=0)
            marca = st.selectbox("Marca", marcas)

        foto_url = st.text_input("URL da Imagem do Produto")

        if st.form_submit_button("Salvar Produto"):
            if nome and codigo:
                st.session_state.produtos_db[codigo] = {
                    "nome": nome,
                    "codigo_barras": codigo,
                    "grupo": grupo,
                    "marca": marca,
                    "preco": preco,
                    "estoque": estoque,
                    "foto": foto_url or "https://via.placeholder.com/150"
                }
                st.success("Produto cadastrado com sucesso!")
                st.session_state.ultimo_codigo = None
            else:
                st.error("⚠️ Nome e código de barras são obrigatórios.")

    st.subheader("📋 Produtos no Sistema")
    if st.session_state.produtos_db:
        produtos_df = pd.DataFrame(st.session_state.produtos_db.values())
        st.dataframe(produtos_df[["nome", "codigo_barras", "preco", "estoque"]])
    else:
        st.info("Nenhum produto cadastrado ainda.")

def cadastro_cliente():
    st.warning("Função 'cadastro_cliente()' ainda não implementada neste script.")

def painel_financeiro():
    st.header("📊 Painel Financeiro")

    vendas_combinadas = []
    try:
        df_ext = pd.read_csv(URLS["venda"])
        df_ext["DATA"] = pd.to_datetime(df_ext["DATA"], errors="coerce")
        vendas_combinadas.extend(df_ext.to_dict(orient="records"))
        st.success(f"✅ {len(df_ext)} vendas externas carregadas")
    except Exception as e:
        st.warning(f"⚠️ Dados externos não acessíveis: {str(e)}")

    vendas_combinadas.extend(st.session_state.vendas_db)

    if not vendas_combinadas:
        st.info("💬 Nenhuma venda registrada ainda.")
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
    col1.metric("🧾 Total de Vendas", f"{total_vendas}")
    col2.metric("💰 Faturamento", f"R$ {soma_total:.2f}")
    col3.metric("📈 Ticket Médio", f"R$ {ticket_medio:.2f}")

    with st.expander("📅 Vendas Registradas"):
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
