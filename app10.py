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
                        
                        if codigo in st.session_state.produtos_db:
                            st.session_state.produtos_db[codigo]['estoque'] += produto['qtd']
                            st.session_state.produtos_db[codigo]['preco_custo'] = produto['valor_unit']
                            st.session_state.produtos_db[codigo]['preco'] = produto['valor_unit'] * (1 + margem/100)
                            st.session_state.produtos_db[codigo]['margem'] = margem
                        else:
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
    
    produtos_df = pd.DataFrame(st.session_state.produtos_db.values())
    if not produtos_df.empty:
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
        
        df_filtrado = produtos_df.copy()
        if filtro_grupo and "Todos" not in filtro_grupo and 'grupo' in df_filtrado.columns:
            df_filtrado = df_filtrado[df_filtrado['grupo'].isin(filtro_grupo)]
        if filtro_marca and "Todas" not in filtro_marca and 'marca' in df_filtrado.columns:
            df_filtrado = df_filtrado[df_filtrado['marca'].isin(filtro_marca)]
            
        colunas_display = ["nome", "codigo_barras", "preco", "estoque", "unidade_medida", "marca", "grupo"]
        st.dataframe(df_filtrado[colunas_display])
    else:
        st.warning("Nenhum produto cadastrado")
        
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
                
                unidades_medida = ["unidade", "kg", "g", "L", "ml", "pacote", "caixa", "fardo"]
                unidade_medida = st.selectbox("Unidade de Medida", unidades_medida,
                                            index=unidades_medida.index(produto.get('unidade_medida')) if produto.get('unidade_medida') in unidades_medida else 0)
            
            with col2:
                modo_preco = st.radio("Modo de precificação:", ["Preço direto", "Baseado em custo"], key="edit_modo")
                
                if modo_preco == "Preço direto":
                    preco = st.number_input("Preço de Venda", min_value=0.01, format="%.2f", value=float(produto.get('preco', 0.01)))
                    preco_custo = st.number_input("Preço de Custo", min_value=0.0, format="%.2f", value=float(produto.get('preco_custo', 0.0)))
                    margem = 0
                    if preco_custo > 0:
                        margem = ((preco - preco_custo) / preco_custo) * 100
                        st.info(f"Margem calculada: {margem:.2f}%")
                else:
                    preco_custo = st.number_input("Preço de Custo", min_value=0.01, format="%.2f", value=float(produto.get('preco_custo', 0.01)))
                    margem = st.slider("Margem de Lucro (%)", min_value=0, max_value=500, value=int(produto.get('margem', 30)))
                    preco = preco_custo * (1 + margem/100)
                    st.info(f"Preço calculado: R$ {preco:.2f}")
                
                estoque = st.number_input("Estoque", min_value=0, value=int(produto.get('estoque', 0)))
                marca = st.selectbox("Marca", marcas_lista,
                                    index=marcas_lista.index(produto.get('marca')) if produto.get('marca') in marcas_lista else 0)
                
            col1, col2 = st.columns(2)
            with col1:
                descricao = st.text_area("Descrição detalhada", value=produto.get('descricao', ''), height=100)
            
            with col2:
                localizacao = st.text_input("Localização no Estoque", value=produto.get('localizacao', ''))
                fornecedor = st.text_input("Fornecedor", value=produto.get('fornecedor', ''))
            
            foto_url = st.text_input("URL da Imagem", value=produto.get('foto', ''))
            
            if st.form_submit_button("Atualizar Produto"):
                if nome:
                    st.session_state.produtos_db[codigo_editar].update({
                        "nome": nome,
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
                        "foto": foto_url if foto_url else produto.get('foto', "https://via.placeholder.com/150")
                    })
                    st.success("Produto atualizado com sucesso!")
                else:
                    st.error("Nome do produto é obrigatório")
    elif codigo_editar:
        st.error("Produto não encontrado!")

# Módulo de Cadastro de Cliente
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

# Módulo de Painel Financeiro
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
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de Vendas", f"{len(vendas_df)}")
    with col2:
        st.metric("Faturamento Total", f"R$ {vendas_df['total'].sum():.2f}")
    with col3:
        st.metric("Ticket Médio", f"R$ {vendas_df['total'].mean():.2f}")
    
    st.subheader("Filtros")
    col1, col2 = st.columns(2)
    with col1:
        hoje = datetime.now().date()
        data_inicio = st.date_input("Data Inicial", 
                                  value=hoje - pd.Timedelta(days=30),
                                  max_value=hoje)
    with col2:
        data_fim = st.date_input("Data Final", 
                               value=hoje,
                               max_value=hoje)
    
    mask = (vendas_df["data"].dt.date >= data_inicio) & (vendas_df["data"].dt.date <= data_fim)
    vendas_filtradas = vendas_df[mask]
    
    if len(vendas_filtradas) == 0:
        st.warning("Nenhuma venda no período selecionado")
        return
    
    st.subheader("Análise de Vendas")
    vendas_por_dia = vendas_filtradas.groupby(vendas_filtradas["data"].dt.date)["total"].sum().reset_index()
    vendas_por_dia.columns = ["data", "total"]
    st.line_chart(vendas_por_dia.set_index("data"))
    
    st.subheader("Vendas por Forma de Pagamento")
    vendas_por_pgto = vendas_filtradas.groupby("forma_pgto")["total"].sum().reset_index()
    st.bar_chart(vendas_por_pgto.set_index("forma_pgto"))
    
    st.subheader("Lista de Vendas no Período")
    st.dataframe(vendas_filtradas[["id", "data", "cliente", "forma_pgto", "total"]])

# Módulo de Histórico de Vendas
def historico_vendas():
    st.header("📜 Histórico de Vendas")
    
    if not st.session_state.vendas_db:
        st.warning("Nenhuma venda registrada")
        return
    
    st.subheader("Filtros")
    col1, col2 = st.columns(2)
    with col1:
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

# Módulo de Gerenciamento de Estoque
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
        nomes_produtos = [p["nome"] for p in produtos]
        produto_selecionado = st.selectbox("Selecione o Produto", nomes_produtos)
    
    with col2:
        quantidade = st.number_input("Quantidade", min_value=1, value=1)
    
    if st.button("Registrar Entrada", type="primary"):
        codigo = None
        for c, p in st.session_state.produtos_db.items():
            if p["nome"] == produto_selecionado:
                codigo = c
                break
        
        if codigo:
            st.session_state.produtos_db[codigo]["estoque"] += quantidade
            st.success(f"Adicionadas {quantidade} unidades de {produto_selecionado} ao estoque!")
            st.rerun()
    
    st.subheader("Alertas de Estoque Baixo")
    
    produtos_baixo_estoque = []
    for codigo, produto in st.session_state.produtos_db.items():
        if produto["estoque"] < 10:
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
        
        logo_url = st.text_input("URL da Logo", value="https://github.com/jesusmjunior/pdv2022/blob/69ff7f9ecaa6209d10cec3ea589f803b56180c32/logo.webp")
        
        if st.form_submit_button("Salvar Configurações"):
            st.success("Configurações salvas!")
    
    st.subheader("Backup de Dados")
    
    if st.button("Exportar Dados"):
        dados_exportacao = {
            "produtos": st.session_state.produtos_db,
            "vendas": st.session_state.vendas_db,
            "clientes": st.session_state.clientes_db,
            "data_exportacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        json_str = pd.Series(dados_exportacao).to_json()
        
        st.download_button(
            label="📥 Baixar Arquivo de Backup",
            data=json_str,
            file_name=f"backup_orion_pdv_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
        
        st.success("Backup gerado com sucesso!")
    
    st.subheader("Importar Backup")
    
    arquivo_importacao = st.file_uploader("Selecione o arquivo de backup", type=["json"])
    
    if arquivo_importacao is not None:
        try:
            dados_importados = pd.read_json(arquivo_importacao, typ="series")
            
            if st.button("Confirmar Importação", type="primary"):
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
    if "autenticado" not in st.session_state or not st.session_state.autenticado:
        autenticar_usuario()
        return
    
    pagina = sidebar()
    
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
