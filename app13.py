import streamlit as st
import pandas as pd
import numpy as np
import re
import io
import uuid
import hashlib
from datetime import datetime
import pytesseract
from PIL import Image
import pdfplumber
import cv2
import json

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

# Configurações do Google OCR (do arquivo JSON)
GOOGLE_OCR_CONFIG = {
    "type": "service_account",
    "project_id": "zeta-bonbon-424022-b5",
    "private_key_id": "691a49c9946f853ce413eacbeefc2c0b0e4b0207",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC6hEdK2mxYW09i\nK0oF2AMrOCK5wYS03Huw/JixtgCVzFywK2fhrSDD+dXJX8+n4xa4Yl3/ELs2mEEI\n+bC5g+ey0cdqD4Ik4DFmN4eUMP3xUC7zUVF1wAQyTuRfcmUAkfyOHl5W5W7F4sJ5\nLM3aTmWS1hinaj+IHgvoc50XD3nALDZeBee5jogbDLHmcjkuEJWmfDBpX+CQL/B0\nWtucK4xO2cfDBvuNDjfyMQU//zDj5fs6nzNfXRC1z8PfKfp5yOr5BksuFdwmA29X\nPKjwhuZSAceSzZ+vFtJW949NYOP9qQDa0x7chSuDHLdJl9NyjAT/gxEmher8awwv\ng+kxB19DAgMBAAECggEACJRGDTjfy+6jR6IzHPKzLp0956pxlrofjGQKB/6Vp05H\noyjT9er3O1x2C3W3QQMui9umdDGKUvgM4cNOcDITicOhdwzwkQ6o5wk92MCqJZvp\nFPMUGqTy7Hd5hLRn1e9hHQ5ji36xKjQEevtnGpgJjwf/CVBXTMUJCi+rNaDWGlM6\nHNwkMg0Ra5zlJA2UxOLlpYhcr2PZR23jsmL1942DXQxifJvKmO2E20iKGZ/u08ew\nPC+Gvd64XTqkiWvLayOw+dU3XfzGWboPaNd3u75+fFWSUVZwMLS1RVogbzLrwHd2\ne7Ebd56H4k+2uqpL5MYcnIyu3EfNGS1HUT+e/wjSEQKBgQDunT+I8Tl4CJ3NgU9/\nLiKk40sxJ5Zm3pcqAmu0SAvwt5wNOJuTokg8RAs5E7bRe1/RAB1ZB+gwrKWS4C3s\nJl1a6m3iEvBy+nlEPWOBT3jLTOvgNavSUNDUVQW+2soNwfiPsNBCkCPnADzqi18Y\n6biOcuASiakk3NSCId3ttjKw0wKBgQDIG0f1NQLcIFVvrEg8MHLiap2462AHfceO\nlbc+jcmsRd0rG0Y8FAk3x60BMYCuPbi8OL5+dsD9FW+CImloZGU55pSScjj08/cc\n4n0tTQwMQgNK8Y40MpbXPDXbCQrYfkAixGStnS8psGJzPp9wF/aLxDGWdTtuRcV1\nq2XYRB0R0QKBgQCRa+pdxk309qNdrHJLm01n2lJoGa1S8lOEOcd0Lvh/8xa7BAXk\n+uE1QW7pkTc5AgzKLly0dtouV/nswo2aP2Nj1j2zq0E5gadITHWJSGrg0/dpRKx7\n1979mPeQcnzz14Rp5iN2fawzy3RUqS4C2+Yrgp1HDvizy5YD3SoJBqJsGwKBgCt6\nwgflnNl3rRi2tntdi5jm0Z58hkEac2Hn5gkRheCIzaWwJ3KmZ9pW6KB5wRwbDSjY\nq4uPAh/7qF7+Wyjzp4sNLvsjFn0jBW6hR9GwDA4dydle4yc0VtItowYU0OZ5iDYF\ntlqC7NyCFuIzmTEiA9AasSugDWnIfz8yHs7+/dIBAoGAFqiRDSxb2Sza5DKEq9WF\nbaz8pKe6DJfJNHzJMnR5YvQtH6DL72MxCv5KTAEIuW8DJC9gUW8RQbG6M3Fa1SPf\npiBH0Sx4M2w/X8Yu1ODUZbxdetkEy4jngNuLwCP57xODl8cF9BBRGJ+6m52moVvp\nMVBNyj2qkuxjydNmuxceerg=\n-----END PRIVATE KEY-----\n",
    "client_email": "ocr-orion-app@zeta-bonbon-424022-b5.iam.gserviceaccount.com",
    "client_id": "113225223604970206908",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/ocr-orion-app%40zeta-bonbon-424022-b5.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
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
            'margem_lucro': 30.0,
            'estoque': 50,
            'foto': "https://www.nestleprofessional.com.br/sites/default/files/styles/np_product_detail/public/2022-09/leite-em-po-ninho-integral-lata-400g.png"
        },
        '7891910000197': {
            'nome': 'Arroz',
            'codigo_barras': '7891910000197',
            'grupo': 'Grãos',
            'marca': 'Tio João',
            'preco': 22.90,
            'preco_custo': 17.50,
            'margem_lucro': 30.0,
            'estoque': 35,
            'foto': "https://m.media-amazon.com/images/I/61l6ojQQtDL._AC_UF894,1000_QL80_.jpg"
        },
        '7891149410116': {
            'nome': 'Café',
            'codigo_barras': '7891149410116',
            'grupo': 'Bebidas',
            'marca': 'Pilão',
            'preco': 15.75,
            'preco_custo': 12.00,
            'margem_lucro': 30.0,
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

# Funções auxiliares
def extrair_codigo_barras(texto):
    numeros = re.findall(r'\d+', texto)
    codigo_extraido = ''.join(numeros)
    if len(codigo_extraido) >= 8:
        return codigo_extraido
    return None

# Função para extrair texto de imagens de nota fiscal
def extrair_texto_de_imagem(imagem):
    if isinstance(imagem, np.ndarray) and len(imagem.shape) > 2:
        imagem = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)

    _, imagem = cv2.threshold(imagem, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    texto = pytesseract.image_to_string(imagem, lang='por')
    return texto

# Função para extrair texto de arquivos PDF
def extrair_texto_de_pdf(pdf_file):
    texto_completo = ""
    with pdfplumber.open(pdf_file) as pdf:
        for pagina in pdf.pages:
            texto_completo += pagina.extract_text() or ""
    return texto_completo

# Função para analisar notas fiscais eletrônicas (DANFE)
def analisar_danfe(texto):
    produtos = []
    linhas_produto = re.findall(r"\d+\s+\d+\)?\s+((\w+\s?)+)\s+\d+\s+\w+\s+(\d+)\s+([\d,]+)\s+([\d,]+)", texto)

    for match in linhas_produto:
        descricao = match[0].strip()
        quantidade = int(match[2])
        valor_unitario = float(match[3].replace('.', '').replace(',', '.'))
        valor_total = float(match[4].replace('.', '').replace(',', '.'))
        
        codigo_barras = re.search(r'CÓD\s*BARRAS[:\s]*(\d+)', texto)
        codigo = codigo_barras.group(1) if codigo_barras else "SEM_CODIGO"

        produtos.append({
            "descricao": descricao,
            "quantidade": quantidade,
            "valor_unitario": valor_unitario,
            "valor_total": valor_total,
            "codigo_barras": codigo
        })

    return produtos

# Função para analisar cupons fiscais
def analisar_cupom_fiscal(texto):
    produtos = []
    linhas_produto = re.findall(r'(\d{3})\s+(\d+)\s+(.+?)\s+(\d+)UN\s*X\s*(\d+,\d+)', texto)
    
    if not linhas_produto:
        linhas_produto = re.findall(r'(\d+)\s+(.+?)\s+(\d+)xX\s*(\d+,\d+)', texto)

    for match in linhas_produto:
        if len(match) >= 4:
            if len(match) == 5:
                item_num = match[0]
                codigo = match[1]
                descricao = match[2].strip()
                quantidade = int(match[3])
                valor_unitario = float(match[4].replace(',', '.'))
            else:
                item_num = match[0]
                descricao = match[1].strip()
                quantidade = int(match[2])
                valor_unitario = float(match[3].replace(',', '.'))
                codigo = "SEM_CODIGO"

            valor_total = quantidade * valor_unitario

            produtos.append({
                "descricao": descricao,
                "quantidade": quantidade,
                "valor_unitario": valor_unitario,
                "valor_total": valor_total,
                "codigo_barras": codigo
            })

    return produtos

# Função para importar produtos para o banco de dados
def importar_para_banco_dados(produtos, margem_lucro):
    for produto in produtos:
        codigo_barras = produto["codigo_barras"]

        if codigo_barras != "SEM_CODIGO" and codigo_barras in st.session_state.produtos_db:
            st.session_state.produtos_db[codigo_barras]["estoque"] += produto["quantidade"]
        else:
            if codigo_barras == "SEM_CODIGO":
                codigo_barras = str(uuid.uuid4())[:13]

            preco_venda = produto["valor_unitario"] * (1 + margem_lucro/100)

            st.session_state.produtos_db[codigo_barras] = {
                "nome": produto["descricao"],
                "codigo_barras": codigo_barras,
                "grupo": "Importado",
                "marca": "Importado",
                "preco": round(preco_venda, 2),
                "preco_custo": produto["valor_unitario"],
                "margem_lucro": margem_lucro,
                "estoque": produto["quantidade"],
                "foto": "https://via.placeholder.com/150"
            }

    return len(produtos)

# Módulo de importação de notas fiscais
def importar_nota_fiscal():
    st.header("📄 Importação de Notas Fiscais e Cupons")

    st.markdown("""
    <div style="padding: 15px; border: 1px solid #4CAF50; border-radius: 5px; margin-bottom: 20px; background-color: #f8f9fa;">
        <h4 style="color: #2E7D32;">Como importar notas fiscais:</h4>
        <ol>
            <li>Faça upload de uma imagem de cupom fiscal ou nota fiscal (DANFE)</li>
            <li>O sistema extrairá automaticamente os produtos e valores</li>
            <li>Defina a margem de lucro para calcular o preço de venda</li>
            <li>Confirme a importação para adicionar os produtos ao estoque</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

    opcao_upload = st.radio(
        "Selecione o tipo de documento:",
        ["PDF (DANFE)", "Imagem de Cupom Fiscal", "Imagem de Nota Fiscal"]
    )

    arquivo_upload = None
    texto_extraido = ""

    if opcao_upload == "PDF (DANFE)":
        arquivo_upload = st.file_uploader("Faça upload do PDF da nota fiscal", type=["pdf"])
        if arquivo_upload:
            with st.spinner("Processando o PDF..."):
                texto_extraido = extrair_texto_de_pdf(arquivo_upload)
    else:
        arquivo_upload = st.file_uploader("Faça upload da imagem", type=["jpg", "jpeg", "png"])
        if arquivo_upload:
            with st.spinner("Processando a imagem..."):
                img = Image.open(arquivo_upload)
                img_np = np.array(img)
                texto_extraido = extrair_texto_de_imagem(img_np)

    if arquivo_upload:
        with st.expander("Ver texto extraído"):
            st.text(texto_extraido)

        produtos = []
        if opcao_upload == "PDF (DANFE)" or opcao_upload == "Imagem de Nota Fiscal":
            produtos = analisar_danfe(texto_extraido)
        else:
            produtos = analisar_cupom_fiscal(texto_extraido)

        if produtos:
            st.success(f"Identificados {len(produtos)} produtos no documento")
            produtos_df = pd.DataFrame(produtos)
            st.dataframe(produtos_df)

            col1, col2 = st.columns([1, 1])
            with col1:
                margem_lucro = st.number_input("Margem de lucro (%)",
                    min_value=0.0,
                    max_value=500.0,
                    value=30.0,
                    step=5.0)

            with col2:
                preco_exemplo = produtos[0]["valor_unitario"] * (1 + margem_lucro/100) if produtos else 0
                st.info(f"Exemplo: Um produto de custo R$ {produtos[0]['valor_unitario']:.2f} será vendido por R$ {preco_exemplo:.2f}")

            if st.button("Importar Produtos", type="primary"):
                num_importados = importar_para_banco_dados(produtos, margem_lucro)
                st.success(f"Importados {num_importados} produtos com sucesso!")

                st.subheader("Produtos no Sistema:")
                produtos_atuais_df = pd.DataFrame(st.session_state.produtos_db.values())
                st.dataframe(produtos_atuais_df[["nome", "codigo_barras", "preco", "preco_custo", "margem_lucro", "estoque"]])
        else:
            st.error("Não foi possível identificar produtos no documento. Tente melhorar a qualidade da imagem ou verificar se o formato está correto.")

    with st.expander("Dicas para melhor reconhecimento"):
        st.markdown("""
        ### Dicas para melhorar o reconhecimento de documentos:

        1. **Para cupons fiscais:**
           - Certifique-se de que a imagem está nítida e bem iluminada
           - Evite reflexos ou sombras
           - Alinhe o cupom para que o texto esteja reto

        2. **Para notas fiscais (DANFE):**
           - Preferencialmente faça upload do PDF original
           - Se for imagem, certifique-se que está em alta resolução
           - Inclua a seção de produtos completa

        3. **Problemas comuns:**
           - Se a importação não detectar produtos, verifique o texto extraído
           - Tente recortar a imagem para mostrar apenas a parte dos itens
           - Algumas notas/cupons podem ter formatos específicos não reconhecidos automaticamente
        """)

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

# Módulo de Registro de Venda
def registrar_venda():
    st.header("🧾 Registrar Venda")
    
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
            
            quantidade = st.number_input(
                "Quantidade",
                min_value=1,
                max_value=produto['estoque'],
                value=1
            )
            
            if st.button("Adicionar ao Carrinho", type="primary"):
                item_existente = next((item for item in st.session_state.carrinho 
                                     if item['codigo_barras'] == codigo_barras), None)
                
                if item_existente:
                    item_existente['quantidade'] += quantidade
                    item_existente['total'] = item_existente['quantidade'] * item_existente['preco_unit']
                else:
                    st.session_state.carrinho.append({
                        "codigo_barras": codigo_barras,
                        "produto": produto['nome'],
                        "quantidade": quantidade,
                        "preco_unit": produto['preco'],
                        "total": quantidade * produto['preco'],
                        "foto": produto['foto']
                    })
                
                st.session_state.produtos_db[codigo_barras]['estoque'] -= quantidade
                st.success(f"Adicionado {quantidade}x {produto['nome']} ao carrinho!")
                st.rerun()
    
    # Mostrar carrinho
    st.header("🛒 Carrinho de Compras")
    
    if not st.session_state.carrinho:
        st.info("Seu carrinho está vazio. Adicione produtos para continuar.")
    else:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            for i, item in enumerate(st.session_state.carrinho):
                with st.container():
                    cols = st.columns([1, 3, 1, 1, 1])
                    with cols[0]:
                        st.image(item['foto'], width=50)
                    with cols[1]:
                        st.write(f"**{item['produto']}**")
                    with cols[2]:
                        st.write(f"{item['quantidade']} x R$ {item['preco_unit']:.2f}")
                    with cols[3]:
                        st.write(f"R$ {item['total']:.2f}")
                    with cols[4]:
                        if st.button("🗑️", key=f"remove_{i}"):
                            # Devolver ao estoque
                            st.session_state.produtos_db[item['codigo_barras']]['estoque'] += item['quantidade']
                            # Remover do carrinho
                            st.session_state.carrinho.pop(i)
                            st.rerun()
                st.divider()
        
        with col2:
            total_venda = sum(item['total'] for item in st.session_state.carrinho)
            st.metric("Total da Venda", f"R$ {total_venda:.2f}")
            
            opcoes_pgto = ["Dinheiro", "Cartão de Crédito", "Cartão de Débito", "PIX", "Crediário"]
            forma_pgto = st.selectbox("Forma de Pagamento", opcoes_pgto)
            
            clientes = ["Consumidor Final"] + [cliente["nome"] for cliente in st.session_state.clientes_db]
            cliente_selecionado = st.selectbox("Cliente", clientes)
            
            if st.button("Finalizar Venda", type="primary"):
                if not st.session_state.carrinho:
                    st.error("Não é possível finalizar venda sem produtos.")
                else:
                    # Gerar ID para a venda
                    venda_id = str(uuid.uuid4())[:8].upper()
                    
                    # Registrar a venda
                    nova_venda = {
                        "id": venda_id,
                        "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "cliente": cliente_selecionado,
                        "forma_pgto": forma_pgto,
                        "itens": [
                            {
                                "produto": item["produto"],
                                "quantidade": item["quantidade"],
                                "preco_unit": item["preco_unit"],
                                "total": item["total"]
                            } for item in st.session_state.carrinho
                        ],
                        "total": total_venda
                    }
                    
                    st.session_state.vendas_db.append(nova_venda)
                    
                    # Gerar recibo
                    recibo_html = gerar_recibo_html(nova_venda)
                    
                    # Limpar carrinho
                    st.session_state.carrinho = []
                    
                    # Mostrar confirmação
                    st.success(f"Venda {venda_id} registrada com sucesso!")
                    
                    # Botão para imprimir recibo
                    st.markdown(f"""
                        <a href="data:text/html;charset=utf-8,{recibo_html}" 
                           download="recibo_{venda_id}.html" 
                           target="_blank" 
                           style="text-decoration:none;">
                            <button style="
                                background-color: #4CAF50;
                                color: white;
                                padding: 10px 24px;
                                border: none;
                                border-radius: 4px;
                                cursor: pointer;
                                font-size: 16px;">
                                📄 Imprimir Recibo
                            </button>
                        </a>
                    """, unsafe_allow_html=True)
                    
                    # Mostrar detalhes da venda
                    with st.expander("Detalhes da Venda"):
                        st.json(nova_venda)

# Módulo de Cadastro de Produtos
def cadastrar_produto():
    st.header("📦 Cadastro de Produtos")
    
    # Carregar dados de grupos e marcas
    try:
        grupos_df = pd.read_csv(URL_GRUPO)
        grupos = grupos_df["nome"].tolist()
    except:
        grupos = ["Alimentos", "Bebidas", "Limpeza", "Higiene", "Outros"]

    try:
        marcas_df = pd.read_csv(URL_MARCAS)
        marcas = marcas_df["nome"].tolist()
    except:
        marcas = ["Diversos", "Importado", "Nacional", "Própria"]
    
    # Tabs para listar e cadastrar
    tab1, tab2 = st.tabs(["Listar Produtos", "Cadastrar Novo"])
    
    with tab1:
        st.subheader("Produtos Cadastrados")
        
        # Filtros
        col1, col2 = st.columns(2)
        with col1:
            filtro_grupo = st.selectbox("Filtrar por Grupo", ["Todos"] + grupos)
        with col2:
            termo_busca = st.text_input("Buscar por Nome ou Código")
        
        # Converter dicionário em DataFrame
        produtos_df = pd.DataFrame(st.session_state.produtos_db.values())
        
        # Aplicar filtros
        if filtro_grupo != "Todos":
            produtos_df = produtos_df[produtos_df["grupo"] == filtro_grupo]
        
        if termo_busca:
            produtos_df = produtos_df[
                (produtos_df["nome"].str.contains(termo_busca, case=False)) | 
                (produtos_df["codigo_barras"].str.contains(termo_busca, case=False))
            ]
        
        # Exibir produtos
        if not produtos_df.empty:
            for i, (_, produto) in enumerate(produtos_df.iterrows()):
                with st.container():
                    col1, col2, col3 = st.columns([1, 3, 1])
                    
                    with col1:
                        st.image(produto['foto'], width=100)
                    
                    with col2:
                        st.subheader(produto['nome'])
                        st.write(f"**Código:** {produto['codigo_barras']}")
                        st.write(f"**Grupo:** {produto['grupo']} | **Marca:** {produto['marca']}")
                        st.write(f"**Preço:** R$ {produto['preco']:.2f} | **Estoque:** {produto['estoque']} unidades")
                    
                    with col3:
                        # Botões de ação
                        st.button("✏️ Editar", key=f"edit_{i}")
                        st.button("🗑️ Excluir", key=f"del_{i}")
                
                st.divider()
        else:
            st.info("Nenhum produto encontrado com os filtros selecionados.")
    
    with tab2:
        st.subheader("Cadastrar Novo Produto")
        
        with st.form("form_cadastro_produto"):
            col1, col2 = st.columns(2)
            
            with col1:
                nome = st.text_input("Nome do Produto*", placeholder="Ex: Arroz Integral 1kg")
                codigo_barras = st.text_input("Código de Barras*", placeholder="Ex: 7891000315507")
                grupo = st.selectbox("Grupo*", grupos)
                marca = st.selectbox("Marca*", marcas)
            
            with col2:
                preco = st.number_input("Preço de Venda* (R$)", min_value=0.01, step=0.50, format="%.2f")
                preco_custo = st.number_input("Preço de Custo (R$)", min_value=0.01, step=0.50, format="%.2f")
                estoque = st.number_input("Estoque Inicial*", min_value=0, step=1)
                foto_url = st.text_input("URL da Foto", placeholder="https://exemplo.com/imagem.jpg", 
                                       value="https://via.placeholder.com/150")
            
            submeter = st.form_submit_button("Cadastrar Produto", type="primary")
            
            if submeter:
                if not nome or not codigo_barras or not grupo or not marca or preco <= 0:
                    st.error("Por favor, preencha todos os campos obrigatórios.")
                elif codigo_barras in st.session_state.produtos_db:
                    st.error(f"Código de barras {codigo_barras} já existe no cadastro.")
                else:
                    # Calcular margem de lucro
                    if preco_custo > 0:
                        margem_lucro = ((preco - preco_custo) / preco_custo) * 100
                    else:
                        margem_lucro = 0
                    
                    # Adicionar ao banco de dados
                    st.session_state.produtos_db[codigo_barras] = {
                        "nome": nome,
                        "codigo_barras": codigo_barras,
                        "grupo": grupo,
                        "marca": marca,
                        "preco": preco,
                        "preco_custo": preco_custo,
                        "margem_lucro": margem_lucro,
                        "estoque": estoque,
                        "foto": foto_url
                    }
                    
                    st.success(f"Produto '{nome}' cadastrado com sucesso!")

# Módulo de cadastro de clientes
def cadastrar_cliente():
    st.header("👥 Cadastro de Clientes")
    
    tab1, tab2 = st.tabs(["Listar Clientes", "Novo Cliente"])
    
    with tab1:
        st.subheader("Clientes Cadastrados")
        
        # Carregar clientes (tentar da planilha, senão usar da sessão)
        try:
            clientes_df = pd.read_csv(URL_CLIENTE)
        except:
            if st.session_state.clientes_db:
                clientes_df = pd.DataFrame(st.session_state.clientes_db)
            else:
                st.info("Nenhum cliente cadastrado.")
                clientes_df = pd.DataFrame()
        
        if not clientes_df.empty:
            busca = st.text_input("Buscar cliente por nome ou telefone:")
            
            if busca:
                clientes_filtrados = clientes_df[
                    (clientes_df["nome"].str.contains(busca, case=False)) | 
                    (clientes_df["telefone"].str.contains(busca, case=False))
                ]
            else:
                clientes_filtrados = clientes_df
            
            for _, cliente in clientes_filtrados.iterrows():
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.subheader(cliente["nome"])
                        st.write(f"📱 **Telefone:** {cliente['telefone']}")
                        st.write(f"📧 **Email:** {cliente.get('email', 'Não informado')}")
                        st.write(f"📍 **Endereço:** {cliente.get('endereco', 'Não informado')}")
                    
                    with col2:
                        st.button("✏️ Editar", key=f"edit_cliente_{cliente['id']}")
                        st.button("🔍 Ver Histórico", key=f"hist_cliente_{cliente['id']}")
                
                st.divider()
    
    with tab2:
        st.subheader("Cadastrar Novo Cliente")
        
        with st.form("form_cadastro_cliente"):
            nome = st.text_input("Nome Completo*")
            
            col1, col2 = st.columns(2)
            with col1:
                telefone = st.text_input("Telefone*", placeholder="(99) 99999-9999")
                endereco = st.text_input("Endereço")
            
            with col2:
                email = st.text_input("E-mail")
                doc = st.text_input("CPF/CNPJ")
            
            observacoes = st.text_area("Observações", height=100)
            
            submeter = st.form_submit_button("Cadastrar Cliente", type="primary")
            
            if submeter:
                if not nome or not telefone:
                    st.error("Nome e telefone são campos obrigatórios.")
                else:
                    # Gerar ID único
                    cliente_id = str(uuid.uuid4())[:8]
                    
                    # Adicionar ao banco de dados
                    novo_cliente = {
                        "id": cliente_id,
                        "nome": nome,
                        "telefone": telefone,
                        "email": email,
                        "endereco": endereco,
                        "documento": doc,
                        "observacoes": observacoes,
                        "data_cadastro": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    st.session_state.clientes_db.append(novo_cliente)
                    st.success(f"Cliente '{nome}' cadastrado com sucesso!")

# Módulo de relatórios
def gerar_relatorios():
    st.header("📊 Relatórios")
    
    tab1, tab2, tab3 = st.tabs(["Vendas", "Estoque", "Financeiro"])
    
    with tab1:
        st.subheader("Relatório de Vendas")
        
        # Converter vendas em DataFrame
        vendas_df = pd.DataFrame(st.session_state.vendas_db)
        
        if not vendas_df.empty:
            # Filtros
            col1, col2 = st.columns(2)
            with col1:
                data_inicio = st.date_input("Data Inicial")
            with col2:
                data_fim = st.date_input("Data Final")
            
            # Converter datas para comparação
            vendas_df['data_dt'] = pd.to_datetime(vendas_df['data'])
            filtro_data = (vendas_df['data_dt'].dt.date >= data_inicio) & (vendas_df['data_dt'].dt.date <= data_fim)
            vendas_filtradas = vendas_df[filtro_data]
            
            # Estatísticas
            if not vendas_filtradas.empty:
                total_vendas = len(vendas_filtradas)
                valor_total = vendas_filtradas['total'].sum()
                ticket_medio = valor_total / total_vendas if total_vendas > 0 else 0
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total de Vendas", f"{total_vendas}")
                with col2:
                    st.metric("Valor Total", f"R$ {valor_total:.2f}")
                with col3:
                    st.metric("Ticket Médio", f"R$ {ticket_medio:.2f}")
                
                # Gráfico de vendas por dia
                vendas_por_dia = vendas_filtradas.groupby(vendas_filtradas['data_dt'].dt.date)['total'].sum().reset_index()
                vendas_por_dia.columns = ['Data', 'Total']
                
                st.subheader("Vendas por Dia")
                st.line_chart(vendas_por_dia.set_index('Data'))
                
                # Lista de vendas
                st.subheader("Lista de Vendas")
                for _, venda in vendas_filtradas.iterrows():
                    with st.expander(f"Venda #{venda['id']} - {venda['data']} - R$ {venda['total']:.2f}"):
                        st.write(f"**Cliente:** {venda['cliente']}")
                        st.write(f"**Forma de Pagamento:** {venda['forma_pgto']}")
                        
                        st.subheader("Itens")
                        for item in venda['itens']:
                            st.write(f"• {item['quantidade']}x {item['produto']} - R$ {item['preco_unit']:.2f} = R$ {item['total']:.2f}")
            else:
                st.info("Nenhuma venda encontrada no período selecionado.")
        else:
            st.info("Nenhuma venda registrada no sistema.")
    
    with tab2:
        st.subheader("Relatório de Estoque")
        
        # Converter produtos em DataFrame
        produtos_df = pd.DataFrame(st.session_state.produtos_db.values())
        
        if not produtos_df.empty:
            # Filtros
            filtro_grupo = st.selectbox("Filtrar por Grupo", ["Todos"] + produtos_df["grupo"].unique().tolist())
            mostrar_zerados = st.checkbox("Mostrar itens com estoque zerado")
            
            # Aplicar filtros
            if filtro_grupo != "Todos":
                produtos_filtrados = produtos_df[produtos_df["grupo"] == filtro_grupo]
            else:
                produtos_filtrados = produtos_df
            
            if not mostrar_zerados:
                produtos_filtrados = produtos_filtrados[produtos_filtrados["estoque"] > 0]
            
            # Estatísticas
            total_produtos = len(produtos_filtrados)
            valor_estoque = (produtos_filtrados["preco"] * produtos_filtrados["estoque"]).sum()
            estoque_baixo = produtos_filtrados[produtos_filtrados["estoque"] <= 5].shape[0]
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total de Produtos", f"{total_produtos}")
            with col2:
                st.metric("Valor em Estoque", f"R$ {valor_estoque:.2f}")
            with col3:
                st.metric("Estoque Baixo", f"{estoque_baixo} produtos")
            
            # Gráfico de estoque por grupo
            estoque_por_grupo = produtos_filtrados.groupby("grupo")["estoque"].sum().reset_index()
            st.subheader("Estoque por Grupo")
            st.bar_chart(estoque_por_grupo.set_index("grupo"))
            
            # Lista de produtos
            st.subheader("Lista de Produtos")
            produtos_ordenados = produtos_filtrados.sort_values("estoque", ascending=True)
            for _, produto in produtos_ordenados.iterrows():
                cor_estoque = "red" if produto["estoque"] <= 5 else "green"
                with st.container():
                    col1, col2, col3 = st.columns([1, 3, 1])
                    with col1:
                        st.image(produto["foto"], width=50)
                    with col2:
                        st.write(f"**{produto['nome']}** ({produto['codigo_barras']})")
                        st.write(f"**Grupo:** {produto['grupo']} | **Marca:** {produto['marca']}")
                    with col3:
                        st.markdown(f"<p style='color:{cor_estoque};font-weight:bold;'>Estoque: {produto['estoque']}</p>", unsafe_allow_html=True)
                        st.write(f"R$ {produto['preco']:.2f}")
                st.divider()
        else:
            st.info("Nenhum produto cadastrado no sistema.")
    
    with tab3:
        st.subheader("Relatório Financeiro")
        
        # Converter vendas em DataFrame
        vendas_df = pd.DataFrame(st.session_state.vendas_db)
        
        if not vendas_df.empty:
            # Filtros
            col1, col2 = st.columns(2)
            with col1:
                mes = st.selectbox("Mês", ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", 
                                       "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"])
            with col2:
                ano = st.selectbox("Ano", range(2023, 2026))
            
            # Mapear mês para número
            meses = {"Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4, "Maio": 5, "Junho": 6, 
                    "Julho": 7, "Agosto": 8, "Setembro": 9, "Outubro": 10, "Novembro": 11, "Dezembro": 12}
            
            mes_num = meses[mes]
            
            # Converter datas para comparação
            vendas_df['data_dt'] = pd.to_datetime(vendas_df['data'])
            filtro_mes = (vendas_df['data_dt'].dt.month == mes_num) & (vendas_df['data_dt'].dt.year == ano)
            vendas_mes = vendas_df[filtro_mes]
            
            # Estatísticas
            if not vendas_mes.empty:
                receita_total = vendas_mes['total'].sum()
                
                # Calcular custo (baseado nos produtos vendidos)
                custo_total = 0
                for _, venda in vendas_mes.iterrows():
                    for item in venda['itens']:
                        codigo = next((k for k, v in st.session_state.produtos_db.items() 
                                    if v['nome'] == item['produto']), None)
                        if codigo:
                            custo_unit = st.session_state.produtos_db[codigo].get('preco_custo', 0)
                            custo_total += custo_unit * item['quantidade']
                
                lucro_bruto = receita_total - custo_total
                margem_lucro = (lucro_bruto / receita_total * 100) if receita_total > 0 else 0
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Receita Total", f"R$ {receita_total:.2f}")
                with col2:
                    st.metric("Custo Total", f"R$ {custo_total:.2f}")
                with col3:
                    st.metric("Lucro Bruto", f"R$ {lucro_bruto:.2f} ({margem_lucro:.1f}%)")
                
                # Gráfico de vendas por forma de pagamento
                vendas_por_pgto = vendas_mes.groupby("forma_pgto")["total"].sum().reset_index()
                st.subheader("Vendas por Forma de Pagamento")
                st.bar_chart(vendas_por_pgto.set_index("forma_pgto"))
                
                # Resumo diário
                st.subheader(f"Resumo Diário - {mes}/{ano}")
                vendas_por_dia = vendas_mes.groupby(vendas_mes['data_dt'].dt.day)['total'].sum().reset_index()
                vendas_por_dia.columns = ['Dia', 'Total']
                st.line_chart(vendas_por_dia.set_index('Dia'))
                
                # Tabela completa
                st.dataframe(vendas_por_dia)
            else:
                st.info(f"Nenhuma venda registrada em {mes}/{ano}.")
        else:
            st.info("Nenhuma venda registrada no sistema.")

# Menu principal
def menu_principal():
    st.sidebar.title("ORION PDV")
    st.sidebar.image("https://github.com/jesusmjunior/pdv2022/blob/69ff7f9ecaa6209d10cec3ea589f803b56180c32/logo.webp", width=100)
    
    opcoes = {
        "🧾 Registrar Venda": registrar_venda,
        "📦 Cadastro de Produtos": cadastrar_produto,
        "👥 Cadastro de Clientes": cadastrar_cliente,
        "📄 Importar Nota Fiscal": importar_nota_fiscal,
        "📊 Relatórios": gerar_relatorios,
        "❓ Ajuda": mostrar_instrucoes_scanner
    }
    
    escolha = st.sidebar.radio("Menu", list(opcoes.keys()))
    
    st.sidebar.markdown("---")
    st.sidebar.info(f"Usuário: {USUARIOS[st.session_state['usuario']]['nome']}")
    
    if st.sidebar.button("🚪 Sair"):
        st.session_state["autenticado"] = False
        st.session_state["usuario"] = None
        st.rerun()
    
    opcoes[escolha]()

# Programa principal
def main():
    if "autenticado" not in st.session_state or not st.session_state["autenticado"]:
        autenticar_usuario()
    else:
        menu_principal()

if __name__ == "__main__":
    main()
