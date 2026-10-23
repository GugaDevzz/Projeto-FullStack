import customtkinter as ctk

from paginas.paginasADM.dashboard_view import DashboardView
from paginas.paginasADM.pedidos_view import PedidosView
from paginas.paginasADM.estoque_view import EstoqueView
from paginas.paginasADM.clientes_view import ClientesView
from paginas.paginasADM.cupons_view import CuponsView
from paginas.paginasADM.relatorios_view import RelatoriosView


ctk.set_appearance_mode("Light")

class PaginaADM(ctk.CTk):
    def __init__(self):
        super().__init__()

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
        ctk.CTkLabel(info, text="CATATAU", font=ctk.CTkFont(size=15, weight="bold"), text_color="#000").pack(anchor="w")

        ctk.CTkLabel(sidebar, text="Admin Control", font=ctk.CTkFont(size=13, weight="bold"), text_color="#000").pack(anchor="w", padx=15, pady=(10, 10))
        
        menu = ["👥 Gerenciar Usuários", "📄 Relatório de\n    Fechamento", "⚙️ Configurações"]
        for item in menu:
            ctk.CTkButton(sidebar, text=item, anchor="w", fg_color="transparent", text_color="#000", hover_color="#DFCBB8", font=ctk.CTkFont(size=12, weight="bold"), height=38).pack(fill="x", padx=8, pady=3)

        # gerencias usuarios deve aparecer todas as informações contidas na tabela clientes 

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
