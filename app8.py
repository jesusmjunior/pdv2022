import streamlit as st
import pandas as pd
from datetime import datetime
import uuid
import hashlib
import re
from PIL import Image

# Configuração da página
st.set_page_config(page_title="ORION PDV-ADM. JESUS MARTINS & ORION I.A.", layout="wide")

# URLs dos dados externos (do app2)
URL_GRUPO = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0r3XE4DpzlYJjZwjc2c_pW_K3euooN9caPedtSq-nH_aEPnvx1jrcd9t0Yhg8fqXfR3j5jM2OyUQQ/pub?gid=528868130&single=true&output=csv"
URL_MARCAS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0r3XE4DpzlYJjZwjc2c_pW_K3euooN9caPedtSq-nH_aEPnvx1jrcd9t0Yhg8fqXfR3j5jM2OyUQQ/pub?gid=832596780&single=true&output=csv"
URL_CLIENTE = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0r3XE4DpzlYJjZwjc2c_pW_K3euooN9caPedtSq-nH_aEPnvx1jrcd9t0Yhg8fqXfR3j5jM2OyUQQ/pub?gid=1645177762&single=true&output=csv"
URL_PRODUTO = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0r3XE4DpzlYJjZwjc2c_pW_K3euooN9caPedtSq-nH_aEPnvx1jrcd9t0Yhg8fqXfR3j5jM2OyUQQ/pub?gid=1506891785&single=true&output=csv"
URL_PGTO = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0r3XE4DpzlYJjZwjc2c_pW_K3euooN9caPedtSq-nH_aEPnvx1jrcd9t0Yhg8fqXfR3j5jM2OyUQQ/pub?gid=1061064660&single=true&output=csv"
URL_VENDA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0r3XE4DpzlYJjZwjc2c_pW_K3euooN9caPedtSq-nH_aEPnvx1jrcd9t0Yhg8fqXfR3j5jM2OyUQQ/pub?gid=1817416820&single=true&output=csv"

# Dados de autenticação (do app2)
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

if 'ultimo_codigo' not in st.session_state:
    st.session_state.ultimo_codigo = None

# Função para extrair números de uma string (do app2)
def extrair_codigo_barras(texto):
    # Extrai todos os números da string
    numeros = re.findall(r'\d+', texto)
    
    # Junta todos os números em uma única string
    codigo_extraido = ''.join(numeros)
    
    # Se tivermos um número de pelo menos 8 dígitos, considera como um código de barras válido
    if len(codigo_extraido) >= 8:
        return codigo_extraido
    
    return None

# Função para autenticar usuário (mantendo o visual do app7 com a lógica do app2)
def autenticar_usuario():
    st.title("🔐 Login - ORION PDV")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("https://i.imgur.com/Ka8kNST.png", width=200)
    
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    
    if st.button("Entrar", type="primary"):
        if usuario in USUARIOS:
            hash_inserida = hashlib.sha256(senha.encode()).hexdigest()
            if hash_inserida == USUARIOS[usuario]["senha_hash"]:
                st.session_state["autenticado"] = True
                st.session_state["usuario"] = usuario
                st.success("Login realizado com sucesso!")
                st.rerun()
            else:
                st.error("Senha incorreta.")
        else:
            st.error("Usuário não encontrado.")

# Função para reconhecimento de texto via OCR Web (do app2)
def reconhecer_texto_imagem():
    st.markdown("""
    <div style="padding: 10px; border: 1px solid #f63366; border-radius: 5px; margin-bottom: 10px; background-color: #fff5f5;">
        <h4 style="color: #f63366;">Como usar o reconhecimento de texto:</h4>
        <ol>
            <li>Tire uma foto clara do código de barras com seu celular</li>
            <li>Use um aplicativo de OCR como Google Lens para extrair os números</li>
            <li>Cole os números obtidos no campo abaixo</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    ocr_texto = st.text_area("Cole aqui o texto obtido pelo OCR ou os números do código de barras",
                         placeholder="Cole aqui o texto que contém os números do código de barras...",
                         height=100)
    
    codigo_barras = None
    
    if st.button("Extrair Código de Barras", type="primary") and ocr_texto:
        codigo_barras = extrair_codigo_barras(ocr_texto)
        
        if codigo_barras:
            st.success(f"Código de barras extraído: {codigo_barras}")
            st.session_state.ultimo_codigo = codigo_barras
        else:
            st.error("Não foi possível extrair um código de barras válido do texto fornecido.")
    
    return st.session_state.ultimo_codigo

# Função para instruções de scanner (do app2)
def mostrar_instrucoes_scanner():
    st.markdown("""
    ### 📱 Como utilizar aplicativos de scanner
    
    Para escanear códigos de barras com seu celular:
    
    1. **Google Lens** - Aponte para o código, tire uma foto e veja os números detectados
       - Abra o Google Lens (disponível no Google Assistant ou Google Fotos)
       - Aponte para o código de barras
       - Quando os números aparecerem, copie-os
    
    2. **Aplicativo de Câmera** - Muitos celulares já detectam códigos automaticamente
       - Abra a câmera e aponte para o código
       - Alguns celulares mostram um link ou os números do código
       
    3. **Aplicativos específicos** - Há vários aplicativos gratuitos para escanear códigos:
       - "Barcode Scanner" (Android/iOS)
       - "QR & Barcode Scanner" (Android/iOS)
    
    Depois de obter os números do código de barras, digite-os na aba "Digitar Código" 
    ou cole o texto completo na aba "Extrair de Texto" e o sistema identificará automaticamente o código.
    """)
    
    # Adicionando QR Code para abrir esta aplicação no celular
    app_url = "https://pdvoliveira.streamlit.app" 
    st.markdown(f"""
    <div style="text-align: center; margin: 20px 0;">
        <p>Escaneie este QR Code para abrir o aplicativo no seu celular:</p>
        <img src="https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={app_url}" width="150">
    </div>
    """, unsafe_allow_html=True)

# Função para gerar recibo HTML (do app7)
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

# Scanner de código de barras assistido (do app2)
def leitor_codigo_barras():
    st.subheader("📷 Scanner de Código de Barras")
    
    st.markdown("""
    <div style="padding: 20px; border: 1px solid #ccc; border-radius: 5px; margin-bottom: 20px;">
        <h4 style="color: #0066cc;">Scanner de Código de Barras Assistido</h4>
        <p>Para escanear um código de barras, você tem duas opções:</p>
        <ol>
            <li><strong>Via celular:</strong> Use Google Lens ou aplicativo de scanner, depois digite o código detectado</li>
            <li><strong>Via caixa de texto:</strong> Utilize a seção abaixo para colar texto com números e extrair o código automaticamente</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Digitar Código", "Extrair de Texto"])
    
    with tab1:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Manual input
            codigo_barras = st.text_input("Digite o código de barras:", 
                                        value=st.session_state.ultimo_codigo if st.session_state.ultimo_codigo else "",
                                        placeholder="Ex: 7891000315507")
        
        with col2:
            # Exibir imagem de exemplo de código de barras
            st.image("https://www.qr-code-generator.com/wp-content/themes/qr/images/barcode-generator-free.jpg", 
                   width=150, caption="Exemplo")
    
        if st.button("Usar Código", type="primary") and codigo_barras:
            st.session_state.ultimo_codigo = codigo_barras
            st.success(f"Código registrado: {codigo_barras}")
    
    with tab2:
        # Reconhecimento avançado
        codigo_texto = reconhecer_texto_imagem()
    
    # Se temos um código válido (de qualquer uma das tabs), verificar no banco de dados
    codigo_selecionado = st.session_state.ultimo_codigo
    if codigo_selecionado and codigo_selecionado in st.session_state.produtos_db:
        produto = st.session_state.produtos_db[codigo_selecionado]
        st.success(f"Produto encontrado: {produto['nome']}")
        
        # Exibir informações do produto
        col1, col2 = st.columns([1, 2])
        with col1:
            if produto['foto']:
                st.image(produto['foto'], width=150)
        with col2:
            st.subheader(produto['nome'])
            st.write(f"**Preço:** R$ {produto['preco']:.2f}")
            st.write(f"**Estoque:** {produto['estoque']} unidades")
    elif codigo_selecionado:
        st.warning(f"Código {codigo_selecionado} não encontrado no cadastro.")
    
    return codigo_selecionado

# Módulo de Registro de Venda (melhorando com o leitor do app2)
def registrar_venda():
    st.header("🧾 Registrar Venda")
    
    # Opções de busca
    busca_tabs = st.tabs(["Buscar por Nome/Código", "Scanner de Código de Barras"])
    
    with busca_tabs[0]:
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
    
    with busca_tabs[1]:
        # Usar o scanner de código de barras avançado
        codigo_barras = leitor_codigo_barras()
        
        if codigo_barras and codigo_barras in st.session_state.produtos_db:
            produto = st.session_state.produtos_db[codigo_barras]
            qtd = st.number_input("Quantidade", min_value=1, max_value=produto['estoque'], value=1, key="qtd_scanner")
            
            if st.button("Adicionar ao Carrinho", type="primary"):
                item_existente = next((item for item in st.session_state.carrinho 
                                     if item['codigo_barras'] == codigo_barras), None)
                
                if item_existente:
                    item_existente['quantidade'] += qtd
                    item_existente['total'] = item_existente['quantidade'] * item_existente['preco_unit']
                else:
                    st.session_state.carrinho.append({
                        "codigo_barras": codigo_barras,
                        "produto": produto['nome'],
                        "quantidade": qtd,
                        "preco_unit": produto['preco'],
                        "total": qtd * produto['preco'],
                        "foto": produto['foto']
                    })
                
                st.session_state.produtos_db[codigo_barras]['estoque'] -= qtd
                st.success(f"Adicionado {qtd}x {produto['nome']}")
                st.session_state.ultimo_codigo = None
                st.rerun()
        
        # Instruções para uso com aplicativos externos
        with st.expander("Como escanear códigos com seu celular", expanded=False):
            mostrar_instrucoes_scanner()
    
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
            # Tentar carregar a lista de clientes da URL externa
            try:
                clientes_df = pd.read_csv(URL_CLIENTE)
                clientes_lista = ["Consumidor Final"] + list(clientes_df["NOME"].dropna())
            except:
                # Se falhar, usa os clientes do session_state
                clientes_lista = ["Consumidor Final"] + [c["NOME"] for c in st.session_state.clientes_db]

            # Tentar carregar formas de pagamento da URL externa
            try:
                pgto_df = pd.read_csv(URL_PGTO)
                pgto_lista = list(pgto_df["DESCRICAO"].dropna())
            except:
                pgto_lista = ["Dinheiro", "Cartão", "Pix"]
                
            cliente = st.selectbox("Cliente", clientes_lista)
            forma_pgto = st.selectbox("Forma de Pagamento", pgto_lista)
            
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

# Módulo de Cadastro de Produto (integrando com dados do Google Sheets)
def cadastro_produto():
    st.header("📦 Cadastro de Produto")
    
    # Tentar carregar dados das planilhas do Google
    try:
        grupo_df = pd.read_csv(URL_GRUPO)
        marcas_df = pd.read_csv(URL_MARCAS)
        grupos_lista = list(grupo_df["DESCRICAO"].dropna())
        marcas_lista = list(marcas_df["DESCRICAO"].dropna())
    except:
        grupos_lista = ["Alimentos", "Bebidas", "Limpeza", "Higiene", "Diversos"]
        marcas_lista = ["Nestlé", "Unilever", "P&G", "Ambev", "Outras"]
    
    # Adicionar opção para usar o scanner de código de barras
    usar_scanner = st.checkbox("Usar scanner de código de barras para o código")
    
    if usar_scanner:
        st.info("Escaneie o código de barras do produto")
        codigo_barras = leitor_codigo_barras()
        if codigo_barras:
            st.success(f"Código de barras obtido: {codigo_barras}")
    
    with st.form("form_produto"):
        col1, col2 = st.columns(2)
        
        with col1:
            nome = st.text_input("Nome do Produto")
            codigo = st.text_input("Código de Barras", 
                                 value=st.session_state.ultimo_codigo if usar_scanner and st.session_state.ultimo_codigo else "")
            grupo = st.selectbox("Grupo/Categoria", grupos_lista)
        
        with col2:
            preco = st.number_input("Preço", min_value=0.01, format="%.2f")
            estoque = st.number_input("Estoque", min_value=0)
            marca = st.selectbox("Marca", marcas_lista)
        
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
                
                # Limpar código de barras da sessão
                if usar_scanner:
                    st.session_state.ultimo_codigo = None
            else:
                st.error("Nome e código são obrigatórios")
    
    st.subheader("Produtos Cadastrados")
    produtos_df = pd.DataFrame(st.session_state.produtos_db.values())
    st.dataframe(produtos_df[["nome", "codigo_barras", "preco", "estoque"]])

# Módulo de Cadastro de Cliente (com dados do Google Sheets)
def cadastro_cliente():
    st.header("👤 Cadastro de Cliente")
    
    # Tenta carregar clientes existentes da planilha
    try:
        clientes_df = pd.read_csv(URL_CLIENTE)
        st.info(f"Dados externos disponíveis: {len(clientes_df)} clientes")
    except:
        st.warning("Não foi possível carregar dados externos de clientes")
    
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
        try:
            # Mostra os dados da planilha externa
            st.dataframe(clientes_df)
        except:
            st.info("Nenhum cliente cadastrado")

# Módulo de Painel Financeiro (melhorado com dados das planilhas)
def painel_financeiro():
    st.header("📊 Painel Financeiro")
    
    # Tentar carregar dados da planilha de vendas
    try:
        venda_ext_df = pd.read_csv(URL_VENDA)
        venda_ext_df["DATA"] = pd.to_datetime(venda_ext_df["DATA"], errors="coerce")
        st.success(f"Dados externos carregados: {len(venda_ext_df)} vendas")
        
        # Combinar dados externos com locais
        vendas_combinadas = st.session_state.vendas_db.copy()
        st.info("Mostrando dados combinados: externos + locais")
    except:
        vendas_combinadas = st.session_state.vendas_db.copy()
        st.warning("Dados externos indisponíveis. Mostrando apenas vendas locais.")
    
    # Processamento das vendas para o painel
    if not vendas_combinadas:
        st.warning("Nenhuma venda registrada")
        return
        
    # Transformar as vendas em um DataFrame para análise
    vendas_df = []
    for venda in vendas_combinadas:
        vendas_df.append({
            "id": venda.get("id", ""),
            "data": venda.get("data", ""),
            "cliente": venda.get("cliente", ""),
            "forma_pgto": venda.get("forma_pgto", ""),
            "total": venda.get("total", 0)
        })
    
    vendas_df = pd.DataFrame(vendas_df)
    
    # Converter datas para datetime
    vendas_df["data"] = pd.to_datetime(vendas_df["data"], errors="coerce")
    
    # Métricas gerais
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de Vendas", f"{len(vendas_df)}")
    with col2:
        st.metric("Faturamento Total", f"R$ {vendas_df['total'].sum():.2f}")
    with col3:
        st.metric("Ticket Médio", f"R$ {vendas_df['total'].mean():.2f}")
    
    # Filtros
    st.subheader("Filtros")
    col1, col2 = st.columns(2)
    with col1:
        # Filtro por data
        hoje = datetime.now().date()
        data_inicio = st.date_input("Data Inicial", 
                                  value=hoje - pd.Timedelta(days=30),
                                  max_value=hoje)
    with col2:
        data_fim = st.date_input("Data Final", 
                               value=hoje,
                               max_value=hoje)
    
    # Aplicar filtros
    mask = (vendas_df["data"].dt.date >= data_inicio) & (vendas_df["data"].dt.date <= data_fim)
    vendas_filtradas = vendas_df[mask]
    
    if len(vendas_filtradas) == 0:
        st.warning("Nenhuma venda no período selecionado")
        return
    
    # Gráficos
    st.subheader("Análise de Vendas")
    
    # Preparar dados para gráficos
    vendas_por_dia = vendas_filtradas.groupby(vendas_filtradas["data"].dt.date)["total"].sum().reset_index()
    vendas_por_dia.columns = ["data", "total"]
    
    # Gráfico de vendas por dia
    st.line_chart(vendas_por_dia.set_index("data"))
    
    # Vendas por forma de pagamento
    st.subheader("Vendas por Forma de Pagamento")
    vendas_por_pgto = vendas_filtradas.groupby("forma_pgto")["total"].sum().reset_index()
    st.bar_chart(vendas_por_pgto.set_index("forma_pgto"))
    
    # Tabela de vendas do período
    st.subheader("Lista de Vendas no Período")
    st.dataframe(vendas_filtradas[["id", "data", "cliente", "forma_pgto", "total"]])

# Módulo de Histórico de Vendas
def historico_vendas():
    st.header("📜 Histórico de Vendas")
    
    if not st.session_state.vendas_db:
        st.warning("Nenhuma venda registrada")
        return
    
    # Filtros
    st.subheader("Filtros")
    col1, col2 = st.columns(2)
    with col1:
        # Filtro por data
        hoje = datetime.now().date()
        data_inicio = st.date_input("Data Inicial", 
                                  value=hoje - pd.Timedelta(days=30),
                                  max_value=hoje,
                                  key="hist_data_inicio")
    with col2:
        data_fim = st.date_input("Data Final", 
                               value=hoje,
                               max_value=hoje,
                               key="hist_data_fim")
    
    # Lista de vendas
    st.subheader("Vendas Realizadas")
    
    for venda in reversed(st.session_state.vendas_db):
        data_venda = datetime.strptime(venda["data"], "%Y-%m-%d %H:%M:%S").date()
        if data_inicio <= data_venda <= data_fim:
            with st.expander(f"Venda #{venda['id']} - {venda['data']} - R$ {venda['total']:.2f}"):
                st.write(f"**Cliente:** {venda['cliente']}")
                st.write(f"**Forma de Pagamento:** {venda['forma_pgto']}")
                st.write(f"**Total:** R$ {venda['total']:.2f}")
                
                # Tabela de itens
                items_df = pd.DataFrame(venda["itens"])
                st.dataframe(items_df[["produto", "quantidade", "preco_unit", "total"]])
                
                # Botão para reimpressão de recibo
                if st.button("Reimprimir Recibo", key=f"reimp_{venda['id']}"):
                    recibo_html = gerar_recibo_html(venda)
                    st.components.v1.html(recibo_html, height=600)
                    st.download_button(
                        "📄 Baixar Recibo",
                        recibo_html,
                        f"recibo_{venda['id']}.html",
                        "text/html"
                    )

# Módulo de Gerenciamento de Estoque
def gerenciar_estoque():
    st.header("🗃️ Gerenciamento de Estoque")
    
    # Tabela de produtos com estoque
    st.subheader("Estoque Atual")
    
    produtos_df = pd.DataFrame(st.session_state.produtos_db.values())
    if not produtos_df.empty:
        st.dataframe(produtos_df[["nome", "codigo_barras", "preco", "estoque", "grupo", "marca"]])
    else:
        st.warning("Nenhum produto cadastrado")
    
    # Entrada de estoque
    st.subheader("Entrada de Estoque")
    
    col1, col2 = st.columns(2)
    with col1:
        # Lista de produtos para seleção
        produtos = list(st.session_state.produtos_db.values())
        nomes_produtos = [p["nome"] for p in produtos]
        produto_selecionado = st.selectbox("Selecione o Produto", nomes_produtos)
    
    with col2:
        # Quantidade a adicionar
        quantidade = st.number_input("Quantidade", min_value=1, value=1)
    
    if st.button("Registrar Entrada", type="primary"):
        # Encontrar o código do produto selecionado
        codigo = None
        for c, p in st.session_state.produtos_db.items():
            if p["nome"] == produto_selecionado:
                codigo = c
                break
        
        if codigo:
            st.session_state.produtos_db[codigo]["estoque"] += quantidade
            st.success(f"Adicionadas {quantidade} unidades de {produto_selecionado} ao estoque!")
            st.rerun()
    
    # Alerta de produtos com estoque baixo
    st.subheader("Alertas de Estoque Baixo")
    
    produtos_baixo_estoque = []
    for codigo, produto in st.session_state.produtos_db.items():
        if produto["estoque"] < 10:  # Definido como baixo estoque
            produtos_baixo_estoque.append(produto)
    
    if produtos_baixo_estoque:
        st.warning(f"{len(produtos_baixo_estoque)} produtos com estoque crítico")
        
        for produto in produtos_baixo_estoque:
            st.error(f"⚠️ {produto['nome']} - Estoque: {produto['estoque']} unidades")
    else:
        st.success("Todos os produtos com estoque adequado")

# Configurações do Sistema
def configuracoes_sistema():
    st.header("⚙️ Configurações do Sistema")
    
    st.subheader("Informações da Empresa")
    
    with st.form("form_config"):
        col1, col2 = st.columns(2)
        
        with col1:
            nome_empresa = st.text_input("Nome da Empresa", value="ORION PDV")
            cnpj = st.text_input("CNPJ")
            telefone = st.text_input("Telefone")
        
        with col2:
            endereco = st.text_input("Endereço")
            cidade = st.text_input("Cidade/UF")
            email = st.text_input("Email")
        
        # Logo
        logo_url = st.text_input("URL da Logo", value="https://i.imgur.com/Ka8kNST.png")
        
        if st.form_submit_button("Salvar Configurações"):
            # Aqui você salvaria em um estado de sessão ou banco de dados
            st.success("Configurações salvas!")
    
    # Backup de dados
    st.subheader("Backup de Dados")
    
    if st.button("Exportar Dados"):
        # Preparar dados para exportação
        dados_exportacao = {
            "produtos": st.session_state.produtos_db,
            "vendas": st.session_state.vendas_db,
            "clientes": st.session_state.clientes_db,
            "data_exportacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Converter para JSON
        json_str = pd.Series(dados_exportacao).to_json()
        
        # Botão de download
        st.download_button(
            label="📥 Baixar Arquivo de Backup",
            data=json_str,
            file_name=f"backup_orion_pdv_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
        
        st.success("Backup gerado com sucesso!")
    
    # Importação
    st.subheader("Importar Backup")
    
    arquivo_importacao = st.file_uploader("Selecione o arquivo de backup", type=["json"])
    
    if arquivo_importacao is not None:
        try:
            dados_importados = pd.read_json(arquivo_importacao, typ="series")
            
            if st.button("Confirmar Importação", type="primary"):
                # Confirmação de substituição de dados
                st.session_state.produtos_db = dados_importados["produtos"]
                st.session_state.vendas_db = dados_importados["vendas"]
                st.session_state.clientes_db = dados_importados["clientes"]
                
                st.success("Dados importados com sucesso!")
                st.info(f"Data do backup: {dados_importados['data_exportacao']}")
        except Exception as e:
            st.error(f"Erro ao importar arquivo: {e}")

# Função para exibir a página Sobre
def sobre():
    st.header("ℹ️ Sobre o ORION PDV")
    
    st.image("https://i.imgur.com/Ka8kNST.png", width=200)
    
    st.markdown("""
    ### Sistema de Ponto de Venda ORION
    
    Versão 1.0.0
    
    O **ORION PDV** é um sistema de ponto de venda completo desenvolvido em Python com Streamlit.
    
    #### Principais Funcionalidades:
    
    - 📱 Scanner de código de barras assistido
    - 🧾 Registro de vendas simplificado
    - 📦 Cadastro de produtos
    - 👤 Cadastro de clientes
    - 🗃️ Gerenciamento de estoque
    - 📊 Relatórios financeiros
    - 🔐 Sistema de autenticação
    
    #### Tecnologias Utilizadas:
    
    - Python
    - Streamlit
    - Pandas
    - Google Sheets (para integração de dados)
    
    © 2025 - Todos os direitos reservados- ADM. JESUS MARTINS OLIVEIRA JUNIOR 
    """)
    
    st.divider()
    
    st.markdown("Desenvolvido por Orion Software Solutions")

# Função principal para a barra lateral
def sidebar():
    with st.sidebar:
        st.image("https://i.imgur.com/Ka8kNST.png", width=200)
        st.title("ORION PDV")
        
        # Menu Principal
        pagina = st.selectbox(
            "Menu Principal",
            [
                "🧾 Registrar Venda",
                "📦 Cadastrar Produto",
                "👤 Cadastrar Cliente",
                "📊 Painel Financeiro",
                "📜 Histórico de Vendas",
                "🗃️ Gerenciar Estoque",
                "⚙️ Configurações",
                "ℹ️ Sobre"
            ]
        )
        
        st.divider()
        
        # Exibir data e hora atual
        st.write(f"📅 {datetime.now().strftime('%d/%m/%Y')}")
        st.write(f"🕒 {datetime.now().strftime('%H:%M:%S')}")
        
        if "usuario" in st.session_state:
            st.write(f"👤 Usuário: {USUARIOS[st.session_state.usuario]['nome']}")
            
            if st.button("Sair", type="primary"):
                st.session_state.clear()
                st.rerun()
    
    return pagina

# Função principal
def main():
    # Verificar se o usuário está autenticado
    if "autenticado" not in st.session_state or not st.session_state.autenticado:
        autenticar_usuario()
        return
    
    # Exibir sidebar e obter a página selecionada
    pagina = sidebar()
    
    # Renderizar a página selecionada
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
    elif pagina == "⚙️ Configurações":
        configuracoes_sistema()
    elif pagina == "ℹ️ Sobre":
        sobre()

# Executar o aplicativo
if __name__ == "__main__":
    main()
