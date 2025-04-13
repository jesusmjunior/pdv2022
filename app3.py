import streamlit as st
import pandas as pd
import hashlib
from datetime import datetime
import io
from PIL import Image
import base64
import re
import streamlit.components.v1 as components

# Configuração inicial
st.set_page_config(page_title="ORION PDV", layout="wide", initial_sidebar_state="collapsed")

# URLs dos dados externos
URL_GRUPO = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0r3XE4DpzlYJjZwjc2c_pW_K3euooN9caPedtSq-nH_aEPnvx1jrcd9t0Yhg8fqXfR3j5jM2OyUQQ/pub?gid=528868130&single=true&output=csv"
URL_MARCAS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0r3XE4DpzlYJjZwjc2c_pW_K3euooN9caPedtSq-nH_aEPnvx1jrcd9t0Yhg8fqXfR3j5jM2OyUQQ/pub?gid=832596780&single=true&output=csv"
URL_CLIENTE = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0r3XE4DpzlYJjZwjc2c_pW_K3euooN9caPedtSq-nH_aEPnvx1jrcd9t0Yhg8fqXfR3j5jM2OyUQQ/pub?gid=1645177762&single=true&output=csv"
URL_PRODUTO = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0r3XE4DpzlYJjZwjc2c_pW_K3euooN9caPedtSq-nH_aEPnvx1jrcd9t0Yhg8fqXfR3j5jM2OyUQQ/pub?gid=1506891785&single=true&output=csv"
URL_PGTO = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0r3XE4DpzlYJjZwjc2c_pW_K3euooN9caPedtSq-nH_aEPnvx1jrcd9t0Yhg8fqXfR3j5jM2OyUQQ/pub?gid=1061064660&single=true&output=csv"
URL_VENDA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0r3XE4DpzlYJjZwjc2c_pW_K3euooN9caPedtSq-nH_aEPnvx1jrcd9t0Yhg8fqXfR3j5jM2OyUQQ/pub?gid=1817416820&single=true&output=csv"

# Banco de dados simulado de produtos
if 'produtos_db' not in st.session_state:
    st.session_state.produtos_db = {
        '7891000315507': {
            'nome': 'Leite Integral',
            'codigo_barras': '7891000315507',
            'grupo': 'Laticínios',
            'marca': 'Ninho',
            'preco_venda': 5.99,
            'preco_custo': 4.20,
            'margem': 30.0,
            'imposto': 12.0,
            'estoque': 50,
            'localizacao': 'Gôndola A3',
            'foto': "https://www.nestleprofessional.com.br/sites/default/files/styles/np_product_detail/public/2022-09/leite-em-po-ninho-integral-lata-400g.png",
            'foto_base64': ""
        },
        '7891910000197': {
            'nome': 'Arroz',
            'codigo_barras': '7891910000197',
            'grupo': 'Grãos',
            'marca': 'Tio João',
            'preco_venda': 22.90,
            'preco_custo': 18.50,
            'margem': 19.2,
            'imposto': 8.5,
            'estoque': 35,
            'localizacao': 'Gôndola B1',
            'foto': "https://m.media-amazon.com/images/I/61l6ojQQtDL._AC_UF894,1000_QL80_.jpg",
            'foto_base64': ""
        },
        '7891149410116': {
            'nome': 'Café',
            'codigo_barras': '7891149410116',
            'grupo': 'Bebidas',
            'marca': 'Pilão',
            'preco_venda': 15.75,
            'preco_custo': 10.80,
            'margem': 31.4,
            'imposto': 9.0,
            'estoque': 28,
            'localizacao': 'Gôndola C4',
            'foto': "https://m.media-amazon.com/images/I/51xq5MnKz4L._AC_UF894,1000_QL80_.jpg",
            'foto_base64': ""
        }
    }

# Variáveis de sessão
if 'ultimo_codigo' not in st.session_state:
    st.session_state.ultimo_codigo = None

if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

if 'ultima_venda' not in st.session_state:
    st.session_state.ultima_venda = None

# Função para extrair números de uma string (potencialmente um código de barras)
def extrair_codigo_barras(texto):
    # Extrai todos os números da string
    numeros = re.findall(r'\d+', texto)
    
    # Junta todos os números em uma única string
    codigo_extraido = ''.join(numeros)
    
    # Se tivermos um número de pelo menos 8 dígitos, considera como um código de barras válido
    if len(codigo_extraido) >= 8:
        return codigo_extraido
    
    return None

# Função para calcular margem e preço de venda
def calcular_margem_preco(preco_custo, margem, imposto=0):
    fator_markup = 1.0 + (margem / 100.0)
    fator_imposto = 1.0 + (imposto / 100.0)
    preco_venda = preco_custo * fator_markup * fator_imposto
    return round(preco_venda, 2)

# Função de reconhecimento de texto via OCR Web
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

# Função de autenticação
def autenticar_usuario():
    # Dados de autenticação
    USUARIOS = {
        "admjesus": {
            "nome": "ADM Jesus",
            "senha_hash": hashlib.sha256("senha123".encode()).hexdigest()
        }
    }
    
    st.title("🔐 Login - ORION PDV")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
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

# Função para scanner de código de barras assistido
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
            elif produto['foto_base64']:
                img_data = base64.b64decode(produto['foto_base64'])
                img = Image.open(BytesIO(img_data))
                st.image(img, width=150)
        with col2:
            st.subheader(produto['nome'])
            st.write(f"**Preço:** R$ {produto['preco_venda']:.2f}")
            st.write(f"**Localização:** {produto['localizacao']}")
            st.write(f"**Estoque:** {produto['estoque']} unidades")
    elif codigo_selecionado:
        st.warning(f"Código {codigo_selecionado} não encontrado no cadastro.")
    
    return codigo_selecionado

# Função para integração alternativa com aplicativos de scanner
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

# Função para buscar produtos por nome, grupo ou código
def buscar_produto(termo_busca, tipo_busca="codigo"):
    if not termo_busca:
        return None
    
    # Busca por código de barras (exato)
    if tipo_busca == "codigo":
        if termo_busca in st.session_state.produtos_db:
            return st.session_state.produtos_db[termo_busca]
    
    # Busca por nome (parcial)
    elif tipo_busca == "nome":
        for codigo, produto in st.session_state.produtos_db.items():
            if termo_busca.lower() in produto['nome'].lower():
                return produto
                
    # Busca por grupo (parcial)
    elif tipo_busca == "grupo":
        for codigo, produto in st.session_state.produtos_db.items():
            if termo_busca.lower() in produto['grupo'].lower():
                return produto
                
    # Busca por localização (parcial)
    elif tipo_busca == "localizacao":
        for codigo, produto in st.session_state.produtos_db.items():
            if termo_busca.lower() in produto['localizacao'].lower():
                return produto
                
    return None

# Função de cadastro de produto com suporte a código de barras e foto
def render_cadastro_produto():
    st.title("📦 Cadastro de Produto")

    try:
        grupo_df = pd.read_csv(URL_GRUPO)
        marcas_df = pd.read_csv(URL_MARCAS)
    except Exception as e:
        st.error(f"Erro ao carregar dados de grupo/marcas: {e}")
        return

    # Aba para adicionar produto via código de barras
    tab1, tab2, tab3 = st.tabs(["Adicionar Produto", "Capturar Foto", "Consultar Produtos"])
    
    with tab1:
        with st.form("form_cad_produto"):
            codigo_barras = st.text_input("Código de Barras", 
                                        value=st.session_state.ultimo_codigo if st.session_state.ultimo_codigo else "",
                                        placeholder="Ex: 7891000315507")
            
            # Botão para ler código de barras
            scan_barcode = st.form_submit_button("📷 Ler Código de Barras", type="secondary")
            if scan_barcode:
                st.info("Clique fora do formulário e use a opção 'Scanner de Código de Barras' abaixo")
                
            nome = st.text_input("Nome do Produto")
            
            col1, col2 = st.columns(2)
            with col1:
                grupo = st.selectbox("Grupo", grupo_df["DESCRICAO"].dropna())
            with col2:
                marca = st.selectbox("Marca", marcas_df["DESCRICAO"].dropna())
            
            col1, col2 = st.columns(2)
            with col1:
                localizacao = st.text_input("Localização na Gôndola", placeholder="Ex: Gôndola A3")
            with col2:
                estoque = st.number_input("Estoque", min_value=0)
            
            # Campos para preço de custo, margem e imposto
            st.subheader("Informações Financeiras")
            col1, col2, col3 = st.columns(3)
            with col1:
                preco_custo = st.number_input("Preço de Custo (R$)", min_value=0.0, step=0.01, format="%.2f")
            with col2:
                margem = st.number_input("Margem de Lucro (%)", min_value=0.0, max_value=500.0, step=0.1, format="%.1f", value=30.0)
            with col3:
                imposto = st.number_input("Imposto (%)", min_value=0.0, max_value=100.0, step=0.1, format="%.1f", value=9.0)
            
            # Calcular preço de venda automaticamente
            preco_venda = calcular_margem_preco(preco_custo, margem, imposto)
            st.success(f"Preço de Venda Calculado: R$ {preco_venda:.2f}")
            
            foto_url = st.text_input("URL da Foto do Produto", 
                                   placeholder="https://exemplo.com/imagem.jpg")
            
            # Exibir prévia da imagem se URL for fornecida
            if foto_url:
                st.image(foto_url, caption="Prévia da imagem", width=200)
                
            enviar = st.form_submit_button("Salvar Produto")
            
            if enviar and codigo_barras and nome:
                foto_base64 = ""
                if "temp_foto_base64" in st.session_state:
                    foto_base64 = st.session_state.temp_foto_base64
                    
                novo_produto = {
                    'nome': nome,
                    'codigo_barras': codigo_barras,
                    'grupo': grupo,
                    'marca': marca,
                    'preco_venda': preco_venda,
                    'preco_custo': preco_custo,
                    'margem': margem,
                    'imposto': imposto,
                    'estoque': estoque,
                    'localizacao': localizacao,
                    'foto': foto_url,
                    'foto_base64': foto_base64
                }
                
                # Salvar no "banco de dados" local (session_state)
                st.session_state.produtos_db[codigo_barras] = novo_produto
                st.success(f"Produto '{nome}' cadastrado com sucesso!")
                
                # Limpar foto temporária
                if "temp_foto_base64" in st.session_state:
                    del st.session_state.temp_foto_base64
    
    with tab2:
        st.subheader("Capturar Foto do Produto")
        img_file = st.camera_input("Tire uma foto do produto")
        
        if img_file is not None:
            image = Image.open(img_file)
            st.image(image, caption="Foto capturada", width=300)
            
            # Converter para base64
            buffered = BytesIO()
            image.save(buffered, format="JPEG")
            encoded_foto = base64.b64encode(buffered.getvalue()).decode("utf-8")
            
            # Armazenar na sessão temporariamente
            st.session_state.temp_foto_base64 = encoded_foto
            st.success("Foto capturada com sucesso! Vá para a aba 'Adicionar Produto' para completar o cadastro.")
    
    with tab3:
        # Scanner de código de barras fora do formulário
        st.subheader("Buscar Produto")
        
        col1, col2 = st.columns(2)
        with col1:
            tipo_busca = st.selectbox("Buscar por:", ["Código de Barras", "Nome", "Grupo", "Localização"])
        with col2:
            termo_busca = st.text_input("Digite o termo de busca:")
        
        if st.button("Buscar") and termo_busca:
            tipo_map = {
                "Código de Barras": "codigo", 
                "Nome": "nome", 
                "Grupo": "grupo", 
                "Localização": "localizacao"
            }
            produto = buscar_produto(termo_busca, tipo_map[tipo_busca])
            
            if produto:
                st.success(f"Produto encontrado: {produto['nome']}")
                
                col1, col2 = st.columns([1, 2])
                with col1:
                    if produto['foto']:
                        st.image(produto['foto'], width=150)
                    elif produto['foto_base64']:
                        img_data = base64.b64decode(produto['foto_base64'])
                        img = Image.open(BytesIO(img_data))
                        st.image(img, width=150)
                
                with col2:
                    st.write(f"**Código:** {produto.get('codigo_barras', '')}")
                    st.write(f"**Nome:** {produto['nome']}")
                    st.write(f"**Grupo:** {produto.get('grupo', '')}")
                    st.write(f"**Localização:** {produto.get('localizacao', '')}")
                    st.write(f"**Preço Venda:** R$ {produto.get('preco_venda', 0):.2f}")
                    st.write(f"**Estoque:** {produto.get('estoque', 0)} unidades")
                
                # Mostrar informações financeiras em uma área expansível
                with st.expander("Informações Financeiras (Somente Admin)"):
                    st.write(f"**Preço de Custo:** R$ {produto.get('preco_custo', 0):.2f}")
                    st.write(f"**Margem:** {produto.get('margem', 0):.1f}%")
                    st.write(f"**Imposto:** {produto.get('imposto', 0):.1f}%")
            else:
                st.warning(f"Nenhum produto encontrado para: {termo_busca}")
        
        # Exibir todos os produtos cadastrados
        st.subheader("Produtos Cadastrados")
        
        # Criar dataframe para visualização
        produtos_list = []
        for codigo, produto in st.session_state.produtos_db.items():
            produtos_list.append({
                "Código": codigo,
                "Produto": produto['nome'],
                "Preço": f"R$ {produto.get('preco_venda', 0):.2f}",
                "Estoque": produto.get('estoque', 0),
                "Localização": produto.get('localizacao', '')
            })
        
        if produtos_list:
            produtos_df = pd.DataFrame(produtos_list)
            st.dataframe(produtos_df, use_container_width=True)
        else:
            st.info("Nenhum produto cadastrado.")

# Função de cadastro de cliente
def render_cadastro_cliente():
    st.title("👤 Cadastro de Cliente")
    
    with st.form("form_cad_cliente"):
        nome = st.text_input("Nome do Cliente")
        documento = st.text_input("CPF/CNPJ")
        email = st.text_input("Email")
        telefone = st.text_input("Telefone")
        
        col1, col2 = st.columns(2)
        with col1:
            endereco = st.text_input("Endereço")
        with col2:
            cidade = st.text_input("Cidade")
            
        enviar = st.form_submit_button("Salvar Cliente")
        
        if enviar:
            st.success("Cliente cadastrado com sucesso!")
            st.json({
                "nome": nome,
                "documento": documento,
                "email": email,
                "telefone": telefone,
                "endereco": endereco,
                "cidade": cidade
            })

# Função para renderizar o recibo/cupom de venda em HTML
def render_cupom():
    st.title("🧾 Cupom de Venda")
    
    if not st.session_state.ultima_venda:
        st.warning("Não há venda finalizada para gerar cupom. Registre uma venda primeiro.")
        return
    
    venda = st.session_state.ultima_venda
    
    # Template HTML do cupom
    html_cupom = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Cupom Eletrônico</title>
        <style>
            body {{ font-family: monospace; }}
            .cupom {{ max-width: 300px; margin: auto; padding: 10px; border: 1px dashed #000; }}
            .center {{ text-align: center; }}
            .linha {{ border-top: 1px dashed #000; margin: 10px 0; }}
            .produto {{ margin-bottom: 8px; }}
            button {{ margin-top: 20px; padding: 5px 15px; }}
        </style>
    </head>
    <body>
        <div class="cupom">
            <div class="center">
                <h3>ORION PDV</h3>
                <p>🧾 CUPOM ELETRÔNICO</p>
                <p>Data: {venda["data"]}</p>
            </div>
            <div class="linha"></div>
            
            <h4>ITENS</h4>
    '''
    
    # Adicionar itens do carrinho
    for item in venda["itens"]:
        html_cupom += f'''
            <div class="produto">
                <div>{item["produto"]}</div>
                <div>{item["quantidade"]} x R$ {item["preco_unit"]:.2f} = R$ {item["total"]:.2f}</div>
            </div>
        '''
    
    # Finalizar cupom
    html_cupom += f'''
            <div class="linha"></div>
            <h4>TOTAL: R$ {venda["total"]:.2f}</h4>
            <p><strong>Cliente:</strong> {venda["cliente"]}</p>
            <p><strong>Pagamento:</strong> {venda["forma_pgto"]}</p>
            <div class="linha"></div>
            <p class="center">Obrigado pela preferência!</p>
        </div>
        <div class="center">
            <button onclick="window.print()">🖨️ Imprimir</button>
        </div>
    </body>
    </html>
    '''
    
    # Renderizar o cupom usando components
    components.html(html_cupom, height=600)
    
    # Opção para baixar o cupom como HTML
    st.download_button(
        label="⬇️ Baixar Cupom HTML",
        data=html_cupom,
        file_name="cupom_venda.html",
        mime="text/html"
    )

# Função de registro de venda com extração assistida de código de barras
def render_registro_venda():
    st.title("🧾 Registrar Venda")

    try:
        cliente_df = pd.read_csv(URL_CLIENTE)
        forma_pgto_df = pd.read_csv(URL_PGTO)
    except Exception as e:
        st.error(f"Erro ao carregar dados de venda: {e}")
        return
    
    # Área de leitura de código de barras
    st.subheader("Adicionar Produto")
    
    tab1, tab2, tab3 = st.tabs(["Por Código de Barras", "Por Nome/Descrição", "Por Localização"])
    
    codigo_produto = None
    quantidade = 1
    
    with tab1:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Input manual
            codigo_manual = st.text_input("Digite o código de barras:", 
                                        placeholder="Ex: 7891000315507",
                                        value=st.session_state.ultimo_codigo if st.session_state.ultimo_codigo else "")
            
            if st.button("✅ Usar Este Código", key="btn_usar_manual"):
                codigo_produto = codigo_manual
                st.session_state.ultimo_codigo = codigo_manual
        
        with col2:
            quantidade = st.number_input("Quantidade", min_value=1, value=1, step=1, key="qtd_tab1")
    
    with tab2:
