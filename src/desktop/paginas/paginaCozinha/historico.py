# pagina_historico.py
from paginas.paginaCozinha.pedidos import CozinhaApp  # Importa sua classe original
from DB.Banco import SessionLocal
from DB.models import Pedido, ItemPedido
from sqlalchemy.orm import joinedload
import customtkinter as ctk

class HistoricoApp(CozinhaApp):
    def __init__(self):
        # Executa a contrução visual da tela pai (com sidebar, footer, etc.)
        super().__init__()
        
    # Sobrescreve apenas a função de carregar dados para buscar FINALIZADOS
    def carregar_pedidos(self):
        for widget in self.cards_frame.winfo_children():
            widget.destroy()

        session = SessionLocal()
        try:
            pedidos_finalizados = session.query(Pedido).options(
                joinedload(Pedido.itens).joinedload(ItemPedido.produto)
            ).filter(
                Pedido.status == "FINALIZADO"
            ).order_by(Pedido.id.desc()).all()

            total_hoje = session.query(Pedido).count()
            self.lbl_total_pedidos.configure(text=str(total_hoje))
            self.lbl_prontos.configure(text=str(len(pedidos_finalizados)))

            colunas_max = 3
            for index, pedido in enumerate(pedidos_finalizados):
                row = index // colunas_max
                col = index % colunas_max
                
                lista_itens = [f"{i.quantidade or 1}x {i.produto.nome if i.produto else 'Produto'}" for i in pedido.itens]
                mesa_num = pedido.num_mesa if pedido.num_mesa is not None else 0
                
                # Reutiliza a função da classe Pai para desenhar os cards
                self.create_order_card(
                    parent=self.cards_frame,
                    row=row,
                    column=col,
                    pedido_id=pedido.id,
                    title=f"MESA {mesa_num}" if mesa_num > 0 else "BALCÃO",
                    sub_id=str(mesa_num) if mesa_num > 0 else "",
                    name=pedido.nome_cliente or "Não informado",
                    items=lista_itens,
                    status="FINALIZADO",
                    descricao=(pedido.descricao or "").strip()
                )
        except Exception as e:
            print(f"Erro: {e}")
        finally:
            session.close()