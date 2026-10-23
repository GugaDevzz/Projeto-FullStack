import customtkinter as ctk

class RelatoriosView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#FFFFFF", corner_radius=15)
        
        ctk.CTkLabel(self, text="RELATÓRIOS E GERENCIAL 📊", font=ctk.CTkFont(size=18, weight="bold"), text_color="#3A1A10").pack(anchor="w", padx=20, pady=15)

        cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame.pack(fill="x", padx=20, pady=10)

        # Opções de Relatório
        opts = [
            ("Fechamento Mensal", "Gerar PDF com todas as vendas do mês."),
            ("Curva ABC de Estoque", "Relatório de consumo dos ingredientes."),
            ("Desempenho de Atendimento", "Tempo médio do pedido até a entrega.")
        ]

        for titulo, desc in opts:
            card = ctk.CTkFrame(cards_frame, fg_color="#F3EBE1", corner_radius=10)
            card.pack(fill="x", pady=8)
            
            info_f = ctk.CTkFrame(card, fg_color="transparent")
            info_f.pack(side="left", padx=15, pady=10)
            ctk.CTkLabel(info_f, text=titulo, font=ctk.CTkFont(size=14, weight="bold"), text_color="#000").pack(anchor="w")
            ctk.CTkLabel(info_f, text=desc, font=ctk.CTkFont(size=11), text_color="#555").pack(anchor="w")
            
            ctk.CTkButton(card, text="Exportar PDF", fg_color="#3A1A10", hover_color="#52291B").pack(side="right", padx=15)