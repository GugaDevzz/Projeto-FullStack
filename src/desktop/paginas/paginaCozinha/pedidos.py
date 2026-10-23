import customtkinter as ctk
from sqlalchemy.orm import joinedload
# Importe suas sessões e modelos
from DB.Banco import SessionLocal  # Ajuste conforme seu arquivo de conexão
from DB.models import Pedido, ItemPedido, Produto, Ingredientes
from sqlalchemy import select


# Configurações gerais de tema
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")


class CozinhaApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Catatau - Cozinha")
        self.geometry("1600x900")
        self.minsize(1000, 550)

        # Paleta de Cores
        self.COLOR_BG = "#F7F0E6"          # Bege claro do fundo principal
        self.COLOR_SIDEBAR = "#F1E5D5"     # Bege um pouco mais escuro (lateral)
        self.COLOR_CARD_BG = "#FFFFFF"     # Branco dos cards
        self.COLOR_BROWN = "#4A2810"       # Marrom escuro (textos, topo e rodapé)
        self.COLOR_ORANGE = "#FF6B00"      # Laranja vivo (botão/status)
        self.COLOR_GREEN = "#2E7D32"       # Verde (finalizado)
        self.COLOR_PROGRESS = "#E0D0C0"    # Barra de progresso fundo

        self.configure(fg_color=self.COLOR_BG)

        self.setup_ui()
        self.carregar_pedidos()

    def logout(self):
        from paginas.pagina_login import CatatauLogin
        self.destroy()
        app_principal = CatatauLogin()
        app_principal.mainloop()

    def carregar_historico(self):
        """ Limpa os cards atuais e renderiza APENAS os pedidos FINALIZADOS """
        # 1. Limpa os cards da tela
        for widget in self.cards_frame.winfo_children():
            widget.destroy()

        session = SessionLocal()
        try:
            # Busca estritamente os pedidos FINALIZADOS
            pedidos_historico = session.query(Pedido).options(
                joinedload(Pedido.itens).joinedload(ItemPedido.produto)
            ).filter(
                Pedido.status == "FINALIZADO"
            ).order_by(Pedido.id.desc()).all()

            # Atualiza contadores do rodapé do painel
            total_hoje = session.query(Pedido).count()
            self.lbl_total_pedidos.configure(text=str(total_hoje))
            self.lbl_prontos.configure(text=str(len(pedidos_historico)))

            if not pedidos_historico:
                lbl_vazio = ctk.CTkLabel(
                    self.cards_frame, 
                    text="Nenhum pedido no histórico! 📜", 
                    font=ctk.CTkFont(size=18, weight="bold"),
                    text_color=self.COLOR_BROWN
                )
                lbl_vazio.pack(pady=40)
                return

            colunas_max = 3
            for index, pedido in enumerate(pedidos_historico):
                row = index // colunas_max
                col = index % colunas_max
                
                lista_itens = []
                for item in pedido.itens:
                    nome_prod = item.produto.nome if item.produto else "Produto sem nome"
                    qtd = item.quantidade if item.quantidade else 1
                    lista_itens.append(f"{qtd}x {nome_prod}")
                
                if not lista_itens:
                    lista_itens = ["(Sem itens registrados)"]
                
                mesa_num = pedido.num_mesa if pedido.num_mesa is not None else 0
                titulo_card = f"MESA {mesa_num}" if mesa_num > 0 else "BALCÃO"
                sub_id_str = str(mesa_num) if mesa_num > 0 else ""
                
                nome_cliente = pedido.nome_cliente if pedido.nome_cliente else "Não informado"
                desc_pedido = (pedido.descricao or "").strip()

                # Reutiliza o SEU MÉTODO create_order_card original!
                self.create_order_card(
                    parent=self.cards_frame,
                    row=row,
                    column=col,
                    pedido_id=pedido.id,
                    title=titulo_card,
                    sub_id=sub_id_str,
                    name=nome_cliente,
                    items=lista_itens,
                    status="FINALIZADO",
                    descricao=desc_pedido
                )

        except Exception as e:
            print(f"Erro ao carregar histórico: {e}")
        finally:
            session.close()    

    def setup_ui(self):
        # Frame Principal (Esquerda + Centro) e Sidebar (Direita)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)  # Sidebar com largura fixa
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)      # Rodapé

        # ------------------- ÁREA PRINCIPAL (ESQUERDA) -------------------
        main_area = ctk.CTkFrame(self, fg_color="transparent")
        main_area.grid(row=0, column=0, sticky="nsew", padx=20, pady=15)
        main_area.grid_columnconfigure(0, weight=1)

        # 1. TÍTULO E LOGO
        header_frame = ctk.CTkFrame(main_area, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))

        title_label = ctk.CTkLabel(
            header_frame, 
            text="COZINHA - PEDIDOS ATIVOS", 
            font=ctk.CTkFont(family="Arial", size=32, weight="bold"),
            text_color=self.COLOR_BROWN
        )
        title_label.pack(side="left")

        logo_label = ctk.CTkLabel(
            header_frame, 
            text="🐻 Catatau", 
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.COLOR_BROWN
        )
        logo_label.pack(side="right")

        # 2. BARRA DE PROGRESSO DE TEMPO/CARGA
        progress_frame = ctk.CTkFrame(main_area, fg_color="transparent")
        progress_frame.pack(fill="x", pady=(0, 15))

        progress_bar = ctk.CTkProgressBar(
            progress_frame, 
            progress_color=self.COLOR_ORANGE,
            fg_color=self.COLOR_PROGRESS,
            height=14,
            corner_radius=7
        )
        progress_bar.pack(fill="x")
        progress_bar.set(0.65)

        # 3. CONTAINER DOS CARDS DE PEDIDOS (Grid dinâmico em ScrollableFrame)
        self.cards_frame = ctk.CTkScrollableFrame(main_area, fg_color="transparent")
        self.cards_frame.pack(fill="both", expand=True, pady=(0, 15))

        # Configura as colunas para o layout flexível de cards
        self.cards_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="card")

        # 4. PAINEL DE ESTATÍSTICAS (RODAPÉ INFERIOR DA ÁREA PRINCIPAL)
        stats_frame = ctk.CTkFrame(main_area, fg_color=self.COLOR_CARD_BG, corner_radius=12)
        stats_frame.pack(fill="x")
        stats_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # Labels das estatísticas que serão atualizadas via banco
        self.lbl_total_pedidos = self.create_stat_item(stats_frame, col=0, icon="📋", label="Total Pedidos (Hoje):", value="0")
        self.lbl_tempo_medio = self.create_stat_item(stats_frame, col=1, icon="⏱", label="Tempo Médio Prep:", value="-- min")
        self.lbl_prontos = self.create_stat_item(stats_frame, col=2, icon="📦", label="Pedidos Prontos:", value="0")

        # ------------------- SIDEBAR (DIREITA) -------------------
        sidebar = ctk.CTkFrame(self, fg_color=self.COLOR_SIDEBAR, corner_radius=0, width=220)
        sidebar.grid(row=0, column=1, sticky="nsew")
        sidebar.grid_propagate(False)

        ctk.CTkLabel(
            sidebar, text="Kitchen Controls", 
            font=ctk.CTkFont(size=16, weight="bold"), 
            text_color="black"
        ).pack(anchor="w", padx=15, pady=(20, 10))

        btn_atualizar = ctk.CTkButton(
            sidebar, text="🔄 Atualizar Lista", 
            fg_color="transparent", text_color="black", 
            anchor="w", hover_color="#E0D0C0", font=ctk.CTkFont(size=13),
            command=self.carregar_pedidos
        )
        btn_atualizar.pack(fill="x", padx=10, pady=2)

        btn_relatorio = ctk.CTkButton(
            sidebar, text="📄 Relatório do Turno", 
            fg_color="transparent", text_color="black", 
            anchor="w", hover_color="#E0D0C0", font=ctk.CTkFont(size=13)
        )
        btn_relatorio.pack(fill="x", padx=10, pady=2)

        ctk.CTkLabel(
            sidebar, text="Alertas de Ingredientes", 
            font=ctk.CTkFont(size=16, weight="bold"), 
            text_color="black"
        ).pack(anchor="w", padx=15, pady=(25, 10))

        # Usando 'sessionlocal' (com 's' minúsculo ou do jeito que estiver no seu código)
        with SessionLocal() as session:  # Use 'sessionlocal' com 's' minúsculo se esse for o nome no seu projeto
            critico = select(Ingredientes.nome).where(
                Ingredientes.status == 'Crítico'
            )
            resultados = session.scalars(critico).all()
            texto_alerta = (
                "\n" .join(resultados) if resultados else 'Nenhum ingrediente crítico'
            )

            # Passa a string gerada para o Label do CustomTkinter
            alert_label = ctk.CTkLabel(
                sidebar,
                text=texto_alerta,
                font=ctk.CTkFont(size=13),
                text_color='black',
                justify="left"
            )
            alert_label.pack(anchor='w', padx=15, pady=2)

        btn_config = ctk.CTkButton(
            sidebar, text="⚙ Configurações", 
            fg_color="transparent", text_color="black", 
            anchor="w", hover_color="#E0D0C0", font=ctk.CTkFont(size=13)
        )
        btn_config.pack(fill="x", padx=10, pady=(25, 0))

        # ------------------- RODAPÉ INFERIOR -------------------
        footer = ctk.CTkFrame(self, fg_color=self.COLOR_BROWN, corner_radius=0, height=35)
        footer.grid(row=1, column=0, columnspan=2, sticky="ew")

        nav_frame = ctk.CTkFrame(footer, fg_color="transparent")
        nav_frame.pack(expand=True)

        for item in ["INÍCIO", "HISTÓRICO", "LOGOUT"]:
            btn = ctk.CTkButton(
                nav_frame, text=item, 
                fg_color="transparent", 
                text_color="white", 
                hover_color="#6A3B18",
                width=100,
                font=ctk.CTkFont(weight="bold")
            )
            btn.pack(side="left", padx=15)

            if item == "INÍCIO":
                btn.configure(command=self.carregar_pedidos) # Volta para os ativos
            elif item == "HISTÓRICO":
                btn.configure(command=self.carregar_historico) # Vai para o histórico
            elif item == "LOGOUT":
                btn.configure(command=self.logout)

    # --- LÓGICA BANCO DE DADOS ---

    def carregar_pedidos(self):
        """ Busca os pedidos no banco e renderiza os cards e estatísticas """
        for widget in self.cards_frame.winfo_children():
            widget.destroy()

        session = SessionLocal()
        try:
            # Query garantindo o JOIN de Pedido -> ItemPedido -> Produto
            pedidos_ativos = session.query(Pedido).options(
                joinedload(Pedido.itens).joinedload(ItemPedido.produto)
            ).filter(
                Pedido.status.in_(["ESPERANDO", "PREPARANDO"])
            ).order_by(Pedido.id.asc()).all()

            total_hoje = session.query(Pedido).count()
            prontos_hoje = session.query(Pedido).filter(Pedido.status == "FINALIZADO").count()
            
            self.lbl_total_pedidos.configure(text=str(total_hoje))
            self.lbl_prontos.configure(text=str(prontos_hoje))

            if not pedidos_ativos:
                lbl_vazio = ctk.CTkLabel(
                    self.cards_frame, 
                    text="Nenhum pedido pendente no momento! 🎉", 
                    font=ctk.CTkFont(size=18, weight="bold"),
                    text_color=self.COLOR_BROWN
                )
                lbl_vazio.pack(pady=40)
                return

            colunas_max = 3
            for index, pedido in enumerate(pedidos_ativos):
                row = index // colunas_max
                col = index % colunas_max
                
                # 1. Trata a lista de itens com validação de produto
                lista_itens = []
                for item in pedido.itens:
                    nome_prod = item.produto.nome if item.produto else "Produto sem nome"
                    qtd = item.quantidade if item.quantidade else 1
                    lista_itens.append(f"{qtd}x {nome_prod}")
                
                if not lista_itens:
                    lista_itens = ["(Sem itens registrados)"]
                
                # 2. Tratamento do número da mesa e nome do cliente
                mesa_num = pedido.num_mesa if pedido.num_mesa is not None else 0
                titulo_card = f"MESA {mesa_num}" if mesa_num > 0 else "BALCÃO"
                sub_id_str = str(mesa_num) if mesa_num > 0 else ""
                
                nome_cliente = pedido.nome_cliente if pedido.nome_cliente else "Não informado"
                desc_pedido = (pedido.descricao or "").strip()


                # 3. Criação do card visual
                self.create_order_card(
                    parent=self.cards_frame,
                    row=row,
                    column=col,
                    pedido_id=pedido.id,
                    title=titulo_card,
                    sub_id=sub_id_str,
                    name=nome_cliente,
                    items=lista_itens,
                    status=pedido.status if pedido.status else "Pendente",
                    descricao=desc_pedido  # <--- PASSANDO A OBSERVAÇÃO AQUI
                )
            


        except Exception as e:
            print(f"Erro ao carregar pedidos: {e}")
        finally:
            session.close()

    def alterar_status_pedido(self, pedido_id, novo_status):
        """ Atualiza o status do pedido no banco de dados """
        session = SessionLocal()
        try:
            pedido = session.query(Pedido).filter(Pedido.id == pedido_id).first()
            if pedido:
                pedido.status = novo_status
                session.commit()
                self.carregar_pedidos()  # Recarrega a interface com os dados atualizados
        except Exception as e:
            session.rollback()
            print(f"Erro ao atualizar status: {e}")
        finally:
            session.close()

    # --- MÉTODOS AUXILIARES ---

    def create_order_card(self, parent, row, column, pedido_id, title, sub_id, name, items, status, descricao=""):
        """ Cria o card de cada pedido vindo do banco """
        
        # Define as cores e textos de acordo com o status do banco
        if status == "ESPERANDO":
            status_color = self.COLOR_BROWN
            btn_text = "INICIAR"
            btn_color = self.COLOR_BROWN
            proximo_status = "PREPARANDO"
        elif status == "PREPARANDO":
            status_color = self.COLOR_ORANGE
            btn_text = "CONCLUIR"
            btn_color = self.COLOR_ORANGE
            proximo_status = "FINALIZADO"
        else:
            status_color = self.COLOR_GREEN
            btn_text = ""
            btn_color = None
            proximo_status = None

        # Criação do Card principal
        card = ctk.CTkFrame(parent, fg_color=self.COLOR_CARD_BG, corner_radius=12)
        card.grid(row=row, column=column, sticky="nsew", padx=8, pady=8)
        
        # Cabeçalho do Card
        head = ctk.CTkFrame(card, fg_color="transparent")
        head.pack(fill="x", padx=15, pady=(12, 2))
        
        ctk.CTkLabel(
            head, text=title, 
            font=ctk.CTkFont(size=18, weight="bold"), 
            text_color="black"
        ).pack(side="left")

        if sub_id:
            ctk.CTkLabel(
                head, text=f"#{sub_id}", 
                font=ctk.CTkFont(size=18, weight="bold"), 
                text_color=self.COLOR_BROWN
            ).pack(side="right")

        # NOME DO CLIENTE
        ctk.CTkLabel(
            card, text=f"👤 Cliente: {name}", 
            font=ctk.CTkFont(size=13, weight="bold"), 
            text_color="#555555",
            anchor="w"
        ).pack(fill="x", padx=15, pady=(2, 5))

        # Linha Divisória
        ctk.CTkFrame(card, fg_color="#E0E0E0", height=2).pack(fill="x", padx=15, pady=5)

        # Lista de Itens do Pedido
        items_frame = ctk.CTkFrame(card, fg_color="transparent")
        items_frame.pack(fill="x", padx=15, pady=5)

        for item in items:
            ctk.CTkLabel(
                items_frame, text=item, 
                font=ctk.CTkFont(size=14, weight="bold"), 
                text_color="black", 
                anchor="w"
            ).pack(fill="x", pady=2)

        # OBSERVAÇÃO / DESCRIÇÃO (Estrutura segura com Frame e Label com quebra de linha)
        if descricao and str(descricao).strip() and str(descricao).strip() != "None":
            obs_frame = ctk.CTkFrame(card, fg_color="#FFF3E0", corner_radius=6)
            obs_frame.pack(fill="x", padx=15, pady=6)

            ctk.CTkLabel(
                obs_frame, 
                text=f"📝 Obs: {descricao}", 
                font=ctk.CTkFont(size=12, weight="bold"), 
                text_color="#D84315",
                wraplength=240,  # Força a quebra correta dentro do card para não sumir o botão
                justify="left"
            ).pack(anchor="w", padx=8, pady=6)

        # Status do Pedido
        ctk.CTkLabel(
            card, text=status, 
            font=ctk.CTkFont(size=14, weight="bold"), 
            text_color=status_color
        ).pack(pady=(5, 5))

        # Botão de Ação dinâmico (Sempre preso no rodapé do card)
        if btn_text:
            btn = ctk.CTkButton(
                card, text=btn_text, 
                fg_color=btn_color, 
                hover_color=btn_color,
                font=ctk.CTkFont(size=13, weight="bold"),
                height=35, 
                corner_radius=8,
                command=lambda pid=pedido_id, nst=proximo_status: self.alterar_status_pedido(pid, nst)
            )
            btn.pack(fill="x", padx=15, pady=(0, 15))
        else:
            ctk.CTkFrame(card, fg_color="transparent", height=35).pack(pady=(0, 15))

    def create_stat_item(self, parent, col, icon, label, value):
        """ Cria um item do painel estatístico e retorna o rótulo do valor para atualização dinâmica """
        item_frame = ctk.CTkFrame(parent, fg_color="transparent")
        item_frame.grid(row=0, column=col, pady=10)

        ctk.CTkLabel(
            item_frame, text=icon, 
            font=ctk.CTkFont(size=24)
        ).pack(side="left", padx=(0, 10))

        info_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        info_frame.pack(side="left")

        ctk.CTkLabel(
            info_frame, text=label, 
            font=ctk.CTkFont(size=12, weight="bold"), 
            text_color="black"
        ).pack(anchor="w")

        lbl_valor = ctk.CTkLabel(
            info_frame, text=value, 
            font=ctk.CTkFont(size=22, weight="bold"), 
            text_color="black"
        )
        lbl_valor.pack(anchor="w")
        
        return lbl_valor
