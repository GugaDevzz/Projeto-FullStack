import customtkinter as ctk
from DB.Banco import SessionLocal
from DB.models import Cliente


class ClienteRow(ctk.CTkFrame):
    """Componente que representa cada linha/campo individual de um cliente."""
    def __init__(self, parent, cliente: Cliente, on_click=None):
        super().__init__(parent, fg_color="#F9F9F9", height=45, corner_radius=8)
        self.pack_propagate(False) # Mantém a altura fixa ajustada
        
        # Mapeamento dinâmico dos atributos do objeto ORM Cliente
        nome = getattr(cliente, 'nome', 'Sem Nome')
        telefone = getattr(cliente, 'telefone', '(00) 00000-0000')
        compras_count = getattr(cliente, 'pedidos_count', 0)
        compras = f"{compras_count} Pedidos" if compras_count != 1 else "1 Pedido"
        tag = getattr(cliente, 'status', 'Regular')

        # Labels formatadas
        self.lbl_nome = ctk.CTkLabel(self, text=nome, font=ctk.CTkFont(size=13, weight="bold"), text_color="#000", width=180, anchor="w")
        self.lbl_nome.pack(side="left", padx=15)

        self.lbl_tel = ctk.CTkLabel(self, text=telefone, font=ctk.CTkFont(size=12), text_color="#555", width=140, anchor="w")
        self.lbl_tel.pack(side="left")

        self.lbl_compras = ctk.CTkLabel(self, text=compras, font=ctk.CTkFont(size=12), text_color="#000", width=100, anchor="w")
        self.lbl_compras.pack(side="left")

        self.lbl_tag = ctk.CTkLabel(self, text=tag, font=ctk.CTkFont(size=11, weight="bold"), text_color="#3A1A10", width=80, anchor="e")
        self.lbl_tag.pack(side="right", padx=15)

class ClientesView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#FFFFFF", corner_radius=15)

        # Título
        ctk.CTkLabel(
            self,
            text="BASE DE CLIENTES CADASTRADOS👥",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#3A1A10"
        ).pack(anchor="w", padx=20, pady=15)

        # Container rolável
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Carrega os registros
        self.carregar_clientes()

    def carregar_clientes(self):
        # Limpa widgets anteriores caso haja recarregamento
        for child in self.scroll.winfo_children():
            child.destroy()

        session = SessionLocal()
        try:
            # Busca todos os clientes do banco de dados
            clientes = session.query(Cliente).all()

            if not clientes:
                ctk.CTkLabel(
                    self.scroll,
                    text="Nenhum cliente cadastrado.",
                    font=ctk.CTkFont(size=13),
                    text_color="#888"
                ).pack(pady=20)
                return

            # Instancia um componente ClienteRow para cada registro do banco
            for cliente in clientes:
                card = ClienteRow(self.scroll, cliente=cliente, on_click=None)
                card.pack(fill="x", pady=4, padx=5)

        finally:
            session.close()

    