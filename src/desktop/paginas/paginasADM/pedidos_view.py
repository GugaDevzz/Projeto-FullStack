import customtkinter as ctk
from DB.Banco import SessionLocal
from DB.models import Pedido, ItemPedido, Produto

class DetalhesPedidoModal(ctk.CTkToplevel):
    def __init__(self, parent, session, pedido_id):
        super().__init__(parent)
        self.session = session

        # Busca o pedido no banco de dados pelo ID
        pedido = self.session.query(Pedido).filter(Pedido.id == pedido_id).first()
        if not pedido:
            self.destroy()
            return

        self.title(f"Detalhes do Pedido #{pedido.id}")
        self.geometry("450x580")
        self.resizable(False, False)

        # Foco exclusivo na janela modal
        self.transient(parent)
        self.grab_set()

        main_frame = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=10)
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # Cabeçalho
        ctk.CTkLabel(
            main_frame,
            text=f"Pedido #{pedido.id} — Status: {pedido.status}",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#3A1A10"
        ).pack(anchor="w", padx=15, pady=(15, 5))

        # Informações da Mesa / Cliente
        info_box = ctk.CTkFrame(main_frame, fg_color="#F9F9F9", corner_radius=8)
        info_box.pack(fill="x", padx=15, pady=5)

        nome_cliente = pedido.nome_cliente if pedido.nome_cliente else "Não informado"
        ctk.CTkLabel(
            info_box,
            text=f"🪑 Mesa: {pedido.num_mesa}",
            font=ctk.CTkFont(weight="bold"),
            text_color="#333"
        ).pack(anchor="w", padx=10, pady=(5, 2))

        ctk.CTkLabel(
            info_box,
            text=f"👤 Cliente: {nome_cliente}",
            text_color="#555"
        ).pack(anchor="w", padx=10, pady=2)

        if pedido.descricao:
            ctk.CTkLabel(
                info_box,
                text=f"📝 Obs: {pedido.descricao}" + " ",
                font=ctk.CTkFont(size=11, slant="italic"),
                text_color="#667"
            ).pack(anchor="w", padx=10, pady=(4, 5))

        # Itens do Pedido
        ctk.CTkLabel(
            main_frame,
            text="Itens do Pedido:",
            font=ctk.CTkFont(weight="bold"),
            text_color="#3A1A10"
        ).pack(anchor="w", padx=15, pady=(10, 2))

        itens_frame = ctk.CTkScrollableFrame(main_frame, fg_color="#F3EBE1", height=180, corner_radius=8)
        itens_frame.pack(fill="x", padx=15, pady=5)

        for item in pedido.itens:
            row = ctk.CTkFrame(itens_frame, fg_color="transparent")
            row.pack(fill="x", pady=2)

            nome_prod = item.produto.nome if item.produto else f"Produto #{item.fk_id_produto}"
            preco_unit = item.produto.valor if (item.produto and hasattr(item.produto, 'valor')) else 0.0
            subtotal = item.quantidade * preco_unit

            ctk.CTkLabel(
                row,
                text=f"{item.quantidade}x {nome_prod}",
                font=ctk.CTkFont(weight="bold"),
                text_color="#000"
            ).pack(side="left")

            ctk.CTkLabel(
                row,
                text=f"R$ {subtotal:.2f}".replace('.', ','),
                text_color="#000"
            ).pack(side="right")

        # Total
        total_box = ctk.CTkFrame(main_frame, fg_color="#F9F9F9", corner_radius=8)
        total_box.pack(fill="x", padx=15, pady=5)

        valor_final = pedido.valor_final if pedido.valor_final else 0.0
        ctk.CTkLabel(
            total_box,
            text=f"💰 Valor Final: R$ {valor_final:.2f}".replace('.', ','),
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#3A1A10"
        ).pack(anchor="w", padx=10, pady=8)

        # Botões de Ação
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(15, 5))

        # ctk.CTkButton(
        #     btn_frame,
        #     text="🖨️ Imprimir Comanda",
        #     fg_color="#3A1A10",
        #     hover_color="#522618",
        #     width=180
        # ).pack(side="left", expand=True, padx=2)
        # essa parte pode ser usada para fins futuros de impressão de nota, para controle físico

        ctk.CTkButton(
            btn_frame,
            text="✅ Concluir Pedido",
            fg_color="#2E7D32",
            hover_color="#1B5E20",
            width=180,
            command=lambda: self.concluir_pedido(pedido)
        ).pack(side="left", expand=True, padx=2)

    def concluir_pedido(self, pedido):
        pedido.status = "Entregue"
        self.session.commit()
        self.destroy()


class PedidosView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#FFFFFF", corner_radius=15)
        
        # Cria a sessão do banco diretamente aqui dentro
        self.session = SessionLocal()

        ctk.CTkLabel(
            self,
            text="GERENCIAMENTO DE PEDIDOS 📝",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#3A1A10"
        ).pack(anchor="w", padx=20, pady=15)

        # Tabela com Scroll
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Cabeçalhos
        headers = ["ID", "Mesa", "Cliente", "Itens", "Total", "Status", "Ação"]
        h_frame = ctk.CTkFrame(scroll, fg_color="#F3EBE1", height=30)
        h_frame.pack(fill="x", pady=2)
        for h in headers:
            ctk.CTkLabel(
                h_frame,
                text=h,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#000",
                width=100
            ).pack(side="left", expand=True)

        # Busca pedidos diretamente do banco
        pedidos = self.session.query(Pedido).order_by(Pedido.id.desc()).all()

        for p in pedidos:
            row = ctk.CTkFrame(scroll, fg_color="#F9F9F9", height=35)
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
                command=lambda p_id=p.id: self.abrir_detalhes(p_id)
            )
            btn_detalhes.pack(side="left", expand=True)
    def abrir_detalhes(self, pedido_id):
        DetalhesPedidoModal(self, self.session, pedido_id)

    def destroy(self):
        # Garante o fechamento da sessão ao fechar o frame
        self.session.close()
        super().destroy()