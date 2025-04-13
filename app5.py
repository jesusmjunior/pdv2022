import streamlit as st
import pandas as pd
from datetime import datetime
import re
import uuid
from PIL import Image

# Page configuration
st.set_page_config(page_title="ORION PDV", layout="wide")

# External URLs for data sources
URL_CLIENTE = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0...output=csv"
URL_PGTO = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0...output=csv"
URL_VENDA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0...output=csv"
URL_GRUPO = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0...output=csv"
URL_MARCAS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0...output=csv"

# Initialize session state (only once)
if 'produtos_db' not in st.session_state:
    st.session_state.produtos_db = {}

if 'vendas_db' not in st.session_state:
    st.session_state.vendas_db = []

if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

if 'ultimo_codigo' not in st.session_state:
    st.session_state.ultimo_codigo = None

# Utility functions
def extrair_codigo(texto):
    """Extract numeric code from text, returning None if less than 8 digits"""
    numeros = re.findall(r'\d+', texto)
    return ''.join(numeros) if len(''.join(numeros)) >= 8 else None

def gerar_recibo_html(venda):
    """Generate HTML receipt for a sale"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    html = f"""
    <!DOCTYPE html><html><head><meta charset="UTF-8"><title>Recibo</title>
    <style>
        body {{ font-family: monospace; max-width: 600px; margin: auto; }}
        .linha {{ border-top: 1px dashed #000; margin: 10px 0; }}
        button {{ margin-top: 20px; padding: 8px 16px; cursor: pointer; }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        th, td {{ padding: 8px; text-align: left; }}
        th {{ border-bottom: 1px solid #ddd; }}
    </style></head><body>
    <h2>🧾 ORION PDV - CUPOM ELETRÔNICO</h2>
    <div class="linha"></div>
    <p><strong>Data:</strong> {venda['data']}</p>
    <p><strong>Cliente:</strong> {venda['cliente']}</p>
    <p><strong>Pagamento:</strong> {venda['forma_pgto']}</p>
    <div class="linha"></div>
    <table>
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

def buscar_produto(termo, tipo="nome"):
    """Search for products by name, category, or location"""
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
    """Display search results in a grid"""
    st.subheader("Resultados da Busca")
    if not produtos:
        st.info("Nenhum produto encontrado.")
        return
    
    cols = st.columns(3)
    for i, p in enumerate(produtos):
        with cols[i % 3]:
            st.markdown(f"### {p['nome']}")
            if p.get("foto"):
                st.image(p["foto"], width=100)
            st.write(f"Preço: R$ {p['preco']:.2f}")
            st.write(f"Estoque: {p['estoque']} | Local: {p.get('localizacao', 'N/A')}")
            if st.button("Adicionar ao Carrinho", key=f"add_{p['codigo_barras']}"):
                st.session_state.ultimo_codigo = p["codigo_barras"]
                st.rerun()

# Module: Product Registration
def render_cadastro_produto():
    """Product registration form"""
    st.header("📦 Cadastro de Produto")

    with st.form("form_produto"):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome do Produto")
            preco = st.number_input("Preço", min_value=0.01, step=0.01)
            grupo = st.text_input("Categoria (Grupo)")
            localizacao = st.text_input("Localização (ex: Gondola 3)")
        
        with col2:
            codigo = st.text_input("Código de Barras ou QR")
            estoque = st.number_input("Estoque", min_value=0, step=1)
            marca = st.text_input("Marca")
            foto_url = st.text_input("URL da Foto do Produto")

        if foto_url:
            st.image(foto_url, width=150)

        enviar = st.form_submit_button("Salvar Produto")
        if enviar:
            if not nome:
                st.error("O nome do produto é obrigatório.")
            elif not codigo:
                st.error("O código do produto é obrigatório.")
            else:
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
    
    # List existing products
    if st.session_state.produtos_db:
        st.subheader("Produtos Cadastrados")
        produtos_df = pd.DataFrame(st.session_state.produtos_db.values())
        st.dataframe(produtos_df[["nome", "codigo_barras", "preco", "estoque", "grupo"]])
    
    # Search interface
    st.subheader("Buscar Produtos")
    col1, col2 = st.columns(2)
    termo_busca = col1.text_input("Termo de Busca")
    tipo_busca = col2.selectbox("Buscar por", ["nome", "categoria", "localizacao"])
    
    if st.button("Buscar") and termo_busca:
        resultados = buscar_produto(termo_busca, tipo_busca)
        exibir_resultados_busca(resultados)

# Module: Sales Registration
def render_registro_venda():
    """Sales registration interface"""
    st.header("🧾 Registrar Venda")
    
    # Product search section
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        codigo = st.text_input("Código do Produto", value=st.session_state.ultimo_codigo or "")
    
    with col2:
        if st.button("Buscar Produto"):
            st.session_state.ultimo_codigo = codigo
    
    with col3:
        if st.button("Limpar"):
            st.session_state.ultimo_codigo = None
            st.rerun()
    
    # Display found product and add to cart
    if codigo and codigo in st.session_state.produtos_db:
        p = st.session_state.produtos_db[codigo]
        col1, col2 = st.columns([1, 3])
        
        with col1:
            if p.get("foto"):
                st.image(p["foto"], width=100)
        
        with col2:
            st.success(f"Produto encontrado: {p['nome']}")
            st.write(f"Preço: R$ {p['preco']:.2f} | Estoque: {p['estoque']}")
            
            qtd_col, add_col = st.columns([1, 1])
            qtd = qtd_col.number_input("Quantidade", min_value=1, max_value=p["estoque"], step=1)
            
            if add_col.button("Adicionar ao Carrinho"):
                st.session_state.carrinho.append({
                    "codigo_barras": p["codigo_barras"],
                    "produto": p["nome"],
                    "quantidade": qtd,
                    "preco_unit": p["preco"],
                    "total": qtd * p["preco"],
                    "foto": p.get("foto", "")
                })
                # Update product stock
                st.session_state.produtos_db[codigo]["estoque"] -= qtd
                st.success("Produto adicionado ao carrinho!")
                st.session_state.ultimo_codigo = None
                st.rerun()
    
    # Search by name option
    with st.expander("Buscar por Nome"):
        termo_busca = st.text_input("Nome do produto")
        if st.button("Buscar por Nome") and termo_busca:
            resultados = buscar_produto(termo_busca, "nome")
            exibir_resultados_busca(resultados)
    
    # Shopping cart
    st.subheader("🛒 Carrinho")
    if not st.session_state.carrinho:
        st.info("Seu carrinho está vazio.")
    else:
        total = 0
        for i, item in enumerate(st.session_state.carrinho):
            col1, col2, col3, col4 = st.columns([1, 4, 2, 1])
            
            with col1:
                if item.get("foto"):
                    st.image(item["foto"], width=60)
            
            with col2:
                st.write(f"{item['produto']}")
                st.caption(f"Código: {item['codigo_barras']}")
            
            with col3:
                st.write(f"Qtd: {item['quantidade']} x R$ {item['preco_unit']:.2f}")
                st.write(f"Subtotal: R$ {item['total']:.2f}")
            
            with col4:
                if st.button("🗑️", key=f"del_{i}"):
                    # Return stock before removing from cart
                    codigo = item["codigo_barras"]
                    if codigo in st.session_state.produtos_db:
                        st.session_state.produtos_db[codigo]["estoque"] += item["quantidade"]
                    
                    st.session_state.carrinho.pop(i)
                    st.rerun()
            
            total += item['total']
        
        st.markdown(f"### Total: R$ {total:.2f}")
        
        # Checkout section
        if st.button("🧾 Finalizar Venda"):
            checkout_col1, checkout_col2 = st.columns(2)
            
            with checkout_col1:
                cliente = st.text_input("Nome do Cliente", "Cliente Padrão")
            
            with checkout_col2:
                forma = st.selectbox("Forma de Pagamento", ["Pix", "Cartão", "Dinheiro"])
            
            if st.button("Confirmar"):
                if st.session_state.carrinho:
                    venda = {
                        "id": str(uuid.uuid4())[:8],
                        "cliente": cliente,
                        "forma_pgto": forma,
                        "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "itens": st.session_state.carrinho.copy(),
                        "total": total
                    }
                    
                    st.session_state.vendas_db.append(venda)
                    html = gerar_recibo_html(venda)
                    
                    st.download_button("📄 Baixar Recibo HTML", html, f"recibo_{venda['id']}.html", "text/html")
                    st.components.v1.html(html, height=600)
                    
                    st.session_state.carrinho = []
                    st.success("Venda concluída!")

# Module: Financial Dashboard
def render_painel():
    """Financial dashboard with reports and charts"""
    st.header("📈 Painel de Vendas")

    # Try to load external CSV data
    try:
        venda_df = pd.read_csv(URL_VENDA)
        st.success("Dados externos carregados com sucesso!")
    except Exception as e:
        st.warning(f"Não foi possível carregar dados externos. Usando apenas dados locais.")
        venda_df = pd.DataFrame(columns=["DATA", "ID_CLIENTE", "ID_FORMA_PGTO", "TOTAL"])

    # Format the DATA column to datetime
    if "DATA" in venda_df.columns:
        venda_df["DATA"] = pd.to_datetime(venda_df["DATA"], errors="coerce")
    else:
        venda_df["DATA"] = pd.to_datetime([])

    # Combine with local sales data
    if st.session_state.vendas_db:
        locais_df = pd.DataFrame([{
            "DATA": pd.to_datetime(v["data"]),
            "ID_CLIENTE": v["cliente"],
            "ID_FORMA_PGTO": v["forma_pgto"],
            "TOTAL": v["total"]
        } for v in st.session_state.vendas_db])
        
        venda_df = pd.concat([venda_df, locais_df], ignore_index=True)

    # Date and payment method filters
    st.subheader("Filtros")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        data_inicio = st.date_input("Data Inicial", value=datetime.today().replace(day=1))
    
    with col2:
        data_fim = st.date_input("Data Final", value=datetime.today())
    
    # Get unique payment methods
    if "ID_FORMA_PGTO" in venda_df.columns:
        formas = ["Todas"] + list(venda_df["ID_FORMA_PGTO"].dropna().unique())
    else:
        formas = ["Todas"]
    
    with col3:
        forma_pgto = st.selectbox("Forma de Pagamento", formas)

    # Apply filters
    try:
        filtro = (venda_df["DATA"].dt.date >= data_inicio) & (venda_df["DATA"].dt.date <= data_fim)
        if forma_pgto != "Todas":
            filtro &= venda_df["ID_FORMA_PGTO"] == forma_pgto
        
        df = venda_df[filtro]
    except Exception as e:
        st.error(f"Erro ao aplicar filtros: {e}")
        df = pd.DataFrame()

    # Show metrics and charts
    if not df.empty:
        st.subheader("Métricas")
        
        metricas_col1, metricas_col2, metricas_col3 = st.columns(3)
        
        with metricas_col1:
            st.metric("💰 Total no Período", f"R$ {df['TOTAL'].sum():,.2f}")
        
        with metricas_col2:
            st.metric("🛒 Total de Vendas", f"{len(df)}")
        
        with metricas_col3:
            if len(df) > 0:
                ticket_medio = df['TOTAL'].sum() / len(df)
                st.metric("💵 Ticket Médio", f"R$ {ticket_medio:,.2f}")
        
        # Charts
        st.subheader("Gráficos")
        
        charts_col1, charts_col2 = st.columns(2)
        
        with charts_col1:
            if "ID_FORMA_PGTO" in df.columns:
                st.subheader("Vendas por Forma de Pagamento")
                pgto_chart = df.groupby("ID_FORMA_PGTO")["TOTAL"].sum().reset_index()
                st.bar_chart(pgto_chart.set_index("ID_FORMA_PGTO"))
        
        with charts_col2:
            st.subheader("Vendas por Data")
            if not df.empty:
                date_chart = df.groupby(df["DATA"].dt.date)["TOTAL"].sum().reset_index()
                st.line_chart(date_chart.set_index("DATA"))
        
        # Table view
        st.subheader("Detalhamento de Vendas")
        if not df.empty:
            st.dataframe(df)

# Main app function
def main():
    # Logo and sidebar navigation
    st.sidebar.image("https://i.imgur.com/Ka8kNST.png", width=150)
    st.sidebar.title("🧭 ORION PDV")
    
    # Menu selection
    menu = st.sidebar.radio("Escolha uma opção:", [
        "🧾 Registrar Venda",
        "📦 Cadastro de Produto",
        "📈 Painel Financeiro"
    ], key=f"menu_navegacao_{str(uuid.uuid4())[:8]}")

    # Render the selected module
    if "Registrar Venda" in menu:
        render_registro_venda()
    elif "Cadastro de Produto" in menu:
        render_cadastro_produto()
    elif "Painel Financeiro" in menu:
        render_painel()
    
    # Footer
    st.sidebar.divider()
    st.sidebar.caption("© 2025 ORION PDV")

# Run the app
if __name__ == "__main__":
    main()
