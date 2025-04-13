import streamlit as st
import pandas as pd
from datetime import datetime
import uuid
import hashlib

# Configuração da página
st.set_page_config(page_title="ORION PDV", layout="wide")

# Dados de autenticação
USUARIOS = {
    "admjesus": {
        "nome": "ADM Jesus",
        "senha_hash": hashlib.sha256("senha123".encode()).hexdigest()
    }
}

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
        }
    }

if 'vendas_db' not in st.session_state:
    st.session_state.vendas_db = [{
        "id": "ABC123",
        "data": "2025-04-13 10:00:00",
        "cliente": "Consumidor Final",
        "forma_pgto": "Dinheiro",
        "itens": [{
            "produto": "Leite Integral",
            "quantidade": 1,
            "preco_unit": 5.99,
            "total": 5.99
        }],
        "total": 5.99
    }]

if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

if 'clientes_db' not in st.session_state:
    st.session_state.clientes_db = []

# Função para autenticar usuário
def autenticar_usuario():
    st.title("🔐 Login - ORION PDV")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("https://drive.google.com/file/d/12XF47mD3ibrkubkj5LcRdosO2mn-4aIy/view?usp=sharing", width=200)
    
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    
    if st.button("Entrar", type="primary"):
        if usuario in USUARIOS:
            hash_inserida = hashlib.sha256(senha.encode()).hexdigest()
            if hash_inserida == USUARIOS[usuario]["senha_hash"]:
                st.session_state["autenticado"] = True
                st.session_state["usuario"] = usuario
                st.rerun()
            else:
                st.error("Senha incorreta.")
        else:
            st.error("Usuário não encontrado.")

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

# Módulo de Registro de Venda
def registrar_venda():
    st.header("🧾 Registrar Venda")
    
    # Busca por produto
    st.subheader("Buscar Produto")
    termo_busca = st.text_input("Digite o nome ou código do produto:")
    
    if termo_busca:
        resultados = []
        for codigo, produto in st.session_state.produtos_db.items():
            if (termo_busca.lower() in produto['nome'].lower() or 
                termo_busca in produto['codigo_barras']):
                resultados.append(produto)
        
        if resultados:
            cols = st.columns(3)
            for i, produto in enumerate(resultados):
                with cols[i % 3]:
                    st.image(produto['foto'], width=150, caption=produto['nome'])
                    st.write(f"**Preço:** R$ {produto['preco']:.2f}")
                    st.write(f"**Estoque:** {produto['estoque']}")
                    
                    with st.form(key=f"add_{produto['codigo_barras']}"):
                        qtd = st.number_input(
                            "Quantidade",
                            min_value=1,
                            max_value=produto['estoque'],
                            value=1,
                            key=f"qtd_{produto['codigo_barras']}"
                        )
                        
                        if st.form_submit_button("Adicionar"):
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
                            
                            st.session_state.produtos_db[produto['codigo_barras']]['estoque'] -= qtd
                            st.success(f"Adicionado {qtd}x {produto['nome']}")
                            st.rerun()
        else:
            st.warning("Nenhum produto encontrado.")
    
    # Carrinho
    st.subheader("🛒 Carrinho")
    
    if not st.session_state.carrinho:
        st.info("Carrinho vazio")
    else:
        total_venda = 0
        for i, item in enumerate(st.session_state.carrinho):
            cols = st.columns([1, 3, 1, 1, 1])
            with cols[0]:
                st.image(item['foto'], width=50)
            with cols[1]:
                st.write(f"**{item['produto']}**")
            with cols[2]:
                st.write(f"R$ {item['preco_unit']:.2f}")
            with cols[3]:
                st.write(f"{item['quantidade']}x")
            with cols[4]:
                st.write(f"R$ {item['total']:.2f}")
                if st.button("❌", key=f"rm_{i}"):
                    st.session_state.produtos_db[item['codigo_barras']]['estoque'] += item['quantidade']
                    st.session_state.carrinho.pop(i)
                    st.rerun()
            
            total_venda += item['total']
        
        st.divider()
        st.markdown(f"**Total:** R$ {total_venda:.2f}")
        
        # Finalização
        with st.form("finalizar_venda"):
            cliente = st.selectbox(
                "Cliente",
                ["Consumidor Final"] + [c["NOME"] for c in st.session_state.clientes_db]
            )
            forma_pgto = st.selectbox(
                "Forma de Pagamento",
                ["Dinheiro", "Cartão", "Pix"]
            )
            
            if st.form_submit_button("Finalizar Venda"):
                nova_venda = {
                    "id": str(uuid.uuid4())[:6],
                    "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "cliente": cliente,
                    "forma_pgto": forma_pgto,
                    "itens": st.session_state.carrinho.copy(),
                    "total": total_venda
                }
                
                st.session_state.vendas_db.append(nova_venda)
                st.session_state.carrinho = []
                
                recibo_html = gerar_recibo_html(nova_venda)
                st.components.v1.html(recibo_html, height=600)
                st.download_button(
                    "📄 Baixar Recibo",
                    recibo_html,
                    f"recibo_{nova_venda['id']}.html",
                    "text/html"
                )
                st.success("Venda registrada!")

# Módulo de Cadastro de Produto
def cadastro_produto():
    st.header("📦 Cadastro de Produto")
    
    with st.form("form_produto"):
        col1, col2 = st.columns(2)
        
        with col1:
            nome = st.text_input("Nome do Produto")
            codigo = st.text_input("Código de Barras")
            grupo = st.text_input("Grupo/Categoria")
        
        with col2:
            preco = st.number_input("Preço", min_value=0.01, format="%.2f")
            estoque = st.number_input("Estoque", min_value=0)
            marca = st.text_input("Marca")
        
        foto_url = st.text_input("URL da Imagem")
        
        if st.form_submit_button("Salvar Produto"):
            if nome and codigo:
                st.session_state.produtos_db[codigo] = {
                    "nome": nome,
                    "codigo_barras": codigo,
                    "grupo": grupo,
                    "marca": marca,
                    "preco": preco,
                    "estoque": estoque,
                    "foto": foto_url if foto_url else "https://via.placeholder.com/150"
                }
                st.success("Produto cadastrado!")
            else:
                st.error("Nome e código são obrigatórios")
    
    st.subheader("Produtos Cadastrados")
    produtos_df = pd.DataFrame(st.session_state.produtos_db.values())
    st.dataframe(produtos_df[["nome", "codigo_barras", "preco", "estoque"]])

# Módulo de Cadastro de Cliente
def cadastro_cliente():
    st.header("👤 Cadastro de Cliente")
    
    with st.form("form_cliente"):
        col1, col2 = st.columns(2)
        
        with col1:
            nome = st.text_input("Nome Completo")
            documento = st.text_input("CPF/CNPJ")
            email = st.text_input("Email")
        
        with col2:
            telefone = st.text_input("Telefone")
            endereco = st.text_input("Endereço")
            cidade = st.text_input("Cidade")
        
        if st.form_submit_button("Salvar Cliente"):
            novo_cliente = {
                "ID": str(uuid.uuid4())[:8],
                "NOME": nome,
                "DOCUMENTO": documento,
                "EMAIL": email,
                "TELEFONE": telefone,
                "ENDERECO": endereco,
                "CIDADE": cidade
            }
            st.session_state.clientes_db.append(novo_cliente)
            st.success("Cliente cadastrado!")
    
    st.subheader("Clientes Cadastrados")
    if st.session_state.clientes_db:
        st.dataframe(pd.DataFrame(st.session_state.clientes_db))
    else:
        st.info("Nenhum cliente cadastrado")

# Módulo de Painel Financeiro
def painel_financeiro():
    st.header("📊 Painel Financeiro")
    
    # Filtros na sidebar
    st.sidebar.subheader("Filtros")
    
    # Filtro por data
    datas_disponiveis = sorted(list(set(
        pd.to_datetime(venda['data']).date() 
        for venda in st.session_state.vendas_db
    )), reverse=True)
    
    data_selecionada = st.sidebar.selectbox(
        "Período",
        datas_disponiveis,
        index=0
    )
    
    # Filtro por forma de pagamento
    formas_pgto = ["Todas"] + sorted(list(set(
        venda['forma_pgto'] 
        for venda in st.session_state.vendas_db
    )))
    
    forma_selecionada = st.sidebar.selectbox(
        "Forma de Pagamento",
        formas_pgto
    )
    
    # Aplicar filtros
    vendas_filtradas = [
        venda for venda in st.session_state.vendas_db
        if pd.to_datetime(venda['data']).date() == data_selecionada and
        (forma_selecionada == "Todas" or venda['forma_pgto'] == forma_selecionada)
    ]
    
    # Métricas
    st.subheader("Métricas")
    
    total_vendas = sum(venda['total'] for venda in vendas_filtradas)
    num_vendas = len(vendas_filtradas)
    ticket_medio = total_vendas / num_vendas if num_vendas > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Vendas", f"R$ {total_vendas:.2f}")
    col2.metric("Número de Vendas", num_vendas)
    col3.metric("Ticket Médio", f"R$ {ticket_medio:.2f}")
    
    # Análise de Vendas
    st.subheader("Análise de Vendas")
    
    tab1, tab2 = st.tabs(["Vendas por Dia", "Vendas por Forma de Pagamento"])
    
    with tab1:
        st.line_chart(
            pd.DataFrame({
                "Data": [pd.to_datetime(venda['data']).date() for venda in st.session_state.vendas_db],
                "Total": [venda['total'] for venda in st.session_state.vendas_db]
            }).groupby("Data").sum()
        )
    
    with tab2:
        st.bar_chart(
            pd.DataFrame({
                "FormaPagto": [venda['forma_pgto'] for venda in st.session_state.vendas_db],
                "Total": [venda['total'] for venda in st.session_state.vendas_db]
            }).groupby("FormaPagto").sum()
        )
    
    # Detalhes
    st.subheader("Detalhes das Vendas")
    if vendas_filtradas:
        st.dataframe(pd.DataFrame(vendas_filtradas))
    else:
        st.info("Nenhuma venda encontrada com os filtros selecionados")

# Página principal
def main():
    if "autenticado" not in st.session_state:
        autenticar_usuario()
        return
    
    # Sidebar com menu
    st.sidebar.image("https://i.imgur.com/Ka8kNST.png", width=100)
    st.sidebar.title(f"Bem-vindo, {st.session_state.usuario}")
    
    opcao = st.sidebar.radio(
        "Menu",
        ["Registrar Venda", "Cadastro de Produto", "Cadastro de Cliente", "Painel Financeiro"]
    )
    
    if opcao == "Registrar Venda":
        registrar_venda()
    elif opcao == "Cadastro de Produto":
        cadastro_produto()
    elif opcao == "Cadastro de Cliente":
        cadastro_cliente()
    elif opcao == "Painel Financeiro":
        painel_financeiro()
    
    st.sidebar.divider()
    if st.sidebar.button("Sair"):
        del st.session_state["autenticado"]
        st.rerun()

if __name__ == "__main__":
    main()
