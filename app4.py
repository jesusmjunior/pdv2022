import streamlit as st
from datetime import datetime
import pandas as pd
import re
from PIL import Image
import base64
import io
import qrcode
import cv2
import numpy as np
from barcode import EAN13
from barcode.writer import ImageWriter
import matplotlib.pyplot as plt
import json
from weasyprint import HTML

# URLs para dados externos
URL_CLIENTE = "https://docs.google.com/spreadsheets/d/e/path_to_your_spreadsheet/cliente.csv"
URL_GRUPO = "https://docs.google.com/spreadsheets/d/e/path_to_your_spreadsheet/grupo.csv"
URL_MARCAS = "https://docs.google.com/spreadsheets/d/e/path_to_your_spreadsheet/marcas.csv"
URL_PGTO = "https://docs.google.com/spreadsheets/d/e/path_to_your_spreadsheet/pgto.csv"
URL_VENDA = "https://docs.google.com/spreadsheets/d/e/path_to_your_spreadsheet/venda.csv"

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
            'foto': "https://www.nestleprofessional.com.br/sites/default/files/styles/np_product_detail/public/2022-09/leite-em-po-ninho-integral-lata-400g.png",
            'localizacao': 'Gôndola 3 - Prateleira 2'
        },
        '7891910000197': {
            'nome': 'Arroz Branco',
            'codigo_barras': '7891910000197',
            'grupo': 'Cereais',
            'marca': 'Tio João',
            'preco': 21.90,
            'estoque': 35,
            'foto': "https://www.tiojoao.com.br/wp-content/uploads/2019/11/arroz-branco-tio-joao-1kg.png",
            'localizacao': 'Gôndola 1 - Prateleira 3'
        },
        '7892840222949': {
            'nome': 'Chocolate ao Leite',
            'codigo_barras': '7892840222949',
            'grupo': 'Doces',
            'marca': 'Nestle',
            'preco': 7.50,
            'estoque': 42,
            'foto': "https://www.nestle.com.br/site/uploads/2022/02/chocolate-ao-leite-nestle-classic-90g.png",
            'localizacao': 'Gôndola 5 - Prateleira 1'
        }
    }

if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

if 'vendas_db' not in st.session_state:
    st.session_state.vendas_db = []

if 'ultimo_codigo' not in st.session_state:
    st.session_state.ultimo_codigo = None

# Funções de Extração de Códigos
def extrair_codigo_barras(texto):
    # Extrai todos os números da string
    numeros = re.findall(r'\d+', texto)
    # Junta todos os números em uma única string
    codigo_extraido = ''.join(numeros)
    # Se tivermos um número de pelo menos 8 dígitos, considera como um código de barras válido
    if len(codigo_extraido) >= 8:
        return codigo_extraido
    return None

def extrair_qr_code(texto):
    # QR Codes podem conter outros caracteres além de números
    # Vamos considerar que um QR code tem um formato específico ou pelo menos 8 caracteres
    if len(texto.strip()) >= 8:
        return texto.strip()
    return None

def leitor_codigo_barras():
    """Função simulada para leitura de código de barras"""
    # Na implementação real, usaria bibliotecas como opencv e pyzbar
    codigo_texto = st.text_input("Digite ou escaneie o código:", key="scanner_input")
    if codigo_texto:
        return codigo_texto
    return None

def mostrar_instrucoes_scanner():
    st.markdown("""
    ### Como escanear códigos de barras ou QR codes:
    
    1. **Usando aplicativos de scanner**:
        - Instale um aplicativo de scanner de QR/código de barras no seu celular
        - Escaneie o código e copie o resultado
        - Cole o resultado no campo de texto acima
        
    2. **Usando câmera do dispositivo**:
        - Se estiver usando um dispositivo com webcam, você pode utilizar o botão "Escanear Código" 
        - Posicione o código de barras em frente à câmera
        - Aguarde a leitura automática
        
    *Nota: Para uma experiência completa, recomenda-se o uso de um scanner físico de códigos de barras conectado via USB.*
    """)

# Função para gerar recibo HTML
def gerar_recibo_html(venda):
    """Gera um recibo HTML para uma venda com layout profissional e imagens dos produtos"""
    # Obter timestamp atual
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Iniciar template HTML
    html = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Recibo de Venda - ORION PDV</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                max-width: 800px;
                margin: 0 auto;
            }}
            .header {{
                text-align: center;
                margin-bottom: 20px;
                border-bottom: 1px solid #ddd;
                padding-bottom: 10px;
            }}
            .logo {{
                font-size: 28px;
                font-weight: bold;
                color: #0066cc;
                margin-bottom: 5px;
            }}
            .info {{
                margin-bottom: 20px;
                background-color: #f9f9f9;
                padding: 15px;
                border-radius: 8px;
            }}
            .items {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
            }}
            .items th, .items td {{
                border: 1px solid #ddd;
                padding: 10px;
                text-align: left;
            }}
            .items th {{
                background-color: #f2f2f2;
            }}
            .item-img {{
                width: 50px;
                height: auto;
                vertical-align: middle;
                margin-right: 10px;
            }}
            .product-cell {{
                display: flex;
                align-items: center;
            }}
            .total {{
                text-align: right;
                font-weight: bold;
                font-size: 18px;
                margin-top: 20px;
                background-color: #f0f7ff;
                padding: 10px;
                border-radius: 8px;
            }}
            .footer {{
                margin-top: 30px;
                font-size: 12px;
                color: #666;
                text-align: center;
                border-top: 1px solid #ddd;
                padding-top: 10px;
            }}
            @media print {{
                body {{
                    padding: 0;
                    margin: 0;
                }}
                .print-button {{
                    display: none;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="logo">ORION PDV</div>
            <div>Sistema de Ponto de Venda</div>
        </div>
        <div class="info">
            <p><strong>Data:</strong> {venda['data']}</p>
            <p><strong>Cliente:</strong> {venda['cliente']}</p>
            <p><strong>Forma de Pagamento:</strong> {venda['forma_pgto']}</p>
        </div>
        <table class="items">
            <thead>
                <tr>
                    <th>Produto</th>
                    <th>Localização</th>
                    <th>Qtd</th>
                    <th>Preço Unit.</th>
                    <th>Total</th>
                </tr>
            </thead>
            <tbody>
    """
    
    # Adicionar itens ao recibo com imagens quando disponíveis
    for item in venda['itens']:
        img_html = ""
        if 'foto' in item and item['foto']:
            img_html = f'<img src="{item["foto"]}" class="item-img" alt="{item["produto"]}">'
        
        localizacao = item.get('localizacao', 'Não especificada')
        
        html += f"""
            <tr>
                <td>
                    <div class="product-cell">
                        {img_html} {item['produto']} ({item['codigo_barras']})
                    </div>
                </td>
                <td>{localizacao}</td>
                <td>{item['quantidade']}</td>
                <td>R$ {item['preco_unit']:.2f}</td>
                <td>R$ {item['total']:.2f}</td>
            </tr>
        """
    
    # Fechar tabela e adicionar total
    html += f"""
            </tbody>
        </table>
        <div class="total">
            Total: R$ {venda['total']:.2f}
        </div>
        <div class="footer">
            <p>Obrigado pela sua compra!</p>
            <p>ORION PDV - Sistema de Ponto de Venda</p>
            <p>Recibo gerado em: {timestamp}</p>
        </div>
        <div class="print-button" style="text-align: center; margin-top: 30px;">
            <button onclick="window.print()">Imprimir Recibo</button>
        </div>
    </body>
    </html>
    """
    
    return html

# Função para converter HTML para PDF
def html_to_pdf(html_content):
    """Converte conteúdo HTML para PDF"""
    try:
        pdf = HTML(string=html_content).write_pdf()
        return pdf
    except Exception as e:
        st.error(f"Erro ao gerar PDF: {e}")
        return None

# Função para buscar produtos
def buscar_produto(termo, tipo_busca='codigo'):
    """
    Busca produtos por diferentes critérios
    Parâmetros:
    - termo: Texto para busca
    - tipo_busca: 'codigo', 'nome', 'categoria', 'localizacao'
    Retorna: Lista de produtos correspondentes
    """
    resultados = []
    if not termo:
        return resultados
    
    termo = termo.lower()
    for codigo, produto in st.session_state.produtos_db.items():
        match = False
        if tipo_busca == 'codigo':
            match = termo in codigo
        elif tipo_busca == 'nome':
            match = termo in produto['nome'].lower()
        elif tipo_busca == 'categoria':
            match = termo in produto['grupo'].lower()
        elif tipo_busca == 'localizacao':
            # Verificar se o produto tem o campo 'localizacao'
            if 'localizacao' in produto and produto['localizacao']:
                match = termo in produto['localizacao'].lower()
        
        if match:
            resultados.append(produto)
    
    return resultados

# Função para exibir resultados de busca em uma interface amigável
def exibir_resultados_busca(resultados):
    """Exibe os resultados da busca em um formato visual agradável"""
    if not resultados:
        st.info("Nenhum produto encontrado.")
        return
    
    st.success(f"{len(resultados)} produto(s) encontrado(s)")
    
    # Exibir em grid
    num_colunas = 3
    colunas = st.columns(num_colunas)
    
    for i, produto in enumerate(resultados):
        col_idx = i % num_colunas
        with colunas[col_idx]:
            st.subheader(produto['nome'])
            
            # Exibir foto do produto se disponível
            if 'foto' in produto and produto['foto']:
                st.image(produto['foto'], width=150)
            
            st.write(f"**Código:** {produto['codigo_barras']}")
            st.write(f"**Preço:** R$ {produto['preco']:.2f}")
            st.write(f"**Estoque:** {produto['estoque']} unidades")
            
            # Exibir localização se disponível
            if 'localizacao' in produto and produto['localizacao']:
                st.write(f"**Localização:** {produto['localizacao']}")
            
            # Botão para adicionar ao carrinho
            qtd = st.number_input(f"Quantidade", min_value=1, value=1, key=f"qtd_{produto['codigo_barras']}")
            
            if st.button("Adicionar ao Carrinho", key=f"add_{produto['codigo_barras']}"):
                # Adicionar ao carrinho
                item = {
                    'codigo_barras': produto['codigo_barras'],
                    'produto': produto['nome'],
                    'quantidade': qtd,
                    'preco_unit': produto['preco'],
                    'total': qtd * produto['preco'],
                    'foto': produto['foto'] if 'foto' in produto else None,
                    'localizacao': produto['localizacao'] if 'localizacao' in produto else None
                }
                
                # Verificar se o produto já está no carrinho
                encontrado = False
                for j, carrinho_item in enumerate(st.session_state.carrinho):
                    if carrinho_item['codigo_barras'] == produto['codigo_barras']:
                        st.session_state.carrinho[j]['quantidade'] += qtd
                        st.session_state.carrinho[j]['total'] = st.session_state.carrinho[j]['quantidade'] * carrinho_item['preco_unit']
                        encontrado = True
                        break
                
                if not encontrado:
                    st.session_state.carrinho.append(item)
                
                st.success(f"Produto '{produto['nome']}' adicionado ao carrinho!")
                st.rerun()

# Função para renderizar a página de cadastro de produtos
def render_cadastro_produto():
    st.title("📦 Cadastro de Produto")
    
    try:
        grupo_df = pd.read_csv(URL_GRUPO)
        marcas_df = pd.read_csv(URL_MARCAS)
    except Exception as e:
        st.error(f"Erro ao carregar dados de grupo/marcas: {e}")
        # Usar listas vazias como fallback
        grupo_df = pd.DataFrame({"DESCRICAO": ["Alimentos", "Bebidas", "Limpeza", "Higiene", "Outros"]})
        marcas_df = pd.DataFrame({"DESCRICAO": ["Diversos", "Marca Própria", "Outras"]})
    
    # Abas para diferentes funções
    tab1, tab2, tab3 = st.tabs(["Adicionar Produto", "Consultar por Código", "Pesquisar Produtos"])
    
    with tab1:
        with st.form("form_cad_produto"):
            # Campos do formulário de cadastro
            codigo_barras = st.text_input("Código de Barras/QR Code", 
                                        value=st.session_state.ultimo_codigo if st.session_state.ultimo_codigo else "",
                                        placeholder="Ex: 7891000315507")
            
            # Botão para ler código de barras
            scan_barcode = st.form_submit_button("📷 Ler Código de Barras/QR", type="secondary")
            if scan_barcode:
                st.info("Clique fora do formulário e use a opção 'Scanner de Código' abaixo")
            
            nome = st.text_input("Nome do Produto")
            
            col1, col2 = st.columns(2)
            with col1:
                grupo = st.selectbox("Grupo/Categoria", grupo_df["DESCRICAO"].dropna())
            with col2:
                marca = st.selectbox("Marca", marcas_df["DESCRICAO"].dropna())
            
            col1, col2 = st.columns(2)
            with col1:
                preco = st.number_input("Preço", min_value=0.0, step=0.01, format="%.2f")
            with col2:
                estoque = st.number_input("Estoque", min_value=0)
            
            # Campo de localização no estoque
            localizacao = st.text_input("Localização na Loja", 
                                      placeholder="Ex: Gôndola 3 - Prateleira 2")
            
            foto_url = st.text_input("URL da Foto do Produto", 
                                   placeholder="https://exemplo.com/imagem.jpg")
            
            # Exibir prévia da imagem se URL for fornecida
            if foto_url:
                st.image(foto_url, caption="Prévia da imagem", width=200)
            
            enviar = st.form_submit_button("Salvar Produto")
            
            if enviar and codigo_barras and nome:
                novo_produto = {
                    'nome': nome,
                    'codigo_barras': codigo_barras,
                    'grupo': grupo,
                    'marca': marca,
                    'preco': preco,
                    'estoque': estoque,
                    'localizacao': localizacao,
                    'foto': foto_url
                }
                
                # Salvar no "banco de dados" local (session_state)
                st.session_state.produtos_db[codigo_barras] = novo_produto
                st.success(f"Produto '{nome}' cadastrado com sucesso!")
                st.json(novo_produto)
    
    with tab2:
        # Scanner de código de barras/QR fora do formulário
        st.subheader("Scanner de Código de Barras/QR")
        codigo_scaneado = leitor_codigo_barras()
        
        if codigo_scaneado:
            st.success(f"Código lido: {codigo_scaneado}")
            st.session_state.ultimo_codigo = codigo_scaneado
            
            # Verificar se o código já existe no banco de dados
            if codigo_scaneado in st.session_state.produtos_db:
                st.info("Produto já cadastrado. Detalhes:")
                st.json(st.session_state.produtos_db[codigo_scaneado])
            else:
                st.warning("Produto não encontrado. Use a aba 'Adicionar Produto' para cadastrá-lo.")
        
        # Instruções para uso com aplicativos externos
        with st.expander("Como escanear códigos com seu celular", expanded=False):
            mostrar_instrucoes_scanner()
    
    with tab3:
        # Interface de busca avançada
        st.subheader("Pesquisa Avançada de Produtos")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            termo_busca = st.text_input("Digite o termo de busca:", placeholder="Nome do produto, categoria, localização...")
        with col2:
            tipo_busca = st.selectbox("Buscar por:", ["Nome", "Categoria", "Localização"])
        
        if st.button("🔍 Pesquisar", type="primary") and termo_busca:
            # Mapear o tipo de busca selecionado
            tipo_map = {
                "Nome": "nome",
                "Categoria": "categoria",
                "Localização": "localizacao"
            }
            
            resultados = buscar_produto(termo_busca, tipo_map[tipo_busca])
            exibir_resultados_busca(resultados)
    
    # Exibir todos os produtos cadastrados
    st.subheader("Produtos Cadastrados")
    
    # Criar dataframe para visualização
    produtos_list = []
    for codigo, produto in st.session_state.produtos_db.items():
        item = {
            "Código": codigo,
            "Produto": produto['nome'],
            "Preço": f"R$ {produto['preco']:.2f}",
            "Estoque": produto['estoque']
        }
        
        # Adicionar localização se existir
        if 'localizacao' in produto and produto['localizacao']:
            item["Localização"] = produto['localizacao']
        
        produtos_list.append(item)
    
    if produtos_list:
        produtos_df = pd.DataFrame(produtos_list)
        st.dataframe(produtos_df, use_container_width=True)
    else:
        st.info("Nenhum produto cadastrado.")

# Função para renderizar a página de registro de vendas
def render_registro_venda():
    st.title("🧾 Registrar Venda")
    
    try:
        cliente_df = pd.read_csv(URL_CLIENTE)
        forma_pgto_df = pd.read_csv(URL_PGTO)
    except Exception as e:
        st.error(f"Erro ao carregar dados de venda: {e}")
        # Usar dados de fallback
        cliente_df = pd.DataFrame({"NOME": ["Cliente Final", "Cliente 1", "Cliente 2"]})
        forma_pgto_df = pd.DataFrame({"DESCRICAO": ["Dinheiro", "Cartão de Crédito", "Cartão de Débito", "PIX"]})
    
    # Inicializar carrinho de compras na sessão se não existir
    if 'carrinho' not in st.session_state:
        st.session_state.carrinho = []
    
    # Abas para diferentes métodos de adicionar produtos
    tabs = st.tabs(["Código de Barras/QR", "Busca por Nome", "Busca por Categoria", "Busca por Localização"])
    
    with tabs[0]:
        # Área de leitura de código de barras
        st.subheader("Adicionar Produto por Código")
        
        codigo_tabs = st.tabs(["Digitar Código", "Scanner"])
        codigo_usado = None
        
        with codigo_tabs[0]:
            col1, col2 = st.columns([3, 1])
            with col1:
                # Input manual
                codigo_manual = st.text_input("Digite o código de barras/QR:", 
                                            placeholder="Ex: 7891000315507",
                                            value=st.session_state.ultimo_codigo if st.session_state.ultimo_codigo else "")
                
                if st.button("✅ Usar Este Código", key="btn_usar_manual"):
                    codigo_usado = codigo_manual
                    st.session_state.ultimo_codigo = codigo_manual
            
            with col2:
                qtd = st.number_input("Quantidade", min_value=1, value=1, step=1, key="qtd_tab1")
        
        with codigo_tabs[1]:
            # Área para uso do scanner
            uploaded_file = st.file_uploader("📸 Upload da foto do código:", type=["jpg", "png", "jpeg"])
            
            if uploaded_file is not None:
                image = Image.open(uploaded_file)
                st.image(image, caption="Imagem carregada (Use OCR externo para extrair o código)", width=250)
                
                ocr_texto = st.text_area("Cole aqui o texto obtido pelo OCR:", 
                                        placeholder="Cole o texto com os números do código...",
                                        height=100)
                
                if st.button("🔍 Extrair Código", key="btn_extrair") and ocr_texto:
                    codigo_extraido = extrair_codigo_barras(ocr_texto) or extrair_qr_code(ocr_texto)
                    if codigo_extraido:
                        st.success(f"Código extraído: {codigo_extraido}")
                        st.session_state.ultimo_codigo = codigo_extraido
                        codigo_usado = codigo_extraido
                    else:
                        st.error("Não foi possível extrair um código válido do texto.")
    
    with tabs[1]:
        # Busca por nome
        st.subheader("Buscar Produto por Nome")
        
        nome_busca = st.text_input("Digite o nome do produto:", placeholder="Ex: Leite, Arroz, Café")
        
        if st.button("🔍 Buscar", key="buscar_nome") and nome_busca:
            resultados = buscar_produto(nome_busca, 'nome')
            exibir_resultados_busca(resultados)
    
    with tabs[2]:
        # Busca por categoria
        st.subheader("Buscar Produto por Categoria")
        
        try:
            grupo_df = pd.read_csv(URL_GRUPO)
            categorias = [""] + list(grupo_df["DESCRICAO"].dropna())
        except Exception as e:
            categorias = ["", "Alimentos", "Bebidas", "Limpeza", "Higiene", "Outros"]
        
        categoria_busca = st.selectbox("Selecione a categoria:", categorias)
        
        if st.button("🔍 Buscar", key="buscar_categoria") and categoria_busca:
            resultados = buscar_produto(categoria_busca.lower(), 'categoria')
            exibir_resultados_busca(resultados)
    
    with tabs[3]:
        # Busca por localização
        st.subheader("Buscar Produto por Localização")
        
        localizacao_busca = st.text_input("Digite a localização:", placeholder="Ex: Gôndola 3, Prateleira 2")
        
        if st.button("🔍 Buscar", key="buscar_local") and localizacao_busca:
            resultados = buscar_produto(localizacao_busca.lower(), 'localizacao')
            exibir_resultados_busca(resultados)
    
    # Usar o código da sessão se não tivemos um código extraído nesta iteração
    if not codigo_usado and st.session_state.ultimo_codigo:
        codigo_usado = st.session_state.ultimo_codigo
    
    # Botão para adicionar produto ao carrinho usando código
    if st.button("Adicionar ao Carrinho", type="primary") and codigo_usado:
        if codigo_usado in st.session_state.produtos_db:
            produto = st.session_state.produtos_db[codigo_usado]
            
            # Verificar se o produto já está no carrinho
            encontrado = False
            for i, item in enumerate(st.session_state.carrinho):
                if item['codigo_barras'] == codigo_usado:
                    st.session_state.carrinho[i]['quantidade'] += qtd
                    st.session_state.carrinho[i]['total'] = st.session_state.carrinho[i]['quantidade'] * item['preco_unit']
                    encontrado = True
                    break
            
            if not encontrado:
                # Adicionar novo item ao carrinho
                item = {
                    'codigo_barras': codigo_usado,
                    'produto': produto['nome'],
                    'quantidade': qtd,
                    'preco_unit': produto['preco'],
                    'total': qtd * produto['preco'],
                    'foto': produto['foto'] if 'foto' in produto else None,
                    'localizacao': produto['localizacao'] if 'localizacao' in produto else None
                }
                st.session_state.carrinho.append(item)
            
            st.success(f"Produto '{produto['nome']}' adicionado ao carrinho!")
            
            # Limpar código após adicionar ao carrinho
            st.session_state.ultimo_codigo = None
            st.rerun()
        else:
            st.error(f"Código {codigo_usado} não encontrado. Cadastre o produto primeiro.")
    
    # Exibir carrinho
    st.subheader("Carrinho de Compras")
    
    if not st.session_state.carrinho:
        st.info("Carrinho vazio. Adicione produtos usando uma das opções acima.")
    else:
        # Exibir itens do carrinho com imagens e informações de localização
        total_carrinho = 0
        
        for i, item in enumerate(st.session_state.carrinho):
            col1, col2, col3, col4 = st.columns([1, 3, 1, 1])
            
            with col1:
                if 'foto' in item and item['foto']:
                    st.image(item['foto'], width=80)
            
            with col2:
                st.write(f"**{item['produto']}**")
                st.write(f"Código: {item['codigo_barras']}")
                if 'localizacao' in item and item['localizacao']:
                    st.write(f"Localização: {item['localizacao']}")
            
            with col3:
                st.write(f"Qtd: {item['quantidade']}")
                st.write(f"R$ {item['preco_unit']:.2f}")
            
            with col4:
                st.write(f"**R$ {item['total']:.2f}**")
                if st.button("🗑", key=
