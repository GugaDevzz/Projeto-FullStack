import customtkinter as ctk
from sqlalchemy.orm import joinedload
from sqlalchemy import or_

from DB.Banco import SessionLocal
from DB.models import Pedido, ItemPedido, Ingredientes


class HistoricoFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        self.setup_ui()

    def setup_ui(self):
        # 1. TÍTULO E LOGO
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 15))

        title_label = ctk.CTkLabel(
            header_frame, 
            text="HISTÓRICO DE PEDIDOS", 
            font=ctk.CTkFont(family="Arial", size=32, weight="bold"),
            text_color=self.controller.COLOR_BROWN
        )
        title_label.pack(side="left")

        logo_label = ctk.CTkLabel(
            header_frame, 
            text="🐻 Catatau", 
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.controller.COLOR_BROWN
        )
        logo_label.pack(side="right")

        # 2. BARRA DE FILTROS E BUSCA
        filter_frame = ctk.CTkFrame(self, fg_color=self.controller.COLOR_CARD_BG, corner_radius=10)
        filter_frame.pack(fill="x", pady=(0, 15), padx=5)

        # Entrada de Pesquisa
        self.search_entry = ctk.CTkEntry(
            filter_frame, 
            placeholder_text="🔍 Buscar por cliente ou mesa...",
            width=300,
            height=35,
            fg_color=self.controller.COLOR_BG,
            border_color=self.controller.COLOR_PROGRESS,
            text_color="black"
        )
        self.search_entry.pack(side="left", padx=15, pady=10)
        
        # Evento corrigido de "" para ""
        self.search_entry.bind("", lambda e: self.carregar_historico())

        # Filtro de Status
        ctk.CTkLabel(filter_frame, text="Status:", font=ctk.CTkFont(weight="bold"), text_color="black").pack(side="left", padx=(15, 5))
        
        self.filter_status_var = ctk.StringVar(value="TODOS")
        self.combo_status = ctk.CTkOptionMenu(
            filter_frame,
            values=["TODOS", "FINALIZADO", "CANCELADO"],
            variable=self.filter_status_var,
            command=lambda val: self.carregar_historico(),
            fg_color=self.controller.COLOR_BROWN,
            button_color=self.controller.COLOR_BROWN,
            button_hover_color="#6A3B18"
        )
        self.combo_status.pack(side="left", padx=5)

        # 3. CONTAINER SCROLLÁVEL
        self.historico_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.historico_container.pack(fill="both", expand=True)

    def carregar_historico(self):
        """ Busca e renderiza os pedidos finalizados/cancelados """
        for widget in self.historico_container.winfo_children():
            widget.destroy()

        busca = self.search_entry.get().strip() if hasattr(self, 'search_entry') else ""
        filtro_status = self.filter_status_var.get() if hasattr(self, 'filter_status_var') else "TODOS"

        session = SessionLocal()
        try:
            query = session.query(Pedido).options(
                joinedload(Pedido.itens).joinedload(ItemPedido.produto)
            )

            if filtro_status == "TODOS":
                query = query.filter(Pedido.status.in_(["FINALIZADO", "CANCELADO"]))
            else:
                query = query.filter(Pedido.status == filtro_status)

            if busca:
                if busca.isdigit():
                    query = query.filter(or_(Pedido.num_mesa == int(busca), Pedido.id == int(busca)))
                else:
                    query = query.filter(Pedido.nome_cliente.ilike(f"%{busca}%"))

            pedidos_historico = query.order_by(Pedido.id.desc()).all()

            if not pedidos_historico:
                lbl_vazio = ctk.CTkLabel(
                    self.historico_container, 
                    text="Nenhum registro encontrado no histórico.", 
                    font=ctk.CTkFont(size=16, weight="bold"),
                    text_color=self.controller.COLOR_BROWN
                )
                lbl_vazio.pack(pady=40)
                return

            for pedido in pedidos_historico:
                self.create_historico_item(pedido)

        except Exception as e:
            print(f"Erro ao carregar histórico: {e}")
        finally:
            session.close()

    def create_historico_item(self, pedido):
        """ Cria a linha/card de cada pedido no Histórico """
        card = ctk.CTkFrame(self.historico_container, fg_color=self.controller.COLOR_CARD_BG, corner_radius=10)
        card.pack(fill="x", pady=6, padx=5)

        if pedido.status == "FINALIZADO":
            status_color = self.controller.COLOR_GREEN
            badge_bg = "#E8F5E9"
        else:
            status_color = self.controller.COLOR_RED
            badge_bg = "#FFEBEE"

        mesa_str = f"Mesa {pedido.num_mesa}" if pedido.num_mesa else "Balcão"
        cliente_str = pedido.nome_cliente or "Sem nome"

        # Cabeçalho do Card
        top_frame = ctk.CTkFrame(card, fg_color="transparent")
        top_frame.pack(fill="x", padx=15, pady=(10, 5))

        ctk.CTkLabel(
            top_frame, text=f"Pedido #{pedido.id} - {mesa_str} ({cliente_str})", 
            font=ctk.CTkFont(size=16, weight="bold"), 
            text_color="black"
        ).pack(side="left")

        status_frame = ctk.CTkFrame(top_frame, fg_color=badge_bg, corner_radius=6)
        status_frame.pack(side="right")

        ctk.CTkLabel(
            status_frame, text=f"  {pedido.status}  ", 
            font=ctk.CTkFont(size=12, weight="bold"), 
            text_color=status_color
        ).pack(pady=3)

        ctk.CTkFrame(card, fg_color="#F0F0F0", height=1).pack(fill="x", padx=15, pady=2)

        # Conteúdo
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(fill="x", padx=15, pady=(5, 10))

        itens_text = ", ".join([f"{item.quantidade or 1}x {item.produto.nome if item.produto else 'Item'}" for item in pedido.itens])
        if not itens_text:
            itens_text = "Nenhum item informado"

        ctk.CTkLabel(
            content_frame, text=f"Itens: {itens_text}", 
            font=ctk.CTkFont(size=13), 
            text_color="#444444",
            anchor="w",
            wraplength=800
        ).pack(side="left", fill="x", expand=True)

        # Botão Reabrir
        btn_reabrir = ctk.CTkButton(
            content_frame, 
            text="↩ Voltar p/ Cozinha", 
            fg_color="transparent", 
            border_color=self.controller.COLOR_BROWN,
            border_width=1,
            text_color=self.controller.COLOR_BROWN,
            hover_color="#E0D0C0",
            font=ctk.CTkFont(size=11, weight="bold"),
            width=130, height=28,
            command=lambda: self.controller.alterar_status_pedido(pedido.id, "PREPARANDO")
        )
        btn_reabrir.pack(side="right", padx=(10, 0))