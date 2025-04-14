import streamlit as st
import pandas as pd
from datetime import datetime
import uuid
import hashlib
import re
import xml.etree.ElementTree as ET
from io import BytesIO

# Configuração da página
st.set_page_config(page_title="ORION PDV-ADM. JESUS MARTINS & ORION I.A.", layout="wide")

# URLs dos dados externos
URL_GRUPO = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0r3XE4DpzlYJjZwjc2c_pW_K3euooN9caPedtSq-nH_aEPnvx1jrcd9t0Yhg8fqXfR3j5jM2OyUQQ/pub?gid=528868130&single=true&output=csv"
URL_MARCAS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0r3XE4DpzlYJjZwjc2c_pW_K3euooN9caPedtSq-nH_aEPnvx1jrcd9t0Yhg8fqXfR3j5jM2OyUQQ/pub?gid=832596780&single=true&output=csv"
URL_CLIENTE = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0r3XE4DpzlYJjZwjc2c_pW_K3euooN9caPedtSq-nH_aEPnvx1jrcd9t0Yhg8fqXfR3j5jM2OyUQQ/pub?gid=1645177762&single=true&output=csv"
URL_PRODUTO = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0r3XE4DpzlYJjZwjc2c_pW_K3euooN9caPedtSq-nH_aEPnvx1jrcd9t0Yhg8fqXfR3j5jM2OyUQQ/pub?gid=1506891785&single=true&output=csv"
URL_PGTO = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0r3XE4DpzlYJjZwjc2c_pW_K3euooN9caPedtSq-nH_aEPnvx1jrcd9t0Yhg8fqXfR3j5jM2OyUQQ/pub?gid=1061064660&single=true&output=csv"
URL_VENDA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0r3XE4DpzlYJjZwjc2c_pW_K3euooN9caPedtSq-nH_aEPnvx1jrcd9t0Yhg8fqXfR3j5jM2OyUQQ/pub?gid=1817416820&single=true&output=csv"

# Dados de autenticação
USUARIOS = {
    "admjesus": {
        "nome": "ADM Jesus",
        "senha_hash": hashlib.sha256("senha123".encode()).hexdigest()
    }
}

# Inicialização do estado da sessão
def inicializar_sessao():
    if 'produtos_db' not in st.session_state:
        st.session_state.produtos_db = {
            '7891000315507': {
                'nome': 'Leite Integral',
                'codigo_barras': '7891000315507',
                'grupo': 'Laticínios',
                'marca': 'Ninho',
                'preco': 5.99,
                'estoque': 50,
                'foto': "https://via.placeholder.com/150"
            },
            '7891910000197': {
                'nome': 'Arroz',
                'codigo_barras': '7891910000197',
                'grupo': 'Grãos',
                'marca': 'Tio João',
                'preco': 22.90,
                'estoque': 35,
                'foto': "https://via.placeholder.com/150"
            },
            '7891149410116': {
                'nome': 'Café',
                'codigo_barras': '7891149410116',
                'grupo': 'Bebidas',
                'marca': 'Pilão',
                'preco': 15.75,
                'estoque': 28,
                'foto': "https://via.placeholder.com/150"
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

# Funções auxiliares
def extrair_codigo_barras(texto):
    numeros = re.findall(r'\d+', texto)
    codigo_extraido = ''.join(numeros)
    return codigo_extraido if len(codigo_extraido) >= 8 else None

def processar_nfe(xml_content):
    """Processa XML da NFe e retorna lista de produtos formatados"""
    try:
        root = ET.fromstring(xml_content)
        produtos = []
        ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}
        
        for det in root.findall('.//nfe:det', ns):
            prod = det.find('nfe:prod', ns)
            
            produto = {
                'nome': prod.find('nfe:xProd', ns).text[:100],
                'codigo_barras': prod.find('nfe:cProd', ns).text or str(uuid.uuid4())[:13],
                'grupo': determinar_grupo(prod.find('nfe:NCM', ns).text),
                'preco': float(prod.find('nfe:vUnCom', ns).text),
                'estoque': 0,
                'marca': extrair_marca(prod.find('nfe:xProd', ns).text),
                'foto': "https://via.placeholder.com/150"
            }
            produtos.append(produto)
        
        return produtos
    except Exception as e:
        st.error(f"Erro ao processar NFe: {str(e)}")
        return []

def determinar_grupo(ncm):
    """Determina grupo baseado no NCM"""
    ncm_prefixo = ncm[:4]
    grupos = {
        '2201': 'Bebidas',
        '2202': 'Bebidas',
        '0901': 'Cafés',
        '0902': 'Cafés',
        '1901': 'Alimentos'
    }
    return grupos.get(ncm_prefixo, 'Diversos')

def extrair_marca(nome_produto):
    """Extrai marca do nome do produto"""
    marcas = {
        'NESTLÉ': 'Nestlé',
        'PILÃO': 'Pilão',
        '3 CORAÇÕES': '3 Corações'
    }
    for marca in marcas:
        if marca in nome_produto.upper():
            return marcas[marca]
    return 'Outras'

# Módulo de Autenticação
def autenticar_usuario():
    st.title("🔐 Login - ORION ADM. JESUS MARTINS O. JR. PDV")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("https://via.placeholder.com/150", width=200)
    
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

# Módulo de Scanner
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
    
    if st.button("Extrair Código de Barras", type="primary") and ocr_texto:
        codigo_barras = extrair_codigo_barras(ocr_texto)
        if codigo_barras:
            st.success(f"Código de barras extraído: {codigo_barras}")
            st.session_state.ultimo_codigo = codigo_barras
        else:
            st.error("Não foi possível extrair um código de barras válido do texto fornecido.")
    
    return st.session_state.ultimo_codigo

def mostrar_instrucoes_scanner():
    st.markdown("""
    ### 📱 Como utilizar aplicativos de scanner
    Para escanear códigos de barras com seu celular:
    1. **Google Lens** - Aponte para o código, tire uma foto e veja os números detectados
    2. **Aplicativo de Câmera** - Muitos celulares já detectam códigos automaticamente
    3. **Aplicativos específicos** - Há vários aplicativos gratuitos para escanear códigos
    """)
    
    st.markdown(f"""
    <div style="text-align: center; margin: 20px 0;">
        <p>Escaneie este QR Code para abrir o aplicativo no seu celular:</p>
        <img src="https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://pdvoliveira.streamlit.app" width="150">
    </div>
    """, unsafe_allow_html=True)

def leitor_codigo_barras():
    st.subheader("📷 Scanner de Código de Barras")
    
    tab1, tab2 = st.tabs(["Digitar Código", "Extrair de Texto"])
    
    with tab1:
        col1, col2 = st.columns([3, 1])
        with col1:
            codigo_barras = st.text_input("Digite o código de barras:", 
                                        value=st.session_state.ultimo_codigo or "",
                                        placeholder="Ex: 7891000315507")
        with col2:
            st.image("https://via.placeholder.com/150", width=150, caption="Exemplo")
    
        if st.button("Usar Código", type="primary") and codigo_barras:
            st.session_state.ultimo_codigo = codigo_barras
            st.success(f"Código registrado: {codigo_barras}")
    
    with tab2:
        reconhecer_texto_imagem()
    
    return st.session_state.ultimo_codigo

# Módulo de Recibos
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
        <thead><tr><th>Produto</th><th>Qtd</th><th>Unit</th><th>Total</th></tr></thead>
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
    <div class="footer">
        <p>Obrigado pela preferência!</p>
        <p>Volte sempre</p>
        <p><small>Gerado em: {timestamp}</small></p>
    </div>
    </body></html>
    """
    return html

# Módulo de Vendas
def registrar_venda():
    st.header("🧾 Registrar Venda")
    
    busca_tabs = st.tabs(["Buscar por Nome/Código", "Scanner de Código de Barras"])
    
    with busca_tabs[0]:
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
                            qtd = st.number_input("Quantidade", min_value=1, max_value=produto['estoque'], value=1)
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
            try:
                clientes_df = pd.read_csv(URL_CLIENTE)
                clientes_lista = ["Consumidor Final"] + list(clientes_df["NOME"].dropna())
            except:
                clientes_lista = ["Consumidor Final"] + [c["NOME"] for c in st.session_state.clientes_db]

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

# Módulo de Produtos
def cadastro_produto():
    st.header("📦 Cadastro de Produto")
    
    tab1, tab2 = st.tabs(["Cadastro Manual", "Importar NFe"])
    
    with tab1:
        try:
            grupo_df = pd.read_csv(URL_GRUPO)
            marcas_df = pd.read_csv(URL_MARCAS)
            grupos_lista = list(grupo_df["DESCRICAO"].dropna())
            marcas_lista = list(marcas_df["DESCRICAO"].dropna())
        except:
            grupos_lista = ["Alimentos", "Bebidas", "Limpeza", "Higiene", "Diversos"]
            marcas_lista = ["Nestlé", "Unilever", "P&G", "Ambev", "Outras"]
        
        usar_scanner = st.checkbox("Usar scanner de código de barras para o código")
        
        if usar_scanner:
            st.info("Escaneie o código de barras do produto")
            codigo_barras = leitor_codigo_barras()
            if codigo_barras:
                st.success(f"Código de barras obtido: {codigo_barras}")
        
        with st.form("form_produto"):
            col1, col2 = st.columns(2)
            
            with col1:
                nome = st.text_input("Nome do Produto*")
                codigo = st.text_input("Código de Barras*", 
                                     value=st.session_state.ultimo_codigo if usar_scanner and st.session_state.ultimo_codido else "")
                grupo = st.selectbox("Grupo/Categoria*", grupos_lista)
            
            with col2:
                preco = st.number_input("Preço*", min_value=0.01, format="%.2f")
                estoque = st.number_input("Estoque*", min_value=0)
                marca = st.selectbox("Marca*", marcas_lista)
            
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
                    
                    if usar_scanner:
                        st.session_state.ultimo_codigo = None
                else:
                    st.error("Campos obrigatórios (*) não preenchidos")
    
    with tab2:
        st.subheader("Importação de Nota Fiscal Eletrônica")
        uploaded_nfe = st.file_uploader("Selecione o arquivo XML da NFe", type=["xml"])
        
        if uploaded_nfe:
            produtos_nfe = processar_nfe(uploaded_nfe.read())
            
            if produtos_nfe:
                st.success(f"{len(produtos_nfe)} produtos encontrados na NFe!")
                
                for produto in produtos_nfe:
                    with st.expander(f"Produto: {produto['nome']}"):
                        with st.form(key=f"form_{produto['codigo_barras']}"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                nome = st.text_input("Nome", value=produto['nome'])
                                codigo = st.text_input("Código de Barras", value=produto['codigo_barras'])
                                grupo = st.text_input("Grupo", value=produto['grupo'])
                            
                            with col2:
                                preco = st.number_input("Preço", value=produto['preco'], min_value=0.01)
                                estoque = st.number_input("Estoque", value=produto['estoque'], min_value=0)
                                marca = st.text_input("Marca", value=produto['marca'])
                            
                            if st.form_submit_button("Salvar Produto"):
                                st.session_state.produtos_db[codigo] = {
                                    'nome': nome,
                                    'codigo_barras': codigo,
                                    'grupo': grupo,
                                    'preco': preco,
                                    'estoque': estoque,
                                    'marca': marca,
                                    'foto': "https://via.placeholder.com/150"
                                }
                                st.success("Produto salvo!")
                                st.rerun()
            else:
                st.warning("Nenhum produto encontrado no arquivo NFe")
    
    st.subheader("Produtos Cadastrados")
    produtos_df = pd.DataFrame(st.session_state.produtos_db.values())
    st.dataframe(produtos_df[["nome", "codigo_barras", "preco", "estoque"]])

# Módulo de Clientes
def cadastro_cliente():
    st.header("👤 Cadastro de Cliente")
    
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
            st.dataframe(clientes_df)
        except:
            st.info("Nenhum cliente cadastrado")

# Módulo Financeiro
def painel_financeiro():
    st.header("📊 Painel Financeiro")
    
    try:
        venda_ext_df = pd.read_csv(URL_VENDA)
        venda_ext_df["DATA"] = pd.to_datetime(venda_ext_df["DATA"], errors="coerce")
        st.success(f"Dados externos carregados: {len(venda_ext_df)} vendas")
        vendas_combinadas = st.session_state.vendas_db.copy()
        st.info("Mostrando dados combinados: externos + locais")
    except:
        vendas_combinadas = st.session_state.vendas_db.copy()
        st.warning("Dados externos indisponíveis. Mostrando apenas vendas locais.")
    
    if not vendas_combinadas:
        st.warning("Nenhuma venda registrada")
        return
        
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
        hoje = datetime.now().date()
        data_inicio = st.date_input("Data Inicial", value=hoje - pd.Timedelta(days=30), max_value=hoje)
    with col2:
        data_fim = st.date_input("Data Final", value=hoje, max_value=hoje)
    
    mask = (vendas_df["data"].dt.date >= data_inicio) & (vendas_df["data"].dt.date <= data_fim)
    vendas_filtradas = vendas_df[mask]
    
    if len(vendas_filtradas) == 0:
        st.warning("Nenhuma venda no período selecionado")
        return
    
    # Gráficos
    st.subheader("Análise de Vendas")
    vendas_por_dia = vendas_filtradas.groupby(vendas_filtradas["data"].dt.date)["total"].sum().reset_index()
    vendas_por_dia.columns = ["data", "total"]
    st.line_chart(vendas_por_dia.set_index("data"))
    
    st.subheader("Vendas por Forma de Pagamento")
    vendas_por_pgto = vendas_filtradas.groupby("forma_pgto")["total"].sum().reset_index()
    st.bar_chart(vendas_por_pgto.set_index("forma_pgto"))
    
    st.subheader("Lista de Vendas no Período")
    st.dataframe(vendas_filtradas[["id", "data", "cliente", "forma_pgto", "total"]])

# Módulo de Histórico
def historico_vendas():
    st.header("📜 Histórico de Vendas")
    
    if not st.session_state.vendas_db:
        st.warning("Nenhuma venda registrada")
        return
    
    st.subheader("Filtros")
    col1, col2 = st.columns(2)
    with col1:
        hoje = datetime.now().date()
        data_inicio = st.date_input("Data Inicial", value=hoje - pd.Timedelta(days=30), max_value=hoje, key="hist_data_inicio")
    with col2:
        data_fim = st.date_input("Data Final", value=hoje, max_value=hoje, key="hist_data_fim")
    
    st.subheader("Vendas Realizadas")
    
    for venda in reversed(st.session_state.vendas_db):
        data_venda = datetime.strptime(venda["data"], "%Y-%m-%d %H:%M:%S").date()
        if data_inicio <= data_venda <= data_fim:
            with st.expander(f"Venda #{venda['id']} - {venda['data']} - R$ {venda['total']:.2f}"):
                st.write(f"**Cliente:** {venda['cliente']}")
                st.write(f"**Forma de Pagamento:** {venda['forma_pgto']}")
                st.write(f"**Total:** R$ {venda['total']:.2f}")
                
                items_df = pd.DataFrame(venda["itens"])
                st.dataframe(items_df[["produto", "quantidade", "preco_unit", "total"]])
                
                if st.button("Reimprimir Recibo", key=f"reimp_{venda['id']}"):
                    recibo_html = gerar_recibo_html(venda)
                    st.components.v1.html(recibo_html, height=600)
                    st.download_button(
                        "📄 Baixar Recibo",
                        recibo_html,
                        f"recibo_{venda['id']}.html",
                        "text/html"
                    )

# Módulo de Estoque
def gerenciar_estoque():
    st.header("🗃️ Gerenciamento de Estoque")
    
    st.subheader("Estoque Atual")
    produtos_df = pd.DataFrame(st.session_state.produtos_db.values())
    if not produtos_df.empty:
        st.dataframe(produtos_df[["nome", "codigo_barras", "preco", "estoque", "grupo", "marca"]])
    else:
        st.warning("Nenhum produto cadastrado")
    
    st.subheader("Entrada de Estoque")
    col1, col2 = st.columns(2)
    with col1:
        produtos = list(st.session_state.produtos_db.values())
        produto_selecionado = st.selectbox("Selecione o Produto", [p["nome"] for p in produtos])
    with col2:
        quantidade = st.number_input("Quantidade", min_value=1, value=1)
    
    if st.button("Registrar Entrada", type="primary"):
        for c, p in st.session_state.produtos_db.items():
            if p["nome"] == produto_selecionado:
                st.session_state.produtos_db[c]["estoque"] += quantidade
                st.success(f"Adicionadas {quantidade} unidades de {produto_selecionado} ao estoque!")
                st.rerun()
    
    st.subheader("Alertas de Estoque Baixo")
    produtos_baixo_estoque = [p for p in st.session_state.produtos_db.values() if p["estoque"] < 10]
    
    if
