import customtkinter as ctk
from datetime import datetime, date, timedelta
from sqlalchemy import Date, cast, func
from DB.models import Pedido, Produto, ItemPedido, Ingredientes
from DB.Banco import SessionLocal
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class DashboardView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        self.grid_columnconfigure((0, 1, 2), weight=1, uniform="group1")
        self.grid_rowconfigure((0, 1), weight=1)

        session = SessionLocal()
        data_referencia = datetime.now().date()
        vendas_dia = (
            session.query(Pedido)
            .filter(Pedido.status == 'FINALIZADO', Pedido.data_hora_fim != None, cast(Pedido.data_hora_fim, Date) == data_referencia).all()
        )
        total_vendas = sum(pedido.valor_final for pedido in vendas_dia if pedido.valor_final)
        
        # Card 1: Vendas do Dia
        c1 = self.create_card(0, 0)
        ctk.CTkLabel(c1, text="VENDAS DO DIA 💰", font=ctk.CTkFont(size=14, weight="bold"), text_color="#000").pack(anchor="w", padx=15, pady=(15, 5))
        ctk.CTkLabel(c1, text=f'R$ {total_vendas:.2f}', font=ctk.CTkFont(size=28, weight="bold"), text_color="#000").pack(anchor="w", padx=15)

        resultados_query = (
            session.query(
                Produto.nome.label('nome_produto'),
                func.sum(ItemPedido.quantidade).label('total_quantidade')
            )
            .join(ItemPedido, ItemPedido.fk_id_produto == Produto.id)
            .join(Pedido, ItemPedido.fk_id_pedido == Pedido.id)
            .group_by(Produto.id, Produto.nome)
            .order_by(func.sum(ItemPedido.quantidade).desc())
            .limit(3)
            .all()
        )

        texto_resultados = "\n \n \n".join([f"{i}º  {r.nome_produto} — {r.total_quantidade} un." for i, r in enumerate(resultados_query, 1)])
        if not texto_resultados:
            texto_resultados = "Nenhum pedido registrado hoje."
        
        # Card 2: Top Lanches
        c2 = self.create_card(0, 1)
        ctk.CTkLabel(c2, text="TOP LANCHES 🍔", font=ctk.CTkFont(size=14, weight="bold"), text_color="#000").pack(anchor="w", padx=15, pady=(15, 0))
        ctk.CTkLabel(c2, text=texto_resultados, font=ctk.CTkFont(size=12, weight="bold"), text_color="#333", justify="left").pack(anchor="w", padx=20, pady=(0, 25), expand=True)

        # Card 3 (Canto Superior Direito): Estoque Crítico
        c3 = self.create_card(0, 2)
        self.fill_estoque_por_status(c3, "ESTOQUE CRÍTICO 📦", "Crítico", "#D97706")

        # Card 4 (Inferior Esquerdo - maior espaço): Estoque em Atenção
        c4 = self.create_card(1, 0)
        self.fill_estoque_por_status(c4, "ESTOQUE EM ATENÇÃO ⚠️", "Atenção", "#D97706")

        # Card 5: Resumo Financeiro (Gráfico 7 dias)
        c5 = self.create_card(1, 1, columnspan=2)
        ctk.CTkLabel(c5, text="RESUMO FINANCEIRO (ÚLTIMOS 7 DIAS)", font=ctk.CTkFont(size=14, weight="bold"), text_color="#000").pack(anchor="w", padx=15, pady=(15, 0))
        
        hoje = datetime.now().date()
        data_inicio = hoje - timedelta(days=6)
        
        vendas_7_dias = (
            session.query(
                cast(Pedido.data_hora_fim, Date).label('data'),
                func.sum(Pedido.valor_final).label('total')
            )
            .filter(
                Pedido.status == 'FINALIZADO',
                Pedido.data_hora_fim != None,
                cast(Pedido.data_hora_fim, Date) >= data_inicio,
                cast(Pedido.data_hora_fim, Date) <= hoje
            )
            .group_by(cast(Pedido.data_hora_fim, Date))
            .order_by(cast(Pedido.data_hora_fim, Date))
            .all()
        )
        session.close()

        dicionario_vendas = {(hoje - timedelta(days=i)): 0.0 for i in range(6, -1, -1)}
        for data_venda, total in vendas_7_dias:
            if data_venda in dicionario_vendas:
                dicionario_vendas[data_venda] = float(total)

        dias_x = [d.strftime('%d/%m') for d in dicionario_vendas.keys()]
        valores_y = list(dicionario_vendas.values())

        fig, ax = plt.subplots(figsize=(6, 2.2), dpi=100)
        fig.patch.set_facecolor('#FFFFFF')
        ax.set_facecolor('#FFFFFF')

        ax.plot(dias_x, valores_y, color='#D97706', marker='o', linewidth=2.5, markersize=6)
        ax.fill_between(dias_x, valores_y, color='#D97706', alpha=0.15)

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#E0E0E0')
        ax.spines['bottom'].set_color('#E0E0E0')
        ax.tick_params(colors='#555', labelsize=9)
        ax.grid(axis='y', linestyle='--', alpha=0.5, color='#E0E0E0')

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=c5)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=15, pady=(5, 15))

    def create_card(self, row, col, columnspan=1):
        card = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=15, border_width=1, border_color="#E0E0E0")
        card.grid(row=row, column=col, columnspan=columnspan, sticky="nsew", padx=6, pady=6)
        return card

    def calcular_status_automatico(self, nome, qtd):
        """Replica exata da sua lógica de cálculo de status baseada nas unidades e quantidades."""
        try:
            qtd_float = float(qtd)
        except (ValueError, TypeError):
            return "Ok"
        
        nome_lower = nome.lower()

        if "uni" in nome_lower:
            if qtd_float < 15: return "Crítico"
            elif qtd_float <= 50: return "Atenção"
            else: return "Ok"
        elif "fatia" in nome_lower:
            if qtd_float < 20: return "Crítico"
            elif qtd_float <= 60: return "Atenção"
            else: return "Ok"
        elif "kg" in nome_lower:
            if qtd_float < 0.5: return "Crítico"
            elif qtd_float <= 1.2: return "Atenção"
            else: return "Ok"
        elif "g" in nome_lower:
            if qtd_float < 200: return "Crítico"
            elif qtd_float <= 600: return "Atenção"
            else: return "Ok"
        
        return "Ok"

    def fill_estoque_por_status(self, card, titulo_card, status_alvo, cor):
        ctk.CTkLabel(card, text=titulo_card, font=ctk.CTkFont(size=14, weight="bold"), text_color="#000").pack(anchor="w", padx=15, pady=(10, 5))
        
        session = SessionLocal()
        try:
            ingredientes = session.query(Ingredientes).all()
        except Exception as e:
            ingredientes = []
            print(f"Erro ao buscar estoque: {e}")
        finally:
            session.close()

        # Filtra dinamicamente usando a sua própria regra/função de status
        itens_filtrados = []
        for ing in ingredientes:
            status_calculado = self.calcular_status_automatico(ing.unidade_medida or ing.nome, ing.quantidade)
            if status_calculado == status_alvo:
                itens_filtrados.append(ing)

        if not itens_filtrados:
            ctk.CTkLabel(card, text=f"Nenhum item em {status_alvo.lower()}.", font=ctk.CTkFont(size=12), text_color="#666").pack(anchor="w", padx=15, pady=10)
            return

        for ing in itens_filtrados:
            try:
                qtd_val = float(ing.quantidade)
            except:
                qtd_val = 0.0

            unidade_lower = (ing.unidade_medida or ing.nome).lower()
            
            # Define o teto máximo de referência para normalizar a barra de 0.0 a 1.0 com base na sua regra
            if "uni" in unidade_lower:
                max_ref = 60.0
            elif "fatia" in unidade_lower:
                max_ref = 80.0
            elif "kg" in unidade_lower:
                max_ref = 2.0
            elif "g" in unidade_lower:
                max_ref = 800.0
            else:
                max_ref = 100.0

            progresso = max(0.0, min(qtd_val / max_ref, 1.0))
            val_texto = f"{ing.quantidade} {ing.unidade_medida or ''}"

            f = ctk.CTkFrame(card, fg_color="transparent")
            f.pack(fill="x", padx=15, pady=2)
            
            ctk.CTkLabel(f, text=ing.nome, font=ctk.CTkFont(size=12, weight="bold"), text_color="#000", width=110, anchor="w").pack(side="left")
            
            pb = ctk.CTkProgressBar(f, height=8, progress_color=cor, fg_color="#E5E7EB")
            pb.pack(side="left", fill="x", expand=True, padx=8)
            pb.set(progresso)
            
            ctk.CTkLabel(f, text=val_texto, font=ctk.CTkFont(size=11, weight="bold"), text_color=cor).pack(side="right")