import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image
import base64
import re

st.set_page_config(page_title="ORION PDV", layout="wide")

# URLs externas
URL_CLIENTE = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0...output=csv"
URL_PGTO = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0...output=csv"
URL_VENDA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0...output=csv"
URL_GRUPO = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0...output=csv"
URL_MARCAS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0...output=csv"

# Sessão
if 'produtos_db' not in st.session_state:
    st.session_state.produtos_db = {}

if 'vendas_db' not in st.session_state:
    st.session_state.vendas_db = []

if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

if 'ultimo_codigo' not in st.session_state:
    st.session_state.ultimo_codigo = None

# Utilitários
def extrair_codigo(texto):
    numeros = re.findall(r'\d+', texto)
    return ''.join(numeros) if len(''.join(numeros)) >= 8 else None

def gerar_recibo_html(venda):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    html = f"""
    <!DOCTYPE html><html><head><meta charset="UTF-8"><title>Recibo</title>
    <style>
        body {{ font-family: monospace; max-width: 600px; margin: auto; }}
        .linha {{ border-top: 1px dashed #000; margin: 10px 0; }}
        button {{ margin-top: 20px; }}
    </style></head><body>
    <h2>🧾 ORION PDV - CUPOM ELETRÔNICO</h2>
    <div class="linha"></div>
    <p><strong>Data:</strong> {venda['data']}</p>
    <p><strong>Cliente:</strong> {venda['cliente']}</p>
    <p><strong>Pagamento:</strong> {venda['forma_pgto']}</p>
    <div class="linha"></div>
    <table width="100%">
        <thead><tr><th>Produto</th><th>Qtd</th><th>Unit</th><th>Total</th></tr></thead>
        <tbody>
    """
    for item in venda['itens']:
        html += f"<tr><td>{item['produto']}</td><td>{item['quantidade']}</td><td>R$ {item['preco_unit']:.2f}</td><td>R$ {item['total']:.2f}</td></tr>"
    html += f"""
        </tbody></table>
        <div class="linha"></div>
        <h4>Total da Venda: R$ {venda['total']:.2f}</h4>
        <div class="linha"></div>
        <p>Obrigado pela preferência!</p>
        <p><small>Gerado em: {timestamp}</small></p>
        <button onclick="window.print()">🖨️ Imprimir</button>
    </body></html>
    """
    return html
# Cadastro de produto
def render_cadastro_produto():
    st.header("📦 Cadastro de Produto")

    with st.form("form_produto"):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome do Produto")
            codigo = st.text_input("Código de Barras ou QR")
        with col2:
            preco = st.number_input("Preço", min_value=0.01, step=0.01)
            estoque = st.number_input("Estoque", min_value=0, step=1)

        grupo = st.text_input("Categoria (Grupo)")
        marca = st.text_input("Marca")
        localizacao = st.text_input("Localização (ex: Gondola 3)")
        foto_url = st.text_input("URL da Foto do Produto")

        if foto_url:
            st.image(foto_url, width=150)

        enviar = st.form_submit_button("Salvar Produto")
        if enviar and nome and codigo:
            st.session_state.produtos_db[codigo] = {
                "nome": nome,
                "codigo_barras": codigo,
                "grupo": grupo,
                "marca": marca,
                "preco": preco,
                "estoque": estoque,
                "localizacao": localizacao,
                "foto": foto_url
            }
            st.success("Produto cadastrado com sucesso!")

# Busca e exibição
def buscar_produto(termo, tipo="nome"):
    termo = termo.lower()
    resultados = []
    for p in st.session_state.produtos_db.values():
        if tipo == "nome" and termo in p["nome"].lower():
            resultados.append(p)
        elif tipo == "categoria" and termo in p["grupo"].lower():
            resultados.append(p)
        elif tipo == "localizacao" and termo in p["localizacao"].lower():
            resultados.append(p)
    return resultados

def exibir_resultados_busca(produtos):
    st.subheader("Resultados da Busca")
    if not produtos:
        st.info("Nenhum produto encontrado.")
        return
    cols = st.columns(3)
    for i, p in enumerate(produtos):
        with cols[i % 3]:
            st.markdown(f"### {p['nome']}")
            if p["foto"]:
                st.image(p["foto"], width=100)
            st.write(f"Preço: R$ {p['preco']:.2f}")
            st.write(f"Estoque: {p['estoque']} | Local: {p['localizacao']}")
            if st.button("Adicionar ao Carrinho", key=f"add_{p['codigo_barras']}"):
                st.session_state.ultimo_codigo = p["codigo_barras"]
                st.rerun()

# Registro de venda
def render_registro_venda():
    st.header("🧾 Registrar Venda")

    codigo = st.text_input("Código do Produto", value=st.session_state.ultimo_codigo or "")
    if st.button("Buscar Produto"):
        st.session_state.ultimo_codigo = codigo

    if codigo and codigo in st.session_state.produtos_db:
        p = st.session_state.produtos_db[codigo]
        st.success(f"Produto encontrado: {p['nome']}")
        st.image(p["foto"], width=100)
        qtd = st.number_input("Quantidade", min_value=1, step=1)
        if st.button("Adicionar ao Carrinho"):
            st.session_state.carrinho.append({
                "codigo_barras": p["codigo_barras"],
                "produto": p["nome"],
                "quantidade": qtd,
                "preco_unit": p["preco"],
                "total": qtd * p["preco"],
                "foto": p["foto"]
            })
            st.success("Produto adicionado ao carrinho!")
            st.session_state.ultimo_codigo = None
            st.rerun()

    st.subheader("🛒 Carrinho")
    total = 0
    for i, item in enumerate(st.session_state.carrinho):
        cols = st.columns([1, 3, 1])
        with cols[0]:
            if item["foto"]:
                st.image(item["foto"], width=80)
        with cols[1]:
            st.write(f"{item['produto']} (Qtd: {item['quantidade']})")
        with cols[2]:
            st.write(f"R$ {item['total']:.2f}")
        total += item["total"]

    st.markdown(f"### Total: R$ {total:.2f}")

    if st.button("🧾 Finalizar Venda"):
        cliente = st.text_input("Nome do Cliente", "Cliente Padrão")
        forma = st.selectbox("Forma de Pagamento", ["Pix", "Cartão", "Dinheiro"])
        if st.session_state.carrinho:
            venda = {
                "cliente": cliente,
                "forma_pgto": forma,
                "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "itens": st.session_state.carrinho,
                "total": total
            }
            st.session_state.vendas_db.append(venda)
            html = gerar_recibo_html(venda)
            st.download_button("📄 Baixar Recibo HTML", html, "recibo.html", "text/html")
            st.components.v1.html(html, height=600)
            st.session_state.carrinho = []
            st.success("Venda concluída!")
# Painel Financeiro
def render_painel():
    st.header("📈 Painel de Vendas")

    # Tenta carregar o CSV externo
    try:
        venda_df = pd.read_csv(URL_VENDA)
    except:
        venda_df = pd.DataFrame(columns=["DATA", "ID_CLIENTE", "ID_FORMA_PGTO", "TOTAL"])

    # Corrigir tipo da coluna DATA
    if "DATA" in venda_df.columns:
        venda_df["DATA"] = pd.to_datetime(venda_df["DATA"], errors="coerce")
    else:
        venda_df["DATA"] = pd.to_datetime([])

    # Combina com vendas locais
    if st.session_state.vendas_db:
        locais_df = pd.DataFrame([{
            "DATA": pd.to_datetime(v["data"]),
            "ID_CLIENTE": v["cliente"],
            "ID_FORMA_PGTO": v["forma_pgto"],
            "TOTAL": v["total"]
        } for v in st.session_state.vendas_db])
        venda_df = pd.concat([venda_df, locais_df], ignore_index=True)

    # Filtros
    col1, col2 = st.columns(2)
    with col1:
        data_inicio = st.date_input("Data Inicial", value=datetime.today().replace(day=1))
    with col2:
        data_fim = st.date_input("Data Final", value=datetime.today())

    formas = ["Todas"]
    if "ID_FORMA_PGTO" in venda_df.columns:
        formas += list(venda_df["ID_FORMA_PGTO"].dropna().unique())

    forma_pgto = st.selectbox("Forma de Pagamento", formas)

    filtro = (venda_df["DATA"].dt.date >= data_inicio) & (venda_df["DATA"].dt.date <= data_fim)
    if forma_pgto != "Todas":
        filtro &= venda_df["ID_FORMA_PGTO"] == forma_pgto

    df = venda_df[filtro]
    st.metric("💰 Total no Período", f"R$ {df['TOTAL'].sum():,.2f}")

    if not df.empty and "ID_FORMA_PGTO" in df.columns:
        st.bar_chart(df.groupby("ID_FORMA_PGTO")["TOTAL"].sum())

    if not df.empty:
        st.line_chart(df.groupby(df["DATA"].dt.date)["TOTAL"].sum())

# Página principal
def main():
    st.sidebar.image("https://i.imgur.com/Ka8kNST.png", width=200)
    st.sidebar.title("🧭 Navegação")
    menu = st.sidebar.radio("Escolha uma opção:", [
        "Registrar Venda",
        "Cadastro de Produto",
        "Painel Financeiro"
    ])

    if menu == "Registrar Venda":
        render_registro_venda()
    elif menu == "Cadastro de Produto":
        render_cadastro_produto()
    elif menu == "Painel Financeiro":
        render_painel()

# Execução principal
if __name__ == "__main__":
    main()

# Sessão
for key in ['produtos_db', 'vendas_db', 'carrinho', 'ultimo_codigo']:
    if key not in st.session_state:
        st.session_state[key] = [] if 'db' in key or key == 'carrinho' else None

# Funções utilitárias
def extrair_codigo(texto):
    numeros = re.findall(r'\d+', texto)
    return ''.join(numeros) if len(''.join(numeros)) >= 8 else None

def gerar_recibo_html(venda):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    html = f"""
    <!DOCTYPE html><html><head><meta charset="UTF-8"><title>Recibo</title>
    <style>
        body {{ font-family: monospace; max-width: 600px; margin: auto; }}
        .linha {{ border-top: 1px dashed #000; margin: 10px 0; }}
        button {{ margin-top: 20px; }}
    </style></head><body>
    <h2>🧾 ORION PDV - CUPOM ELETRÔNICO</h2>
    <div class="linha"></div>
    <p><strong>Data:</strong> {venda['data']}</p>
    <p><strong>Cliente:</strong> {venda['cliente']}</p>
    <p><strong>Pagamento:</strong> {venda['forma_pgto']}</p>
    <div class="linha"></div>
    <table width="100%">
        <thead><tr><th>Produto</th><th>Qtd</th><th>Unit</th><th>Total</th></tr></thead>
        <tbody>
    """
    for item in venda['itens']:
        html += f"<tr><td>{item['produto']}</td><td>{item['quantidade']}</td><td>R$ {item['preco_unit']:.2f}</td><td>R$ {item['total']:.2f}</td></tr>"
    html += f"""
        </tbody></table>
        <div class="linha"></div>
        <h4>Total da Venda: R$ {venda['total']:.2f}</h4>
        <div class="linha"></div>
        <p>Obrigado pela preferência!</p>
        <p><small>Gerado em: {timestamp}</small></p>
        <button onclick="window.print()">🖨️ Imprimir</button>
    </body></html>
    """
    return html

def render_cadastro_produto():
    st.header("📦 Cadastro de Produto")
    with st.form("form_produto"):
        col1, col2 = st.columns(2)
        nome = col1.text_input("Nome do Produto")
        codigo = col2.text_input("Código de Barras ou QR")
        preco = col1.number_input("Preço", min_value=0.01, step=0.01)
        estoque = col2.number_input("Estoque", min_value=0, step=1)
        grupo = st.text_input("Categoria (Grupo)")
        marca = st.text_input("Marca")
        localizacao = st.text_input("Localização (ex: Gondola 3)")
        foto_url = st.text_input("URL da Foto")
        if foto_url:
            st.image(foto_url, width=100)
        if st.form_submit_button("Salvar Produto") and nome and codigo:
            st.session_state.produtos_db[codigo] = {
                "nome": nome, "codigo_barras": codigo, "grupo": grupo,
                "marca": marca, "preco": preco, "estoque": estoque,
                "localizacao": localizacao, "foto": foto_url
            }
            st.success("Produto cadastrado com sucesso!")

def buscar_produto(termo, tipo="nome"):
    termo = termo.lower()
    return [p for p in st.session_state.produtos_db.values()
            if termo in p.get(tipo, "").lower()]

def exibir_resultados_busca(produtos):
    if not produtos:
        st.info("Nenhum produto encontrado.")
        return
    cols = st.columns(3)
    for i, p in enumerate(produtos):
        with cols[i % 3]:
            st.markdown(f"### {p['nome']}")
            if p["foto"]:
                st.image(p["foto"], width=100)
            st.write(f"Preço: R$ {p['preco']:.2f} | Estoque: {p['estoque']}")
            st.write(f"Local: {p['localizacao']}")
            if st.button("Adicionar ao Carrinho", key=f"add_{p['codigo_barras']}"):
                st.session_state.ultimo_codigo = p["codigo_barras"]
                st.rerun()
def render_registro_venda():
    st.header("🧾 Registrar Venda")
    codigo = st.text_input("Código do Produto", value=st.session_state.ultimo_codigo or "")
    if st.button("Buscar Produto"):
        st.session_state.ultimo_codigo = codigo

    if codigo and codigo in st.session_state.produtos_db:
        p = st.session_state.produtos_db[codigo]
        st.success(f"Produto encontrado: {p['nome']}")
        st.image(p["foto"], width=100)
        qtd = st.number_input("Quantidade", min_value=1, step=1)
        if st.button("Adicionar ao Carrinho"):
            st.session_state.carrinho.append({
                "codigo_barras": p["codigo_barras"],
                "produto": p["nome"],
                "quantidade": qtd,
                "preco_unit": p["preco"],
                "total": qtd * p["preco"],
                "foto": p["foto"]
            })
            st.success("Produto adicionado ao carrinho!")
            st.session_state.ultimo_codigo = None
            st.rerun()

    st.subheader("🛒 Carrinho")
    total = 0
    for i, item in enumerate(st.session_state.carrinho):
        cols = st.columns([1, 3, 1])
        with cols[0]:
            if item["foto"]:
                st.image(item["foto"], width=80)
        with cols[1]:
            st.write(f"{item['produto']} (Qtd: {item['quantidade']})")
        with cols[2]:
            st.write(f"R$ {item['total']:.2f}")
        total += item["total"]

    st.markdown(f"### Total: R$ {total:.2f}")

    if st.button("🧾 Finalizar Venda"):
        cliente = st.text_input("Nome do Cliente", "Cliente Padrão")
        forma = st.selectbox("Forma de Pagamento", ["Pix", "Cartão", "Dinheiro"])
        if st.session_state.carrinho:
            venda = {
                "cliente": cliente,
                "forma_pgto": forma,
                "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "itens": st.session_state.carrinho,
                "total": total
            }
            st.session_state.vendas_db.append(venda)
            html = gerar_recibo_html(venda)
            st.download_button("📄 Baixar Recibo HTML", html, "recibo.html", "text/html")
            st.components.v1.html(html, height=600)
            st.session_state.carrinho = []
            st.success("Venda concluída!")
def render_painel():
    st.header("📈 Painel de Vendas")
    
    try:
        venda_df = pd.read_csv(URL_VENDA)
    except:
        venda_df = pd.DataFrame(columns=["DATA", "ID_CLIENTE", "ID_FORMA_PGTO", "TOTAL"])

    # Garantir que a coluna DATA esteja presente e em formato datetime
    if "DATA" in venda_df.columns:
        venda_df["DATA"] = pd.to_datetime(venda_df["DATA"], errors="coerce")
    else:
        venda_df["DATA"] = pd.to_datetime([])

    # Combinar com vendas locais
    if st.session_state.vendas_db:
        locais_df = pd.DataFrame([{
            "DATA": pd.to_datetime(v["data"]),
            "ID_CLIENTE": v["cliente"],
            "ID_FORMA_PGTO": v["forma_pgto"],
            "TOTAL": v["total"]
        } for v in st.session_state.vendas_db])
        venda_df = pd.concat([venda_df, locais_df], ignore_index=True)

    # Filtros por data e forma de pagamento
    col1, col2 = st.columns(2)
    with col1:
        data_inicio = st.date_input("Data Inicial", value=datetime.today().replace(day=1))
    with col2:
        data_fim = st.date_input("Data Final", value=datetime.today())

    if "ID_FORMA_PGTO" in venda_df:
        formas = ["Todas"] + list(venda_df["ID_FORMA_PGTO"].dropna().unique())
    else:
        formas = ["Todas"]

    forma_pgto = st.selectbox("Forma de Pagamento", formas)

    # Aplicação dos filtros
    filtro = (venda_df["DATA"].dt.date >= data_inicio) & (venda_df["DATA"].dt.date <= data_fim)
    if forma_pgto != "Todas":
        filtro &= venda_df["ID_FORMA_PGTO"] == forma_pgto

    df = venda_df[filtro]

    st.metric("💰 Total no Período", f"R$ {df['TOTAL'].sum():,.2f}")

    if not df.empty and "ID_FORMA_PGTO" in df:
        st.bar_chart(df.groupby("ID_FORMA_PGTO")["TOTAL"].sum())
    if not df.empty:
        st.line_chart(df.groupby(df["DATA"].dt.date)["TOTAL"].sum())
if __name__ == "__main__":
    main()
