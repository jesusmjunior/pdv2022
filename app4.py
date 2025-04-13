# ORION PDV - SISTEMA FINAL COMPILADO
# Integração completa: autenticação, cadastro, venda, recibo e painel

import streamlit as st
import pandas as pd
import hashlib
from datetime import datetime
import base64
import io
import re

# Configuração inicial do app
st.set_page_config(page_title="ORION PDV", layout="wide", initial_sidebar_state="expanded")

# URLs de dados externos (Google Sheets publicados)
URL_GRUPO = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0r3XE4DpzlYJjZwjc2c_pW_K3euooN9caPedtSq-nH_aEPnvx1jrcd9t0Yhg8fqXfR3j5jM2OyUQQ/pub?gid=528868130&single=true&output=csv"
URL_MARCAS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0r3XE4DpzlYJjZwjc2c_pW_K3euooN9caPedtSq-nH_aEPnvx1jrcd9t0Yhg8fqXfR3j5jM2OyUQQ/pub?gid=832596780&single=true&output=csv"
URL_CLIENTE = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0r3XE4DpzlYJjZwjc2c_pW_K3euooN9caPedtSq-nH_aEPnvx1jrcd9t0Yhg8fqXfR3j5jM2OyUQQ/pub?gid=1645177762&single=true&output=csv"
URL_PGTO = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0r3XE4DpzlYJjZwjc2c_pW_K3euooN9caPedtSq-nH_aEPnvx1jrcd9t0Yhg8fqXfR3j5jM2OyUQQ/pub?gid=1061064660&single=true&output=csv"

# Inicialização do estado
if 'produtos_db' not in st.session_state:
    st.session_state.produtos_db = {}
if 'vendas_db' not in st.session_state:
    st.session_state.vendas_db = []
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

# Autenticação
USUARIOS = {
    "admjesus": {"nome": "ADM Jesus", "senha_hash": hashlib.sha256("senha123".encode()).hexdigest()}
}

def autenticar_usuario():
    st.title("🔐 Login - ORION PDV")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if usuario in USUARIOS:
            hash_inserida = hashlib.sha256(senha.encode()).hexdigest()
            if hash_inserida == USUARIOS[usuario]["senha_hash"]:
                st.session_state["autenticado"] = True
                st.rerun()
            else:
                st.error("Senha incorreta.")
        else:
            st.error("Usuário não encontrado.")

# Recibo HTML

def gerar_recibo_html(venda):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    html = f"""
    <html><body>
    <h2>ORION PDV - Recibo</h2>
    <p>Data: {venda['data']}<br>
    Cliente: {venda['cliente']}<br>
    Pagamento: {venda['forma_pgto']}</p>
    <table border='1'><tr><th>Produto</th><th>Qtd</th><th>Unitário</th><th>Total</th></tr>
    """
    for item in venda['itens']:
        html += f"<tr><td>{item['produto']}</td><td>{item['quantidade']}</td><td>R$ {item['preco_unit']:.2f}</td><td>R$ {item['total']:.2f}</td></tr>"
    html += f"</table><p><strong>Total:</strong> R$ {venda['total']:.2f}</p><p>Gerado em: {timestamp}</p></body></html>"
    return html

def download_html_as_file(html, filename):
    b64 = base64.b64encode(html.encode()).decode()
    link = f'<a href="data:text/html;base64,{b64}" download="{filename}">📄 Baixar Recibo HTML</a>'
    st.markdown(link, unsafe_allow_html=True)

# Finalização da venda

def finalizar_venda(cliente, forma_pgto, carrinho):
    total = sum(item['total'] for item in carrinho)
    venda = {
        "cliente": cliente,
        "forma_pgto": forma_pgto,
        "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total": total,
        "itens": carrinho
    }
    st.session_state.vendas_db.append(venda)
    st.success("Venda registrada com sucesso!")
    download_html_as_file(gerar_recibo_html(venda), "recibo.html")
    st.session_state.carrinho = []

# Cadastro de produto

def cadastrar_produto():
    st.title("Cadastro de Produto")
    codigo = st.text_input("Código de Barras")
    nome = st.text_input("Nome do Produto")
    grupo = st.text_input("Grupo / Categoria")
    marca = st.text_input("Marca")
    preco = st.number_input("Preço", min_value=0.01)
    estoque = st.number_input("Estoque", min_value=0)
    localizacao = st.text_input("Localização / Gôndola")
    foto = st.text_input("URL da Foto")
    if st.button("Salvar Produto"):
        st.session_state.produtos_db[codigo] = {
            "nome": nome,
            "codigo_barras": codigo,
            "grupo": grupo,
            "marca": marca,
            "preco": preco,
            "estoque": estoque,
            "localizacao": localizacao,
            "foto": foto
        }
        st.success("Produto salvo com sucesso!")

# Registro de venda

def registrar_venda():
    st.title("Registrar Venda")
    codigo = st.text_input("Código do Produto")
    qtd = st.number_input("Quantidade", min_value=1, value=1)
    if st.button("Adicionar ao Carrinho"):
        if codigo in st.session_state.produtos_db:
            produto = st.session_state.produtos_db[codigo]
            item = {
                "codigo_barras": codigo,
                "produto": produto["nome"],
                "quantidade": qtd,
                "preco_unit": produto["preco"],
                "total": qtd * produto["preco"],
                "foto": produto["foto"]
            }
            st.session_state.carrinho.append(item)
            st.success(f"{produto['nome']} adicionado ao carrinho")
    if st.session_state.carrinho:
        st.subheader("Carrinho")
        for item in st.session_state.carrinho:
            st.write(f"{item['produto']} - {item['quantidade']} x R$ {item['preco_unit']:.2f} = R$ {item['total']:.2f}")
        cliente = st.text_input("Nome do Cliente")
        forma_pgto = st.selectbox("Forma de Pagamento", ["Dinheiro", "Cartão", "PIX"])
        if st.button("Finalizar Venda"):
            finalizar_venda(cliente, forma_pgto, st.session_state.carrinho)

# Painel de análise

def render_painel():
    st.title("Painel de Vendas")
    if not st.session_state.vendas_db:
        st.warning("Nenhuma venda registrada ainda.")
        return
    df = pd.DataFrame(st.session_state.vendas_db)
    st.dataframe(df)
    st.bar_chart(df.groupby("forma_pgto")["total"].sum())

# Execução principal

def main():
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False
    if not st.session_state["autenticado"]:
        autenticar_usuario()
        return
    st.sidebar.title("Menu PDV")
    if st.sidebar.button("Sair"):
        st.session_state["autenticado"] = False
        st.rerun()
    menu = st.sidebar.radio("Escolha a opção:", ["Registrar Venda", "Cadastro Produto", "Painel"])
    if menu == "Registrar Venda":
        registrar_venda()
    elif menu == "Cadastro Produto":
        cadastrar_produto()
    elif menu == "Painel":
        render_painel()

if __name__ == '__main__':
    main()
