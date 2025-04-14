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

# Funções auxiliares
def extrair_codigo_barras(texto):
    numeros = re.findall(r'\d+', texto)
    codigo_extraido = ''.join(numeros)
    if len(codigo_extraido) >= 8:
        return codigo_extraido
    return None

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

# Módulo de Registro de Venda
def registrar_venda():
    st.header("🧾 Registrar Venda")
    
    # Opções de busca
    busca_tabs = st.tabs(["Buscar por Nome/Código", "Scanner de Código de Barras"])
    
    with busca_tabs[0]:
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

# Módulo de Cadastro de Produto
def cadastro_produto():
    st.header("📦 Cadastro de Produto")
    
    # Tabs para diferentes métodos de cadastro
    cadastro_tabs = st.tabs(["Cadastro Manual", "Importar Planilha", "Importar Nota Fiscal"])
    
    with cadastro_tabs[0]:
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
                                    value=st.session_state.ultimo_codigo if usar_scanner and st.session_state.ultimo_codigo else "")
                grupo = st.selectbox("Grupo/Categoria*", grupos_lista)
                
                unidades_medida = ["unidade", "kg", "g", "L", "ml", "pacote", "caixa", "fardo"]
                unidade_medida = st.selectbox("Unidade de Medida*", unidades_medida)
            
            with col2:
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
                    
                    if usar_scanner:
                        st.session_state.ultimo_codigo = None
                else:
                    st.error("Campos obrigatórios (*) não preenchidos")
    
    with cadastro_tabs[1]:
        st.subheader("Importar Produtos de Planilha")
        
        st.markdown("""
        ### Instruções para importação:
        1. Baixe o modelo da planilha
        2. Preencha com os dados dos produtos
        3. Importe a planilha preenchida
        """)
        
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
                            codigo = str(row['codigo_barras'])
                            
                            preco = float(row.get('preco', 0))
                            preco_custo = float(row.get('preco_custo', 0))
                            margem = float(row.get('margem', 0))
                            estoque = int(row.get('estoque', 0))
                            
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
        
        uploaded_nf = st.file_uploader("Selecione o arquivo XML da Nota Fiscal", type=["xml"])
        
        if uploaded_nf is not None:
            st.success("Arquivo carregado com sucesso!")
            
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
                        st.write(f"**Valor Unit.:** R$ {produto['valor_unit']:.2
