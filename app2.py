import streamlit as st
import pandas as pd
import hashlib
from datetime import datetime
import io
from PIL import Image
import base64
import re

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

# Variável para armazenar o último código de barras
if 'ultimo_codigo' not in st.session_state:
    st.session_state.ultimo_codigo = None

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
        with col2:
            st.subheader(produto['nome'])
            st.write(f"**Preço:** R$ {produto['preco']:.2f}")
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
    # (substituir pelo seu URL real quando deployed)
    app_url = "https://pdvoliveira.streamlit.app" 
    st.markdown(f"""
    <div style="text-align: center; margin: 20px 0;">
        <p>Escaneie este QR Code para abrir o aplicativo no seu celular:</p>
        <img src="https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={app_url}" width="150">
    </div>
    """, unsafe_allow_html=True)

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
    tab1, tab2 = st.tabs(["Adicionar Produto", "Consultar por Código de Barras"])
    
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
                preco = st.number_input("Preço", min_value=0.0, step=0.01, format="%.2f")
            with col2:
                estoque = st.number_input("Estoque", min_value=0)
            
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
                    'foto': foto_url
                }
                
                # Salvar no "banco de dados" local (session_state)
                st.session_state.produtos_db[codigo_barras] = novo_produto
                st.success(f"Produto '{nome}' cadastrado com sucesso!")
                st.json(novo_produto)
    
    with tab2:
        # Scanner de código de barras fora do formulário
        codigo_scaneado = leitor_codigo_barras()
        
        # Instruções para uso com aplicativos externos
        with st.expander("Como escanear códigos com seu celular", expanded=False):
            mostrar_instrucoes_scanner()
            
        # Exibir todos os produtos cadastrados
        st.subheader("Produtos Cadastrados")
        
        # Criar dataframe para visualização
        produtos_list = []
        for codigo, produto in st.session_state.produtos_db.items():
            produtos_list.append({
                "Código": codigo,
                "Produto": produto['nome'],
                "Preço": f"R$ {produto['preco']:.2f}",
                "Estoque": produto['estoque']
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

# Função de registro de venda com extração assistida de código de barras
def render_registro_venda():
    st.title("🧾 Registrar Venda")

    try:
        cliente_df = pd.read_csv(URL_CLIENTE)
        forma_pgto_df = pd.read_csv(URL_PGTO)
    except Exception as e:
        st.error(f"Erro ao carregar dados de venda: {e}")
        return
    
    # Inicializar carrinho de compras na sessão se não existir
    if 'carrinho' not in st.session_state:
        st.session_state.carrinho = []
    
    # Área de leitura de código de barras
    st.subheader("Adicionar Produto por Código de Barras")
    
    tab1, tab2 = st.tabs(["Digitar Código", "Extrair de Texto/Imagem"])
    
    codigo_usado = None
    
    with tab1:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Input manual
            codigo_manual = st.text_input("Digite o código de barras:", 
                                        placeholder="Ex: 7891000315507",
                                        value=st.session_state.ultimo_codigo if st.session_state.ultimo_codigo else "")
            
            if st.button("✅ Usar Este Código", key="btn_usar_manual"):
                codigo_usado = codigo_manual
                st.session_state.ultimo_codigo = codigo_manual
        
        with col2:
            qtd = st.number_input("Quantidade", min_value=1, value=1, step=1, key="qtd_tab1")
    
    with tab2:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Área para colar texto para extração de código
            ocr_texto = st.text_area("Cole aqui o texto obtido pelo OCR ou os números do código de barras:",
                                   placeholder="Cole o texto que contém os números do código de barras...",
                                   height=100)
            
            if st.button("🔍 Extrair Código", key="btn_extrair") and ocr_texto:
                codigo_extraido = extrair_codigo_barras(ocr_texto)
                if codigo_extraido:
                    st.success(f"Código extraído: {codigo_extraido}")
                    st.session_state.ultimo_codigo = codigo_extraido
                    codigo_usado = codigo_extraido
                else:
                    st.error("Não foi possível extrair um código de barras válido do texto.")
            
            # Upload de imagem para referência visual
            uploaded_file = st.file_uploader("📸 Upload da foto do código de barras (para referência):", 
                                          type=["jpg", "png", "jpeg"])
            
            if uploaded_file is not None:
                image = Image.open(uploaded_file)
                st.image(image, caption="Imagem carregada (Use OCR externo para extrair o código)", width=250)
                st.info("Use Google Lens ou outro app de OCR para extrair os números da imagem.")
                
        with col2:
            qtd = st.number_input("Quantidade", min_value=1, value=1, step=1, key="qtd_tab2")
    
    # Link para instruções de scanner
    with st.expander("Como escanear códigos com seu celular", expanded=False):
        mostrar_instrucoes_scanner()
    
    # Usar o código da sessão se não tivemos um código extraído nesta iteração
    if not codigo_usado and st.session_state.ultimo_codigo:
        codigo_usado = st.session_state.ultimo_codigo
    
    # Botão para adicionar produto ao carrinho
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
                    'foto': produto['foto']
                }
                st.session_state.carrinho.append(item)
                
            st.success(f"Produto '{produto['nome']}' adicionado ao carrinho!")
            
            # Limpar código após adicionar ao carrinho
            st.session_state.ultimo_codigo = None
            st.rerun()
        else:
            st.error(f"Código de barras {codigo_usado} não encontrado. Cadastre o produto primeiro.")
    
    # Exibir carrinho
    st.subheader("Carrinho de Compras")
    
    if not st.session_state.carrinho:
        st.info("Carrinho vazio. Adicione produtos escaneando os códigos de barras.")
    else:
        # Exibir itens do carrinho
        for i, item in enumerate(st.session_state.carrinho):
            col1, col2, col3, col4 = st.columns([1, 3, 1, 1])
            
            with col1:
                if item['foto']:
                    st.image(item['foto'], width=80)
                
            with col2:
                st.write(f"**{item['produto']}**")
                st.write(f"Código: {item['codigo_barras']}")
                
            with col3:
                st.write(f"Qtd: {item['quantidade']}")
                st.write(f"R$ {item['preco_unit']:.2f}")
                
            with col4:
                st.write(f"**R$ {item['total']:.2f}**")
                if st.button("🗑️", key=f"remove_{i}"):
                    st.session_state.carrinho.pop(i)
                    st.rerun()
            
            st.divider()
        
        # Total do carrinho
        total_carrinho = sum(item['total'] for item in st.session_state.carrinho)
        st.subheader(f"Total: R$ {total_carrinho:.2f}")
        
        # Área de finalização
        st.subheader("Finalizar Venda")
        with st.form("form_finalizar"):
            cliente = st.selectbox("Cliente", cliente_df["NOME"].dropna())
            forma_pgto = st.selectbox("Forma de Pagamento", forma_pgto_df["DESCRICAO"].dropna())
            
            finalizar = st.form_submit_button("Finalizar Venda")
            
            if finalizar:
                venda = {
                    "cliente": cliente,
                    "forma_pgto": forma_pgto,
                    "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "total": total_carrinho,
                    "itens": st.session_state.carrinho
                }
                
                st.success("Venda registrada com sucesso!")
                st.json(venda)
                
                # Limpar carrinho após finalizar
                st.session_state.carrinho = []
                st.rerun()
        
        # Botão para limpar carrinho
        if st.button("Limpar Carrinho"):
            st.session_state.carrinho = []
            st.rerun()

# Função de relatórios
def render_relatorios():
    st.title("📊 Relatório de Vendas")

    try:
        venda_df = pd.read_csv(URL_VENDA)
        venda_df["DATA"] = pd.to_datetime(venda_df["DATA"], errors="coerce")
    except Exception as e:
        st.error(f"Erro ao carregar dados para relatório: {e}")
        return

    col1, col2 = st.columns(2)
    with col1:
        data_ini = st.date_input("Data Inicial", datetime.today())
    with col2:
        data_fim = st.date_input("Data Final", datetime.today())

    formas = venda_df["ID_FORMA_PGTO"].dropna().unique()
    forma_selecionada = st.selectbox("Filtrar por Forma de Pagamento (opcional)", ["Todas"] + list(formas))

    if st.button("Gerar Relatório"):
        try:
            filtro = (venda_df['DATA'].dt.date >= data_ini) & (venda_df['DATA'].dt.date <= data_fim)
            if forma_selecionada != "Todas":
                filtro &= (venda_df['ID_FORMA_PGTO'] == forma_selecionada)

            relatorio = venda_df[filtro].copy()

            if not relatorio.empty:
                st.success(f"Foram encontradas {len(relatorio)} vendas no período.")
                st.dataframe(relatorio)
                total = relatorio['TOTAL'].sum()
                st.markdown(f"### 💰 Total de Vendas no Período: R$ {total:.2f}")

                csv = relatorio.to_csv(index=False).encode()
                st.download_button("📥 Baixar CSV", csv, "relatorio_vendas.csv", "text/csv")
            else:
                st.warning("Nenhuma venda encontrada para os filtros aplicados.")

        except Exception as err:
            st.error(f"Erro no processamento do relatório: {err}")

# Função do painel financeiro
def render_painel():
    st.title("📈 Painel Financeiro")

    try:
        venda_df = pd.read_csv(URL_VENDA)
        venda_df["DATA"] = pd.to_datetime(venda_df["DATA"], errors="coerce")
    except Exception as e:
        st.error(f"Erro ao carregar dados para o painel: {e}")
        return

    # Versão sem Plotly (usando gráficos nativos do Streamlit)
    st.subheader("Total por Forma de Pagamento")
    pgto_group = venda_df.groupby("ID_FORMA_PGTO")["TOTAL"].sum().reset_index()
    st.bar_chart(pgto_group.set_index("ID_FORMA_PGTO"))
    
    st.subheader("Evolução Diária de Vendas")
    diario = venda_df.groupby(venda_df["DATA"].dt.date)["TOTAL"].sum().reset_index()
    st.line_chart(diario.set_index("DATA"))
    
    total_vendas = venda_df['TOTAL'].sum()
    st.metric("Total Geral de Vendas", f"R$ {total_vendas:,.2f}")

# Função principal que gerencia todo o fluxo do aplicativo
def main():
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        autenticar_usuario()
        return

    st.sidebar.title("🔹 Menu PDV")
    if st.sidebar.button("Sair"):
        st.session_state["autenticado"] = False
        st.rerun()

    menu = st.sidebar.radio("Escolha a opção:", [
        "Registrar Venda", "Cadastro Produto", "Cadastro Cliente", "Relatórios", "Painel"])

    if menu == "Cadastro Produto":
        render_cadastro_produto()
    elif menu == "Cadastro Cliente":
        render_cadastro_cliente()
    elif menu == "Registrar Venda":
        render_registro_venda()
    elif menu == "Relatórios":
        render_relatorios()
    elif menu == "Painel":
        render_painel()

# Execução principal
if __name__ == "__main__":
    main()
