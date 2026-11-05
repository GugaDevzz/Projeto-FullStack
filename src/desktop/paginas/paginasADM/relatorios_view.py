import customtkinter as ctk
import calendar
from datetime import datetime, timedelta
from sqlalchemy import func, cast, Date
from DB.models import Pedido, Produto, ItemPedido
from DB.Banco import SessionLocal

# Importações do Matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class RelatoriosView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#FFFFFF", corner_radius=15)
        
        # Título principal da página
        ctk.CTkLabel(
            self, 
            text="RELATÓRIOS E GERENCIAL 📊", 
            font=ctk.CTkFont(size=18, weight="bold"), 
            text_color="#3A1A10"
        ).pack(anchor="w", padx=20, pady=(15, 10))

        # Criando um ScrollableFrame para conter os gráficos com rolagem suave
        self.scroll_container = ctk.CTkScrollableFrame(
            self, 
            fg_color="transparent", 
            corner_radius=10
        )
        self.scroll_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.scroll_container.grid_columnconfigure(0, weight=1)

        # Abre a sessão do banco para coletar os dados
        session = SessionLocal()
        try:
            self.criar_grafico_faturamento(session)
            self.criar_grafico_produtos(session)
            self.criar_grafico_status_pedidos(session)
        finally:
            session.close()

    def criar_card_container(self, titulo):
        """Cria um card padrão para encapsular cada gráfico"""
        card = ctk.CTkFrame(
            self.scroll_container, 
            fg_color="#F9F9F9", 
            corner_radius=15, 
            border_width=1, 
            border_color="#E0E0E0"
        )
        card.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            card, 
            text=titulo, 
            font=ctk.CTkFont(size=14, weight="bold"), 
            text_color="#3A1A10"
        ).pack(anchor="w", padx=15, pady=(15, 5))
        
        return card

    def criar_grafico_faturamento(self, session):
        """Gráfico 1: Faturamento Geral do Mês Atual (Blindado para qualquer mês)"""
        card = self.criar_card_container("📈 EVOLUÇÃO DO FATURAMENTO (MÊS ATUAL)")
        
        hoje = datetime.now().date()
        primeiro_dia_mes = hoje.replace(day=1)
        
        # Descobre automaticamente quantos dias o mês atual tem (ex: 28, 30, 31)
        ultimo_dia_num = calendar.monthrange(hoje.year, hoje.month)[1]
        
        # Define o limite máximo: ou é o dia de hoje (se o mês estiver correndo) ou o último dia do mês
        limite_data = min(hoje, hoje.replace(day=ultimo_dia_num))
        
        vendas = (
            session.query(
                cast(Pedido.data_hora_fim, Date).label('data'),
                func.sum(Pedido.valor_final).label('total')
            )
            .filter(
                Pedido.status == 'FINALIZADO',
                Pedido.data_hora_fim != None,
                cast(Pedido.data_hora_fim, Date) >= primeiro_dia_mes,
                cast(Pedido.data_hora_fim, Date) <= limite_data
            )
            .group_by(cast(Pedido.data_hora_fim, Date))
            .order_by(cast(Pedido.data_hora_fim, Date))
            .all()
        )

        # Cria o dicionário preenchendo do dia 1º até o dia atual de forma segura
        dicionario_vendas = {}
        data_atual = primeiro_dia_mes
        while data_atual <= limite_data:
            dicionario_vendas[data_atual] = 0.0
            data_atual += timedelta(days=1)

        # Preenche com os valores reais vindos do banco
        for data_venda, total in vendas:
            if data_venda in dicionario_vendas:
                dicionario_vendas[data_venda] = float(total)

        dias_x = [d.strftime('%d/%m') for d in dicionario_vendas.keys()]
        valores_y = list(dicionario_vendas.values())

        fig, ax = plt.subplots(figsize=(8, 2.5), dpi=100)
        fig.patch.set_facecolor('#F9F9F9')
        ax.set_facecolor('#F9F9F9')

        ax.plot(dias_x, valores_y, color='#D97706', marker='o', linewidth=2, markersize=4)
        ax.fill_between(dias_x, valores_y, color='#D97706', alpha=0.15)

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#E0E0E0')
        ax.spines['bottom'].set_color('#E0E0E0')
        ax.tick_params(colors='#555', labelsize=8)
        
        if len(dias_x) > 15:
            plt.xticks(rotation=45)

        ax.grid(axis='y', linestyle='--', alpha=0.5, color='#E0E0E0')
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=card)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=15, pady=(5, 15))

    def criar_grafico_produtos(self, session):
        """Gráfico 2: Top 5 Produtos Mais Vendidos"""
        card = self.criar_card_container("🍔 TOP 5 PRODUTOS MAIS VENDIDOS (GERAL)")
        
        resultados = (
            session.query(
                Produto.nome.label('nome'),
                func.sum(ItemPedido.quantidade).label('qtd')
            )
            .join(ItemPedido, ItemPedido.fk_id_produto == Produto.id)
            .group_by(Produto.id, Produto.nome)
            .order_by(func.sum(ItemPedido.quantidade).desc())
            .limit(5)
            .all()
        )

        if resultados:
            nomes = [r.nome for r in resultados][::-1] # Inverte para exibir o 1º no topo
            quantidades = [r.qtd for r in resultados][::-1]
        else:
            nomes = ["Sem vendas"]
            quantidades = [0]

        fig, ax = plt.subplots(figsize=(8, 2.5), dpi=100)
        fig.patch.set_facecolor('#F9F9F9')
        ax.set_facecolor('#F9F9F9')

        bars = ax.barh(nomes, quantidades, color='#4B5563', height=0.5)
        
        # Destaca o primeiro colocado com cor laranjada da marca
        if len(bars) > 0:
            bars[-1].set_color('#D97706')

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#E0E0E0')
        ax.spines['bottom'].set_color('#E0E0E0')
        ax.tick_params(colors='#555', labelsize=9)
        ax.grid(axis='x', linestyle='--', alpha=0.5, color='#E0E0E0')
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=card)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=15, pady=(5, 15))

    def criar_grafico_status_pedidos(self, session):
        """Gráfico 3: Distribuição do Status dos Pedidos"""
        card = self.criar_card_container("📋 DISTRIBUIÇÃO DE STATUS DOS PEDIDOS")
        
        status_query = (
            session.query(
                Pedido.status,
                func.count(Pedido.id).label('total')
            )
            .group_by(Pedido.status)
            .all()
        )

        if status_query:
            labels = [s[0] for s in status_query]
            tamanhos = [s[1] for s in status_query]
        else:
            labels = ['Nenhum pedido']
            tamanhos = [1]

        fig, ax = plt.subplots(figsize=(8, 2.5), dpi=100)
        fig.patch.set_facecolor('#F9F9F9')
        ax.set_facecolor('#F9F9F9')

        cores = ['#D97706', '#4B5563', '#10B981', '#EF4444', '#3B82F6']
        
        wedges, texts, autotexts = ax.pie(
            tamanhos, 
            labels=labels, 
            autopct='%1.1f%%', 
            startangle=140, 
            colors=cores[:len(labels)],
            textprops=dict(color="#333", size=10)
        )
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_weight('bold')

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=card)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=15, pady=(5, 15))