import streamlit as st
import pandas as pd
from datetime import datetime
import re
import uuid
import hashlib
from PIL import Image
import base64
import io

# Configuração da página
st.set_page_config(page_title="ORION PDV", layout="wide", initial_sidebar_state="collapsed")

# URLs dos dados externos (do app2.py)
URL_GRUPO = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0r3XE4DpzlYJjZwjc2c_pW_K3euooN9caPedtSq-nH_aEPnvx1jrcd9t0Yhg8fqXfR3j5jM2OyUQQ/pub?gid=528868130&single=true&output=csv"
URL_MARCAS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0r3XE4DpzlYJjZwjc2c_pW_K3euooN9caPedtSq-nH_aEPnvx1jrcd9t0Yhg8fqXfR3j5jM2OyUQQ/pub?gid=832596780&single=true&output=csv"
URL_CLIENTE = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0r3XE4DpzlYJjZwjc2c_pW_K3euooN9caPedtSq-nH_aEPnvx1jrcd9t0Yhg8fqXfR3j5jM2OyUQQ/pub?gid=1645177762&single=true&output=csv"
URL_PRODUTO = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0r3XE4DpzlYJjZwjc2c_pW_K3euooN9caPedtSq-nH_aEPnvx1jrcd9t0Yhg8fqXfR3j5jM2OyUQQ/pub?gid=1506891785&single=true&output=csv"
URL_PGTO = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0r3XE4DpzlYJjZwjc2c_pW_K3euooN9caPedtSq-nH_aEPnvx1jrcd9t0Yhg8fqXfR3j5jM2OyUQQ/pub?gid=1061064660&single=true&output=csv"
URL_VENDA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0r3XE4DpzlYJjZwjc2c_pW_K3euooN9caPedtSq-nH_aEPnvx1jrcd9t0Yhg8fqXfR3j5jM2OyUQQ/pub?gid=1817416820&single=true&output=csv"

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

if 'ultimo_codigo' not in st.session_state:
    st.session_state.ultimo_codigo = None

# Função para autenticar usuário (do app2.py)
def autenticar_usuario():
    # Dados de autenticação
    USUARIOS = {
        "admjesus": {
            "nome": "ADM Jesus",
            "senha_hash": hashlib.sha256("senha123".encode()).hexdigest()
        }
    }
    
    st.title("🔐 Login - ORION PDV")
    
    # Logo centralizada
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

# Funções de utilidade
def extrair_codigo(texto):
    """Extract numeric code from text, returning None if less than 8 digits"""
    numeros = re.findall(r'\d+', texto)
    return ''.join(numeros) if len(''.join(numeros)) >= 8 else None

def gerar_recibo_html(venda):
    """Generate HTML receipt for a sale (do app5.py)"""
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
        elif tipo == "categoria" and termo in p.get("grupo", "").lower():
            resultados.append(p)
        elif tipo == "localizacao" and termo in p.get("localizacao", "").lower():
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

def mostrar_instrucoes_scanner():
    """Display instructions for using external scanner apps"""
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

def leitor_codigo_barras():
    """Barcode reader with OCR assistance"""
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
        # Reconhecimento via OCR
        ocr_texto = st.text_area("Cole aqui o texto obtido pelo OCR ou os números do código de barras",
                             placeholder="Cole aqui o texto que contém os números do código de barras...",
                             height=100)
        
        if st.button("Extrair Código de Barras", type="primary") and ocr_texto:
            codigo_barras = extrair_codigo(ocr_texto)
            
            if codigo_barras:
                st.success(f"Código de barras extraído: {codigo_barras}")
                st.session_state.ultimo_codigo = codigo_barras
            else:
                st.error("Não foi possível extrair um código de barras válido do texto fornecido.")
    
    # Se temos um código válido, verificar no banco de dados
    codigo_selecionado = st.session_state.ultimo_codigo
    if codigo_selecionado and codigo_selecionado in st.session_state.produtos_db:
        produto = st.session_state.produtos_db[codigo_selecionado]
        st.success(f"Produto encontrado: {produto['nome']}")
        
        # Exibir informações do produto
        col1, col2 = st.columns([1, 2])
        with col1:
            if produto.get('foto'):
                st.image(produto['foto'], width=150)
        with col2:
            st.subheader(produto['nome'])
            st.write(f"**Preço:** R$ {produto['preco']:.2f}")
            st.write(f"**Estoque:** {produto['estoque']} unidades")
    
    return codigo_selecionado

# Módulo: Cadastro de Produto
def render_cadastro_produto():
    """Product registration form (combination of app2 and app5)"""
    st.header("📦 Cadastro de Produto")

    try:
        grupo_df = pd.read_csv(URL_GRUPO)
        marcas_df = pd.read_csv(URL_MARCAS)
    except Exception as e:
        st.error(f"Erro ao carregar dados de grupo/marcas: {e}")
        grupo_df = pd.DataFrame({"DESCRICAO": ["Alimentos", "Bebidas", "Limpeza", "Higiene", "Outros"]})
        marcas_df = pd.DataFrame({"DESCRICAO": ["Ninho", "Pilão", "Tio João", "Ypê", "Outras"]})

    # Aba para adicionar produto via código de barras
    tab1, tab2 = st.tabs(["Adicionar Produto", "Consultar por Código de Barras"])
    
    with tab1:
        with st.form("form_cad_produto"):
            col1, col2 = st.columns(2)
            
            with col1:
                nome = st.text_input("Nome do Produto")
                codigo_barras = st.text_input("Código de Barras", 
                                            value=st.session_state.ultimo_codigo if st.session_state.ultimo_codigo else "",
                                            placeholder="Ex: 7891000315507")
                grupo = st.selectbox("Grupo/Categoria", grupo_df["DESCRICAO"].dropna())
                localizacao = st.text_input("Localização (ex: Gondola 3)")
            
            with col2:
                preco = st.number_input("Preço", min_value=0.01, step=0.01, format="%.2f")
                estoque = st.number_input("Estoque", min_value=0, step=1)
                marca = st.selectbox("Marca", marcas_df["DESCRICAO"].dropna())
                foto_url = st.text_input("URL da Foto do Produto", 
                                       placeholder="https://exemplo.com/imagem.jpg")
            
            # Exibir prévia da imagem se URL for fornecida
            if foto_url:
                st.image(foto_url, caption="Prévia da imagem", width=200)
                
            enviar = st.form_submit_button("Salvar Produto")
            
            if enviar:
                if not nome:
                    st.error("O nome do produto é obrigatório.")
                elif not codigo_barras:
                    st.error("O código do produto é obrigatório.")
                else:
                    st.session_state.produtos_db[codigo_barras] = {
                        "nome": nome,
                        "codigo_barras": codigo_barras,
                        "grupo": grupo,
                        "marca": marca,
                        "preco": preco,
                        "estoque": estoque,
                        "localizacao": localizacao,
                        "foto": foto_url
                    }
                    st.success(f"Produto '{nome}' cadastrado com sucesso!")
    
    with tab2:
        # Scanner de código de barras fora do formulário
        codigo_scaneado = leitor_codigo_barras()
        
        # Instruções para uso com aplicativos externos
        with st.expander("Como escanear códigos com seu celular", expanded=False):
            mostrar_instrucoes_scanner()
    
    # Exibir todos os produtos cadastrados
    st.subheader("Produtos Cadastrados")
    
    if st.session_state.produtos_db:
        produtos_df = pd.DataFrame(st.session_state.produtos_db.values())
        st.dataframe(produtos_df[["nome", "codigo_barras", "preco", "estoque", "grupo"]])
    else:
        st.info("Nenhum produto cadastrado.")
    
    # Interface de busca
    st.subheader("Buscar Produtos")
    col1, col2 = st.columns(2)
    termo_busca = col1.text_input("Termo de Busca")
    tipo_busca = col2.selectbox("Buscar por", ["nome", "categoria", "localizacao"])
    
    if st.button("Buscar") and termo_busca:
        resultados = buscar_produto(termo_busca, tipo_busca)
        exibir_resultados_busca(resultados)

# Módulo: Cadastro de Cliente
def render_cadastro_cliente():
    """Customer registration form"""
    st.header("👤 Cadastro de Cliente")
    
    try:
        # Tentar carregar clientes existentes
        clientes_df = pd.read_csv(URL_CLIENTE)
        st.info(f"Dados externos carregados: {len(clientes_df)} clientes encontrados.")
    except Exception as e:
        st.warning(f"Não foi possível carregar dados externos. Usando apenas dados locais.")
        clientes_df = pd.DataFrame(columns=["ID", "NOME", "DOCUMENTO", "EMAIL", "TELEFONE"])
    
    with st.form("form_cad_cliente"):
        col1, col2 = st.columns(2)
        
        with col1:
            nome = st.text_input("Nome do Cliente")
            documento = st.text_input("CPF/CNPJ")
            email = st.text_input("Email")
        
        with col2:
            telefone = st.text_input("Telefone")
            endereco = st.text_input("Endereço")
            cidade = st.text_input("Cidade")
            
        enviar = st.form_submit_button("Salvar Cliente")
        
        if enviar:
            if not nome:
                st.error("O nome do cliente é obrigatório.")
            else:
                novo_cliente = {
                    "ID": str(uuid.uuid4())[:8],
                    "NOME": nome,
                    "DOCUMENTO": documento,
                    "EMAIL": email,
                    "TELEFONE": telefone,
                    "ENDERECO": endereco,
                    "CIDADE": cidade
                }
                
                st.success(f"Cliente '{nome}' cadastrado com sucesso!")
                st.json(novo_cliente)
    
    # Exibir clientes cadastrados
    if not clientes_df.empty:
        st.subheader("Clientes Cadastrados")
        st.dataframe(clientes_df)

# Módulo: Registro de Venda (combinando app2 e app5)
def render_registro_venda():
    """Sales registration interface with HTML receipt generation"""
    st.header("🧾 Registrar Venda")

    try:
        cliente_df = pd.read_csv(URL_CLIENTE)
        forma_pgto_df = pd.read_csv(URL_PGTO)
    except Exception as e:
        st.warning(f"Não foi possível carregar dados externos: {e}")
        cliente_
