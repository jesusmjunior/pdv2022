import streamlit as st
import pandas as pd
from datetime import datetime
import uuid
import hashlib
import re
from PIL import Image
import xml.etree.ElementTree as ET
from io import BytesIO
import base64

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
            'preco_custo': 4.50,
            'margem': 33.11,
            'estoque': 50,
            'unidade_medida': 'L',
            'descricao': 'Leite integral longa vida 1L',
            'localizacao': 'Prateleira A1',
            'fornecedor': 'Distribuidor Leite Bom',
            'foto': "https://www.nestleprofessional.com.br/sites/default/files/styles/np_product_detail/public/2022-09/leite-em-po-ninho-integral-lata-400g.png"
        },
        '7891910000197': {
            'nome': 'Arroz',
            'codigo_barras': '7891910000197',
            'grupo': 'Grãos',
            'marca': 'Tio João',
            'preco': 22.90,
            'preco_custo': 18.50,
            'margem': 23.78,
            'estoque': 35,
            'unidade_medida': 'pacote',
            'descricao': 'Arroz tipo 1 5kg',
            'localizacao': 'Prateleira B2',
            'fornecedor': 'Casa dos Grãos',
            'foto': "https://m.media-amazon.com/images/I/61l6ojQQtDL._AC_UF894,1000_QL80_.jpg"
        },
        '7891149410116': {
            'nome': 'Café',
            'codigo_barras': '7891149410116',
            'grupo': 'Bebidas',
            'marca': 'Pilão',
            'preco': 15.75,
            'preco_custo': 12.00,
            'margem': 31.25,
            'estoque': 28,
            'unidade_medida': 'g',
            'descricao': 'Café torrado e moído 500g',
            'localizacao': 'Prateleira C3',
            'fornecedor': 'Distribuidora de Café',
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
    numeros = re.findall(r'\d+', texto)
    codigo_extraido = ''.join(numeros)
    if len(codigo_extraido) >= 8:
        return codigo_extraido
    return None

# Função para autenticar usuário
def autenticar_usuario():
    st.title("🔐 Login - ORION ADM. JESUS MARTINS O. JR. PDV")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("https://github.com/jesusmjunior/pdv2022/blob/69ff7f9ecaa6209d10cec3ea589f803b56180c32/logo.webp", width=200)
    
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

# Função para reconhecimento de texto via OCR Web
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

# Função para instruções de scanner
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
    
    app_url = "https://pdvoliveira.streamlit.app" 
    st.markdown(f"""
    <div style="text-align: center; margin: 20px 0;">
        <p>Escaneie este QR Code para abrir o aplicativo no seu celular:</p>
        <img src="https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={app_url}" width="150">
    </div>
    """, unsafe_allow_html=True)

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

# Scanner de código de barras assistido
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
            codigo_barras = st.text_input("Digite o código de barras:", 
                                        value=st.session_state.ultimo_codigo if st.session_state.ultimo_codigo else "",
                                        placeholder="Ex: 7891000315507")
        
        with col2:
            st.image("https://www.qr-code-generator.com/wp-content/themes/qr/images/barcode-generator-free.jpg", 
                   width=150, caption="Exemplo")
    
        if st.button("Usar Código", type="primary") and codigo_barras:
            st.session_state.ultimo_codigo = codigo_barras
            st.success(f"Código registrado: {codigo_barras}")
    
    with tab2:
        codigo_texto = reconhecer_texto_imagem()
    
    codigo_selecionado = st.session_state.ultimo_codigo
    if codigo_selecionado and codigo_selecionado in st.session_state.produtos_db:
        produto = st.session_state.produtos_db[codigo_selecionado]
        st.success(f"Produto encontrado: {produto['nome']}")
        
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

# Função para processar XML de nota fiscal
def processar_xml_nfe(arquivo_xml):
    try:
        tree = ET.parse(arquivo_xml)
        root = tree.getroot()
        
        # Namespaces da NFe
        ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}
        
        produtos = []
        
        # Encontrar todos os itens da nota
        for det in root.findall('.//nfe:det', ns):
            prod = det.find('nfe:prod', ns)
            
            codigo = prod.find('nfe:cProd', ns).text if prod.find('nfe:cProd', ns) is not None else str(uuid.uuid4())[:8]
            descricao = prod.find('nfe:xProd', ns).text if prod.find('nfe:xProd', ns) is not None else "Produto sem descrição"
            quantidade = float(prod.find('nfe:qCom', ns).text) if prod.find('nfe:qCom', ns) is not None else 1
            unidade = prod.find('nfe:uCom', ns).text if prod.find('nfe:uCom', ns) is not None else "unidade"
            valor_unit = float(prod.find('nfe:vUnCom', ns).text) if prod.find('nfe:vUnCom', ns) is not None else 0.0
            
            produtos.append({
                "codigo": codigo,
                "descricao": descricao,
                "qtd": quantidade,
                "unidade": unidade,
                "valor_unit": valor_unit
            })
        
        return produtos
    except Exception as e:
        st.error(f"Erro ao processar XML: {str(e)}")
        return []

# Função para cadastro de produto
def cadastro_produto():
    st.header("📦 Cadastro de Produto")
    
    # Tabs para diferentes métodos de cadastro
    cadastro_tabs = st.tabs(["Cadastro Manual", "Importar Planilha", "Importar Nota Fiscal"])
    
    with cadastro_tabs[0]:
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
                nome = st.text_input("Nome do Produto*")
                codigo = st.text_input("Código de Barras*", 
                                    value=st.session_state.ultimo_codigo if usar_scanner and st.session_state.ultimo_codigo else "")
                grupo = st.selectbox("Grupo/Categoria*", grupos_lista)
                
                # Novo campo para unidade de medida
                unidades_medida = ["unidade", "kg", "g", "L", "ml", "pacote", "caixa", "fardo"]
                unidade_medida = st.selectbox("Unidade de Medida*", unidades_medida)
            
            with col2:
                # Adicionar campos para lógica de precificação
                modo_preco = st.radio("Modo de precificação:", ["Preço direto", "Baseado em custo"])
                
                if modo_preco == "Preço direto":
                    preco = st.number_input("Preço de Venda*", min_value=0.01, format="%.2f")
                    preco_custo = st.number_input("Preço de Custo (opcional)", min_value=0.0, format="%.2f")
                    margem = 0
                    if preco_custo > 0:
                        margem = ((preco - preco_custo) / preco_custo) * 100
                        st.info(f"Margem calculada: {margem:.2f}%")
                else:
                    preco_custo = st.number_input("Preço de Custo*", min_value=0.01, format="%.2f")
                    margem = st.slider("Margem de Lucro (%)*", min_value=0, max_value=500, value=30)
                    preco = preco_custo * (1 + margem/100)
                    st.info(f"Preço calculado: R$ {preco:.2f}")
                
                estoque = st.number_input("Estoque*", min_value=0)
                marca = st.selectbox("Marca*", marcas_lista)
            
            # Campos adicionais
            col1, col2 = st.columns(2)
            with col1:
                descricao = st.text_area("Descrição detalhada", height=100, 
                                       placeholder="Informações adicionais sobre o produto...")
            
            with col2:
                localizacao = st.text_input("Localização no Estoque", placeholder="Ex: Prateleira A3")
                fornecedor = st.text_input("Fornecedor", placeholder="Nome do fornecedor")
            
            foto_url = st.text_input("URL da Imagem")
            
            if st.form_submit_button("Salvar Produto"):
                if nome and codigo:
                    st.session_state.produtos_db[codigo] = {
                        "nome": nome,
                        "codigo_barras": codigo,
                        "grupo": grupo,
                        "marca": marca,
                        "preco": preco,
                        "preco_custo": preco_custo,
                        "margem": margem,
                        "estoque": estoque,
                        "unidade_medida": unidade_medida,
                        "descricao": descricao,
                        "localizacao": localizacao,
                        "fornecedor": fornecedor,
                        "foto": foto_url if foto_url else "https://via.placeholder.com/150"
                    }
                    st.success("Produto cadastrado!")
                    
                    # Limpar código de barras da sessão
                    if usar_scanner:
                        st.session_state.ultimo_codigo = None
                else:
                    st.error("Campos obrigatórios (*) não preenchidos")
    
    with cadastro_tabs[1]:
        st.subheader("Importar Produtos de Planilha")
        
        # Modelo de planilha para download
        st.markdown("""
        ### Instruções para importação:
        1. Baixe o modelo da planilha
        2. Preencha com os dados dos produtos
        3. Importe a planilha preenchida
        """)
        
        # Criando planilha modelo para download
        modelo_df = pd.DataFrame({
            "nome": ["Exemplo Produto"],
            "codigo_barras": ["7891000000000"],
            "grupo": ["Alimentos"],
            "marca": ["Marca Exemplo"],
            "preco_custo": [10.00],
            "margem": [30.00],
            "preco": [13.00],
            "estoque": [50],
            "unidade_medida": ["unidade"],
            "descricao": ["Descrição do produto exemplo"],
            "localizacao": ["Prateleira A1"],
            "fornecedor": ["Fornecedor Exemplo"]
        })
        
        csv = modelo_df.to_csv(index=False)
        st.download_button(
            label="📥 Baixar Modelo de Planilha",
            data=csv,
            file_name="modelo_produtos.csv",
            mime="text/csv"
        )
        
        uploaded_file = st.file_uploader("Selecione a planilha com produtos", type=["csv", "xlsx"])
        
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.csv'):
                    import_df = pd.read_csv(uploaded_file)
                else:
                    import_df = pd.read_excel(uploaded_file)
                
                st.success(f"Planilha carregada com {len(import_df)} produtos")
                st.dataframe(import_df)
                
                if st.button("Confirmar Importação", type="primary"):
                    cont_import = 0
                    for _, row in import_df.iterrows():
                        try:
                            # Garante que o código de barras seja string
                            codigo = str(row['codigo_barras'])
                            
                            # Verifica valores numéricos
                            preco = float(row.get('preco', 0))
                            preco_custo = float(row.get('preco_custo', 0))
                            margem = float(row.get('margem', 0))
                            estoque = int(row.get('estoque', 0))
                            
                            # Adiciona ao database
                            st.session_state.produtos_db[codigo] = {
                                "nome": row.get('nome', ''),
                                "codigo_barras": codigo,
                                "grupo": row.get('grupo', 'Diversos'),
                                "marca": row.get('marca', 'Outras'),
                                "preco": preco,
                                "preco_custo": preco_custo,
                                "margem": margem,
                                "estoque": estoque,
                                "unidade_medida": row.get('unidade_medida', 'unidade'),
                                "descricao": row.get('descricao', ''),
                                "localizacao": row.get('localizacao', ''),
                                "fornecedor": row.get('fornecedor', ''),
                                "foto": row.get('foto', "https://via.placeholder.com/150")
                            }
                            cont_import += 1
                        except Exception as e:
                            st.error(f"Erro ao importar linha: {e}")
                    
                    st.success(f"{cont_import} produtos importados com sucesso!")
            except Exception as e:
                st.error(f"Erro ao processar o arquivo: {e}")
    
    with cadastro_tabs[2]:
        st.subheader("Importar de Nota Fiscal")
        
        st.info("Esta função permite extrair produtos de notas fiscais eletrônicas (XML)")
        
        # Upload da nota fiscal
        uploaded_nf = st.file_uploader("Selecione o arquivo XML da Nota Fiscal", type=["xml"])
        
        if uploaded_nf is not None:
            st.success("Arquivo carregado com sucesso!")
            
            # Processar XML da NF-e
            produtos_nf = processar_xml_nfe(uploaded_nf)
            
            if not produtos_nf:
                st.error("Não foi possível extrair produtos da nota fiscal")
                return
            
            st.subheader("Produtos encontrados na nota")
            
            for produto in produtos_nf:
                with st.expander(f"{produto['descricao']} - R$ {produto['valor_unit']:.2f}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"**Código:** {produto['codigo']}")
                        st.write(f"**Quantidade:** {produto['qtd']}")
                        st.write(f"**Unidade:** {produto['unidade']}")
                    
                    with col2:
                        st.write(f"**Valor Unit.:** R$ {produto['valor_unit']:.2f}")
                        margem_nf = st.slider("Margem (%)", 0, 100, 30, key=f"margem_{produto['codigo']}")
                    
                    with col3:
                        preco_venda = produto['valor_unit'] * (1 + margem_nf/100)
                        st.write(f"**Preço Sugerido:** R$ {preco_venda:.2f}")
                        adicionar = st.checkbox("Importar", key=f"add_{produto['codigo']}")
            
            if st.button("Importar Selecionados", type="primary"):
                produtos_importados = 0
                for produto in produtos_nf:
                    if st.session_state.get(f"add_{produto['codigo']}", False):
                        codigo = produto['codigo']
                        margem = st.session_state.get(f"margem_{codigo}", 30)
                        
                        # Verifica se o produto já existe
                        if codigo in st.session_state.produtos_db:
                            # Atualiza estoque e preço se necessário
                            st.session_state.produtos_db[codigo]['estoque'] += produto['qtd']
                            st.session_state.produtos_db[codigo]['preco_custo'] = produto['valor_unit']
                            st.session_state.produtos_db[codigo]['preco'] = produto['valor_unit'] * (1 + margem/100)
                            st.session_state.produtos_db[codigo]['margem'] = margem
                        else:
                            # Adiciona novo produto
                            st.session_state.produtos_db[codigo] = {
                                "nome": produto['descricao'],
                                "codigo_barras": codigo,
                                "grupo": "Importado NF",
                                "marca": "Importado NF",
                                "preco": produto['valor_unit'] * (1 + margem/100),
                                "preco_custo": produto['valor_unit'],
                                "margem": margem,
                                "estoque": produto['qtd'],
                                "unidade_medida": produto['unidade'],
                                "descricao": f"Importado de Nota Fiscal em {datetime.now().strftime('%d/%m/%Y')}",
                                "localizacao": "",
                                "fornecedor": "Importado via NF",
                                "foto": "https://via.placeholder.com/150"
                            }
                        produtos_importados += 1
                
                if produtos_importados > 0:
                    st.success(f"{produtos_importados} produtos importados/atualizados com sucesso!")
                    st.rerun()
                else:
                    st.warning("Nenhum produto selecionado para importação")
    
    # Exibição dos produtos cadastrados
    st.subheader("Produtos Cadastrados")
    
    # Adiciona opção para exportar produtos
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("📥 Exportar Lista"):
            produtos_df = pd.DataFrame(st.session_state.produtos_db.values())
            csv = produtos_df.to_csv(index=False)
            st.download_button(
                label="Baixar CSV",
                data=csv,
                file_name=f"produtos_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                key="download_produtos"
            )
    
    # Exibir tabela de produtos
    produtos_df = pd.DataFrame(st.session_state.produtos_db.values())
    if not produtos_df.empty:
        # Adiciona filtros
        col1, col2 = st.columns(2)
        with col1:
            if 'grupo' in produtos_df.columns:
                filtro_grupo = st.multiselect("Filtrar por Grupo:", 
                                            options=["Todos"] + list(produtos_df['grupo'].unique()),
                                            default="Todos")
        with col2:
            if 'marca' in produtos_df.columns:
                filtro_marca = st.multiselect("Filtrar por Marca:", 
                                            options=["Todas"] + list(produtos_df['marca'].unique()),
                                            default="Todas")
        
        # Aplicar filtros
        df_filtrado = produtos_df.copy()
        if filtro_grupo and "Todos" not in filtro_grupo and 'grupo' in df_filtrado.columns:
            df_filtrado = df_filtrado[df_filtrado['grupo'].isin(filtro_grupo)]
        if filtro_marca and "Todas" not in filtro_marca and 'marca' in df_filtrado.columns:
            df_filtrado = df_filtrado[df_filtrado['marca'].isin(filtro_marca)]
            
        # Mostrar produtos com colunas básicas
        colunas_display = ["nome", "codigo_barras", "preco", "estoque", "unidade_medida", "marca", "grupo"]
        st.dataframe(df_filtrado[colunas_display])
    else:
        st.warning("Nenhum produto cadastrado")
        
    # Adiciona função para editar produtos existentes
    st.subheader("Editar Produto Existente")
    codigo_editar = st.text_input("Digite o código do produto para editar:")
    
    if codigo_editar in st.session_state.produtos_db:
        produto = st.session_state.produtos_db[codigo_editar]
        st.success(f"Editando: {produto['nome']}")
        
        with st.form("form_editar_produto"):
            col1, col2 = st.columns(2)
            
            with col1:
                nome = st.text_input("Nome do Produto", value=produto.get('nome', ''))
                grupo = st.selectbox("Grupo/Categoria", grupos_lista, 
                                    index=grupos_lista.index(produto.get('grupo')) if produto.get('grupo') in grupos_lista else 0)
                
                # Unidade de medida
                unidades_medida = ["unidade", "kg", "g", "L", "ml", "pacote", "caixa", "fardo"]
                unidade_medida = st.selectbox
