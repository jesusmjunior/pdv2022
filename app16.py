import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import hashlib
import uuid
import re
from PIL import Image

# ----------------------------- CONFIGURAÇÃO BÁSICA ----------------------------- #
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
    st.session_state.autenticado = False

# ----------------------------- FUNÇÕES AUXILIARES ----------------------------- #
def extrair_codigo_barras(texto):
    numeros = re.findall(r'\d+', texto)
    codigo_extraido = ''.join(numeros)
    return codigo_extraido if len(codigo_extraido) >= 8 else None

def reconhecer_texto_imagem():
    st.markdown("""...""")  # Mantido o mesmo conteúdo
    # ... (implementação original mantida)
    return st.session_state.ultimo_codigo

# ----------------------------- MÓDULOS PRINCIPAIS ----------------------------- #
def leitor_codigo_barras():
    # ... (implementação original mantida)
    return codigo_selecionado

def importar_produtos_csv():
    # ... (implementação original mantida)
    # Corrigido o sep do pandas.read_csv
    df = pd.read_csv(arquivo, sep=',', engine='python')

def cadastro_produto():
    # ... (implementação original mantida)

def cadastro_cliente():
    # ... (implementação original mantida)

def painel_financeiro():
    # ... (implementação original mantida - removida a duplicata)

# ----------------------------- AUTENTICAÇÃO ----------------------------- #
USUARIOS = {
    "admjesus": {
        "nome": "ADM Jesus",
        "senha_hash": hashlib.sha256("senha123".encode()).hexdigest()
    }
}

def autenticar_usuario():
    # ... (implementação original mantida)

# ----------------------------- NAVEGAÇÃO ----------------------------- #
def sidebar():
    # ... (implementação original mantida)

def main():
    if not st.session_state.get("autenticado"):
        autenticar_usuario()
        return

    pagina = sidebar()
    
    # Mapeamento simplificado das páginas
    paginas = {
        "📥 Importar Produtos via CSV": importar_produtos_csv,
        "📦 Cadastrar Produto": cadastro_produto,
        "👤 Cadastrar Cliente": cadastro_cliente,
        "📊 Painel Financeiro": painel_financeiro
    }
    
    if pagina in paginas:
        paginas[pagina]()
    else:
        st.warning("Funcionalidade em desenvolvimento")

# Lousa 11 – Sidebar, Navegação e Função Principal do App
import streamlit as st
from datetime import datetime
import pandas as pd
import uuid

# ----------------------------- REGISTRAR VENDA ----------------------------- #
def registrar_venda():
    st.header("🧾 Registrar Venda")

    if not st.session_state.produtos_db:
        st.warning("Nenhum produto cadastrado. Cadastre produtos primeiro.")
        return

    st.subheader("Buscar Produto")
    termo = st.text_input("Digite nome ou código de barras")
    resultados = []
    for p in st.session_state.produtos_db.values():
        if termo.lower() in p["nome"].lower() or termo in p["codigo_barras"]:
            resultados.append(p)

    for produto in resultados:
        col1, col2 = st.columns([1, 3])
        with col1:
            st.image(produto['foto'], width=100)
        with col2:
            st.write(f"**{produto['nome']}**")
            st.write(f"Preço: R$ {produto['preco']:.2f} | Estoque: {produto['estoque']} unidades")
            qtd = st.number_input("Quantidade", min_value=1, max_value=produto['estoque'], key=produto['codigo_barras'])
            if st.button("Adicionar", key=f"add_{produto['codigo_barras']}"):
                item = {
                    "codigo_barras": produto['codigo_barras'],
                    "produto": produto['nome'],
                    "quantidade": qtd,
                    "preco_unit": produto['preco'],
                    "total": qtd * produto['preco'],
                    "foto": produto['foto']
                }
                st.session_state.carrinho.append(item)
                st.session_state.produtos_db[produto['codigo_barras']]['estoque'] -= qtd
                st.success(f"{qtd}x {produto['nome']} adicionados")

    st.subheader("🛒 Carrinho")
    total = 0
    for i, item in enumerate(st.session_state.carrinho):
        cols = st.columns([2, 4, 2, 2])
        cols[0].image(item["foto"], width=50)
        cols[1].write(f"{item['produto']} ({item['quantidade']}x)")
        cols[2].write(f"R$ {item['total']:.2f}")
        if cols[3].button("❌", key=f"rm_{i}"):
            st.session_state.produtos_db[item['codigo_barras']]['estoque'] += item['quantidade']
            st.session_state.carrinho.pop(i)
            st.rerun()
        total += item['total']

    if st.session_state.carrinho:
        st.markdown(f"### Total: R$ {total:.2f}")
        with st.form("finalizar"):
            cliente = st.text_input("Cliente", value="Consumidor Final")
            forma_pgto = st.selectbox("Forma de Pagamento", ["Dinheiro", "Cartão", "Pix"])
            if st.form_submit_button("Finalizar Venda"):
                venda = {
                    "id": str(uuid.uuid4())[:8],
                    "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "cliente": cliente,
                    "forma_pgto": forma_pgto,
                    "itens": st.session_state.carrinho.copy(),
                    "total": total
                }
                st.session_state.vendas_db.append(venda)
                st.session_state.carrinho = []
                st.success("Venda registrada com sucesso!")

# ----------------------------- SIDEBAR ----------------------------- #
def sidebar():
    with st.sidebar:
        st.image("https://i.imgur.com/Ka8kNST.png", width=200)
        st.title("ORION PDV")

        pagina = st.selectbox(
            "Menu Principal",
            [
                "🧾 Registrar Venda",
                "📦 Cadastrar Produto",
                "👤 Cadastrar Cliente",
                "📊 Painel Financeiro",
                "📜 Histórico de Vendas",
                "🗃️ Gerenciar Estoque",
                "📥 Importar Produtos via CSV",
                "⚙️ Configurações",
                "ℹ️ Sobre"
            ]
        )

        st.divider()
        st.write(f"📅 {datetime.now().strftime('%d/%m/%Y')}")
        st.write(f"🕒 {datetime.now().strftime('%H:%M:%S')}")

        if "usuario" in st.session_state:
            st.write(f"👤 Usuário: {st.session_state['usuario']}")
            if st.button("Sair", type="primary"):
                st.session_state.clear()
                st.rerun()

    return pagina

# ----------------------------- MAIN ----------------------------- #
def main():
    if "autenticado" not in st.session_state or not st.session_state.autenticado:
        autenticar_usuario()
        return

    pagina = sidebar()

    if pagina == "🧾 Registrar Venda":
        registrar_venda()
    elif pagina == "📦 Cadastrar Produto":
        cadastro_produto()
    elif pagina == "👤 Cadastrar Cliente":
        cadastro_cliente()
    elif pagina == "📊 Painel Financeiro":
        painel_financeiro()
    elif pagina == "📜 Histórico de Vendas":
        historico_vendas()
    elif pagina == "🗃️ Gerenciar Estoque":
        gerenciar_estoque()
    elif pagina == "📥 Importar Produtos via CSV":
        importar_produtos_csv()
    elif pagina == "⚙️ Configurações":
        configuracoes_sistema()
    elif pagina == "ℹ️ Sobre":
        sobre()

# ----------------------------- EXECUÇÃO ----------------------------- #
if __name__ == "__main__":
    main()

