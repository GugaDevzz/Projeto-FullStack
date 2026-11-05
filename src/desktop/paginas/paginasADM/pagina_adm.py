import customtkinter as ctk

from paginas.paginasADM.dashboard_view import DashboardView
from paginas.paginasADM.pedidos_view import PedidosView
from paginas.paginasADM.estoque_view import EstoqueView
from paginas.paginasADM.clientes_view import ClientesView
from paginas.paginasADM.clientes_view import ClienteRow
from paginas.paginasADM.cupons_view import CuponsView
from paginas.paginasADM.relatorios_view import RelatoriosView
from DB.Banco import SessionLocal
from DB.models import Cliente, Pedido


ctk.set_appearance_mode("Light")

class PaginaADM(ctk.CTk):
    def __init__(self, usuario_atual=None):
        super().__init__()
        self.usuario_atual = usuario_atual or 'CATATAU'

        self.title("Catatau Lanches - Painel Administrativo")
        self.geometry("1100x620")
        self.configure(fg_color="#F3EBE1")

        # Configuração do Grid Principal
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(0, weight=1)

        # Lado Esquerdo (Header + Barra Nav + Conteúdo Mutável)
        self.left_container = ctk.CTkFrame(self, fg_color="transparent")
        self.left_container.grid(row=0, column=0, sticky="nsew", padx=20, pady=10)

        # Título
        self.header_label = ctk.CTkLabel(
            self.left_container, 
            text="CATATAU LANCHES 🐻🍔", 
            font=ctk.CTkFont(family="Arial", size=32, weight="bold"),
            text_color="#C09267"
        )
        self.header_label.pack(anchor="w", pady=(0, 10))

        # Dicionário de Páginas
        self.pages = {}
        
        # Barra de Navegação
        self.nav_buttons = {}
        self.create_navbar()

        # ÁREA DINÂMICA (Onde as telas vão trocar)
        self.content_area = ctk.CTkFrame(self.left_container, fg_color="transparent")
        self.content_area.pack(fill="both", expand=True)

        # Inicializar e guardar cada página
        self.pages["DASHBOARD"] = DashboardView(self.content_area)
        self.pages["PEDIDOS"] = PedidosView(self.content_area)
        self.pages["ESTOQUE"] = EstoqueView(self.content_area)
        self.pages["CLIENTES"] = ClientesView(self.content_area)
        self.pages["CUPONS"] = CuponsView(self.content_area)
        self.pages["RELATÓRIOS"] = RelatoriosView(self.content_area)

        # Sidebar e Footer
        self.create_sidebar()
        self.create_footer()

        # Mostrar tela inicial
        self.show_page("DASHBOARD")


    

    def carregar_dados_geral(self):
        """Função única na PaginaADM que atualiza tanto os Clientes quanto todo o resto de uma vez só"""
        session = SessionLocal()
        try:
            # 1. CARREGAR CLIENTES
            scroll_clientes = self.pages["CLIENTES"].scroll
            for child in scroll_clientes.winfo_children():
                child.destroy()
                
            session.rollback() # Limpa o cache da sessão atual
            
            clientes = session.query(Cliente).all()
            if not clientes:
                ctk.CTkLabel(
                    scroll_clientes,
                    text="Nenhum cliente cadastrado.",
                    font=ctk.CTkFont(size=13),
                    text_color="#888",
                ).pack(pady=20)
            else:
                for cliente in clientes:
                    card = ClienteRow(scroll_clientes, cliente=cliente, on_click=None)
                    card.pack(fill="x", pady=4, padx=5)

            # 2. CARREGAR PEDIDOS
            scroll_pedidos = self.pages["PEDIDOS"].scroll
            for child in scroll_pedidos.winfo_children():
                child.destroy()

            # Cabeçalhos da tabela de pedidos
            headers = ["ID", "Mesa", "Cliente", "Itens", "Total", "Status", "Ação"]
            h_frame = ctk.CTkFrame(scroll_pedidos, fg_color="#F3EBE1", height=30)
            h_frame.pack(fill="x", pady=2)
            for h in headers:
                ctk.CTkLabel(
                    h_frame,
                    text=h,
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color="#000",
                    width=100
                ).pack(side="left", expand=True)

            pedidos = session.query(Pedido).order_by(Pedido.id.desc()).all()
            if not pedidos:
                ctk.CTkLabel(
                    scroll_pedidos,
                    text="Nenhum pedido cadastrado.",
                    font=ctk.CTkFont(size=13),
                    text_color="#888",
                ).pack(pady=20)
            else:
                for p in pedidos:
                    row = ctk.CTkFrame(scroll_pedidos, fg_color="#F9F9F9", height=35)
                    row.pack(fill="x", pady=2)

                    total_itens = sum(item.quantidade for item in p.itens) if p.itens else 0
                    if total_itens == 0:
                        resumo_itens = "Sem lanches"
                    elif total_itens == 1:
                        resumo_itens = "1x Lanche"
                    else:
                        resumo_itens = f"{total_itens}x Lanches"

                    nome_cliente = p.nome_cliente if p.nome_cliente else "-"
                    valor = p.valor_final if p.valor_final else 0.0

                    ctk.CTkLabel(row, text=f"#{p.id}", font=ctk.CTkFont(size=12), text_color="#000", width=100).pack(side="left", expand=True)
                    ctk.CTkLabel(row, text=f"Mesa {p.num_mesa}", font=ctk.CTkFont(size=12), text_color="#000", width=100).pack(side="left", expand=True)
                    ctk.CTkLabel(row, text=nome_cliente, font=ctk.CTkFont(size=12), text_color="#000", width=100).pack(side="left", expand=True)
                    ctk.CTkLabel(row, text=resumo_itens, font=ctk.CTkFont(size=12), text_color="#000", width=100).pack(side="left", expand=True)
                    ctk.CTkLabel(row, text=f"R$ {valor:.2f}".replace('.', ','), font=ctk.CTkFont(size=12), text_color="#000", width=100).pack(side="left", expand=True)
                    ctk.CTkLabel(row, text=p.status, font=ctk.CTkFont(size=12), text_color="#000", width=100).pack(side="left", expand=True)

                    btn_detalhes = ctk.CTkButton(
                        row,
                        text="Detalhes",
                        width=80,
                        height=24,
                        fg_color="#3A1A10",
                        font=ctk.CTkFont(size=11),
                        command=lambda p_id=p.id, s=session: self.pages["PEDIDOS"].abrir_detalhes(p_id)
                    )
                    btn_detalhes.pack(side="left", expand=True)
        finally:
            session.close()


    def create_navbar(self):
        nav_frame = ctk.CTkFrame(self.left_container, fg_color="transparent")
        nav_frame.pack(fill="x", pady=(0, 10))

        nav_items = ["DASHBOARD", "PEDIDOS", "ESTOQUE", "CLIENTES", "CUPONS", "RELATÓRIOS"]
        
        for name in nav_items:
            btn = ctk.CTkButton(
                nav_frame,
                text=name,
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color="transparent",
                text_color="#000000",
                hover_color="#DFCBB8",
                corner_radius=12,
                height=32,
                width=95,
                command=lambda p=name: self.show_page(p)
            )
            btn.pack(side="left", padx=3)
            self.nav_buttons[name] = btn

    def show_page(self, page_name):
        # Esconde todas as páginas
        for page in self.pages.values():
            page.pack_forget()

        # Exibe a página selecionada
        if page_name in self.pages:
            self.pages[page_name].pack(fill="both", expand=True)

        # Atualiza a cor dos botões da Navbar
        for name, btn in self.nav_buttons.items():
            if name == page_name:
                btn.configure(fg_color="#3A1A10", text_color="#FFFFFF", hover_color="#52291B")
            else:
                btn.configure(fg_color="transparent", text_color="#000000", hover_color="#DFCBB8")

    def create_sidebar(self):
        sidebar = ctk.CTkFrame(self, fg_color="#EADDCF", width=200, corner_radius=0)
        sidebar.grid(row=0, column=1, sticky="nsew")
        sidebar.grid_propagate(False)

        user_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        user_frame.pack(fill="x", padx=15, pady=20)
        ctk.CTkLabel(user_frame, text="👤", font=ctk.CTkFont(size=32)).pack(side="left", padx=(0, 8))
        
        info = ctk.CTkFrame(user_frame, fg_color="transparent")
        info.pack(side="left")
        ctk.CTkLabel(info, text="Gerente", font=ctk.CTkFont(size=11), text_color="#555").pack(anchor="w")
        ctk.CTkLabel(info, text=str(self.usuario_atual).upper(), font=ctk.CTkFont(size=15, weight="bold"), text_color="#000").pack(anchor="w")

        ctk.CTkLabel(sidebar, text="Admin Control", font=ctk.CTkFont(size=13, weight="bold"), text_color="#000").pack(anchor="w", padx=15, pady=(10, 10))
        
        # menu = ["👥 Gerenciar Usuários", "⚙️ Configurações"]
        # for item in menu:
        #     ctk.CTkButton(sidebar, text=item, anchor="w", fg_color="transparent", text_color="#000", hover_color="#DFCBB8", font=ctk.CTkFont(size=12, weight="bold"), height=38).pack(fill="x", padx=8, pady=3)

        btn_atualizar = ctk.CTkButton(
            sidebar, text="🔄 Atualizar Lista", 
            fg_color="transparent", text_color="#000", 
            anchor="w", hover_color="#DFCBB8", font=ctk.CTkFont(size=12, weight="bold"),
            command=self.carregar_dados_geral
        )
        btn_atualizar.pack(fill="x", padx=10, pady=2)   

        btn_usuarios = ctk.CTkButton(
            sidebar, text="👥 Gestão de Usuários",
            fg_color="transparent", text_color="#000",
            anchor="w", hover_color="#DFCBB8", font=ctk.CTkFont(size=12, weight="bold"),
            command=self.abrir_gestao_usuarios
        )
        btn_usuarios.pack(fill="x", padx=10, pady=2)

        # gerencias usuarios deve aparecer todas as informações contidas na tabela clientes 

    def abrir_gestao_usuarios(self):
        from paginas.paginasADM.gestao_usuarios_modal import GestaoUsuariosModal
        GestaoUsuariosModal(self, usuario_logado=self.usuario_atual)

    def logout(self):
        from paginas.pagina_login import CatatauLogin
        self.destroy()
        app_principal = CatatauLogin()
        app_principal.mainloop()

    def create_footer(self):
        footer = ctk.CTkFrame(self, fg_color="#3A1A10", height=35, corner_radius=0)
        footer.grid(row=1, column=0, columnspan=2, sticky="ew")


        ctk.CTkButton(footer, text="LOGOUT", fg_color="transparent", text_color="#FFF", hover_color="#52291B", font=ctk.CTkFont(weight="bold"), command=self.logout).pack(side="left", expand=True)

        ctk.CTkButton(footer, text="AJUDA", fg_color="transparent", text_color="#FFF", hover_color="#52291B", font=ctk.CTkFont(weight="bold")).pack(side="right", expand=True)
