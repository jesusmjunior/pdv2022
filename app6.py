import streamlit as st
import pandas as pd
from datetime import datetime
import uuid

# Configuração da página
st.set_page_config(page_title="ORION PDV - Vendas", layout="wide")

# Inicialização do estado da sessão
if 'produtos_db' not in st.session_state:
    st.session_state.produtos_db = {
        '7891000315507': {
            'nome': 'Leite Integral',
            'codigo_barras': '7891000315507',
            'grupo': 'Laticínios',
            'marca': 'Ninho',
            'preco': 5.99,
            'estoque': 50,
            'foto': "https://www.nestleprofessional.com.br/sites/default/files/styles/np_product_detail/public/2022-09/leite-em-po-ninho-integral-lata-400g.png"
        },
        '7891910000197': {
            'nome': 'Arroz',
            'codigo_barras': '7891910000197',
            'grupo': 'Grãos',
            'marca': 'Tio João',
            'preco': 22.90,
            'estoque': 35,
            'foto': "https://m.media-amazon.com/images/I/61l6ojQQtDL._AC_UF894,1000_QL80_.jpg"
        },
        '7891149410116': {
            'nome': 'Café',
            'codigo_barras': '7891149410116',
            'grupo': 'Bebidas',
            'marca': 'Pilão',
            'preco': 15.75,
            'estoque': 28,
            'foto': "https://m.media-amazon.com/images/I/51xq5MnKz4L._AC_UF894,1000_QL80_.jpg"
        }
    }

if 'vendas_db' not in st.session_state:
    st.session_state.vendas_db = []

if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

# Função para gerar recibo HTML
def gerar_recibo_html(venda):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    html = f"""
    <!DOCTYPE html><html><head><meta charset="UTF-8"><title>Recibo</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px; }}
        .header {{ text-align: center; margin-bottom: 20px; }}
        .linha {{ border-top: 1px dashed #000; margin: 10px 0; }}
        .total {{ font-weight: bold; font-size: 1.2em; }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #f2f2f2; }}
        .footer {{ text-align: center; margin-top: 30px; font-size: 0.9em; color: #555; }}
    </style></head><body>
    <div class="header">
        <h2>ORION PDV</h2>
        <h3>CUPOM ELETRÔNICO</h3>
    </div>
    <div class="linha"></div>
    <p><strong>Data:</strong> {venda['data']}</p>
    <p><strong>Cliente:</strong> {venda['cliente']}</p>
    <p><strong>Pagamento:</strong> {venda['forma_pgto']}</p>
    <div class="linha"></div>
    <table>
        <thead>
            <tr>
                <th>Produto</th>
                <th>Qtd</th>
                <th>Unit</th>
                <th>Total</th>
            </tr>
        </thead>
        <tbody>
    """
    
    for item in venda['itens']:
        html += f"""
            <tr>
                <td>{item['produto']}</td>
                <td>{item['quantidade']}</td>
                <td>R$ {item['preco_unit']:.2f}</td>
                <td>R$ {item['total']:.2f}</td>
            </tr>
        """
    
    html += f"""
        </tbody>
    </table>
    <div class="linha"></div>
    <p class="total">Total da Venda: R$ {venda['total']:.2f}</p>
    <div class="linha"></div>
    <div class="footer">
        <p>Obrigado pela preferência!</p>
        <p>Volte sempre</p>
        <p><small>Gerado em: {timestamp}</small></p>
    </div>
    <script>
        window.onload = function() {{
            window.print();
        }}
    </script>
    </body></html>
    """
    return html

# Função para buscar produtos
def buscar_produto_por_nome(termo):
    termo = termo.lower()
    resultados = []
    for codigo, produto in st.session_state.produtos_db.items():
        if termo in produto['nome'].lower():
            resultados.append(produto)
    return resultados

# Função para registrar venda
def registrar_venda():
    st.title("🛒 Registro de Venda")
    
    # Busca por nome do produto
    st.subheader("Buscar Produto por Nome")
    termo_busca = st.text_input("Digite o nome do produto:")
    
    if termo_busca:
        resultados = buscar_produto_por_nome(termo_busca)
        
        if resultados:
            st.subheader("Resultados da Busca")
            cols = st.columns(3)
            
            for i, produto in enumerate(resultados):
                with cols[i % 3]:
                    st.image(produto['foto'], width=150, caption=produto['nome'])
                    st.write(f"**Preço:** R$ {produto['preco']:.2f}")
                    st.write(f"**Em estoque:** {produto['estoque']} unidades")
                    
                    # Adicionar ao carrinho
                    with st.form(key=f"form_{produto['codigo_barras']}"):
                        qtd = st.number_input(
                            "Quantidade",
                            min_value=1,
                            max_value=produto['estoque'],
                            value=1,
                            key=f"qtd_{produto['codigo_barras']}"
                        )
                        
                        if st.form_submit_button("Adicionar ao Carrinho"):
                            # Verificar se já está no carrinho
                            item_existente = next((item for item in st.session_state.carrinho 
                                                 if item['codigo_barras'] == produto['codigo_barras']), None)
                            
                            if item_existente:
                                item_existente['quantidade'] += qtd
                                item_existente['total'] = item_existente['quantidade'] * item_existente['preco_unit']
                            else:
                                st.session_state.carrinho.append({
                                    "codigo_barras": produto['codigo_barras'],
                                    "produto": produto['nome'],
                                    "quantidade": qtd,
                                    "preco_unit": produto['preco'],
                                    "total": qtd * produto['preco'],
                                    "foto": produto['foto']
                                })
                            
                            # Atualizar estoque
                            st.session_state.produtos_db[produto['codigo_barras']]['estoque'] -= qtd
                            st.success(f"{qtd}x {produto['nome']} adicionado ao carrinho!")
                            st.rerun()
        else:
            st.warning("Nenhum produto encontrado com esse nome.")

    # Exibir carrinho
    st.subheader("🛒 Carrinho de Compras")
    
    if not st.session_state.carrinho:
        st.info("O carrinho está vazio.")
    else:
        total_venda = 0
        
        for i, item in enumerate(st.session_state.carrinho):
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            
            with col1:
                st.image(item['foto'], width=80)
                st.write(f"**{item['produto']}**")
            
            with col2:
                st.write(f"**Preço:**")
                st.write(f"R$ {item['preco_unit']:.2f}")
            
            with col3:
                st.write(f"**Qtd:**")
                st.write(f"{item['quantidade']}")
            
            with col4:
                st.write(f"**Total:**")
                st.write(f"R$ {item['total']:.2f}")
                
                # Botão para remover item
                if st.button("❌", key=f"remove_{i}"):
                    # Devolver ao estoque
                    st.session_state.produtos_db[item['codigo_barras']]['estoque'] += item['quantidade']
                    # Remover do carrinho
                    st.session_state.carrinho.pop(i)
                    st.rerun()
            
            total_venda += item['total']
            st.divider()
        
        st.markdown(f"### Total da Venda: R$ {total_venda:.2f}")
        
        # Finalizar venda
        with st.form("finalizar_venda"):
            st.subheader("Finalizar Venda")
            
            cliente = st.text_input("Nome do Cliente", "Consumidor Final")
            forma_pgto = st.selectbox("Forma de Pagamento", ["Dinheiro", "Cartão", "Pix", "Outro"])
            
            if st.form_submit_button("Finalizar Venda"):
                # Registrar a venda
                nova_venda = {
                    "id": str(uuid.uuid4())[:8],
                    "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "cliente": cliente,
                    "forma_pgto": forma_pgto,
                    "itens": st.session_state.carrinho.copy(),
                    "total": total_venda
                }
                
                # Adicionar ao histórico de vendas
                st.session_state.vendas_db.append(nova_venda)
                
                # Gerar recibo
                recibo_html = gerar_recibo_html(nova_venda)
                
                # Limpar carrinho
                st.session_state.carrinho = []
                
                # Mostrar recibo
                st.success("Venda registrada com sucesso!")
                st.balloons()
                
                # Exibir recibo para impressão
                st.components.v1.html(recibo_html, height=600, scrolling=True)
                
                # Botão para download do recibo
                st.download_button(
                    label="📄 Baixar Recibo",
                    data=recibo_html,
                    file_name=f"recibo_{nova_venda['id']}.html",
                    mime="text/html"
                )

# Função para exibir o painel financeiro
def painel_financeiro():
    st.title("📊 Painel Financeiro")
    
    if not st.session_state.vendas_db:
        st.info("Nenhuma venda registrada ainda.")
        return
    
    # Criar DataFrame com as vendas
    vendas_df = pd.DataFrame(st.session_state.vendas_db)
    
    # Converter a coluna de data
    vendas_df['data'] = pd.to_datetime(vendas_df['data'])
    
    # Filtros
    st.sidebar.subheader("Filtros")
    
    # Filtro por data
    data_min = vendas_df['data'].min().date()
    data_max = vendas_df['data'].max().date()
    
    datas = st.sidebar.date_input(
        "Período",
        [data_min, data_max],
        min_value=data_min,
        max_value=data_max
    )
    
    # Filtro por forma de pagamento
    formas_pgto = ["Todas"] + list(vendas_df['forma_pgto'].unique())
    forma_selecionada = st.sidebar.selectbox("Forma de Pagamento", formas_pgto)
    
    # Aplicar filtros
    if len(datas) == 2:
        vendas_filtradas = vendas_df[
            (vendas_df['data'].dt.date >= datas[0]) & 
            (vendas_df['data'].dt.date <= datas[1])
        ]
    else:
        vendas_filtradas = vendas_df.copy()
    
    if forma_selecionada != "Todas":
        vendas_filtradas = vendas_filtradas[vendas_filtradas['forma_pgto'] == forma_selecionada]
    
    # Métricas
    st.subheader("Métricas")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total de Vendas", f"R$ {vendas_filtradas['total'].sum():,.2f}")
    
    with col2:
        st.metric("Número de Vendas", len(vendas_filtradas))
    
    with col3:
        ticket_medio = vendas_filtradas['total'].mean() if len(vendas_filtradas) > 0 else 0
        st.metric("Ticket Médio", f"R$ {ticket_medio:,.2f}")
    
    # Gráficos
    st.subheader("Análise de Vendas")
    
    tab1, tab2 = st.tabs(["Vendas por Dia", "Vendas por Forma de Pagamento"])
    
    with tab1:
        vendas_por_dia = vendas_filtradas.groupby(vendas_filtradas['data'].dt.date)['total'].sum()
        st.line_chart(vendas_por_dia)
    
    with tab2:
        vendas_por_pgto = vendas_filtradas.groupby('forma_pgto')['total'].sum()
        st.bar_chart(vendas_por_pgto)
    
    # Detalhes das vendas
    st.subheader("Detalhes das Vendas")
    st.dataframe(vendas_filtradas)

# Menu principal
def main():
    st.sidebar.title("ORION PDV")
    st.sidebar.image("https://i.imgur.com/Ka8kNST.png", width=100)
    
    opcao = st.sidebar.radio(
        "Menu",
        ["Registrar Venda", "Painel Financeiro"]
    )
    
    if opcao == "Registrar Venda":
        registrar_venda()
    elif opcao == "Painel Financeiro":
        painel_financeiro()

if __name__ == "__main__":
    main()
