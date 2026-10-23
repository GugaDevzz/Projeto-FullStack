import customtkinter as ctk

class CuponsView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#FFFFFF", corner_radius=15)
        
        ctk.CTkLabel(self, text="CUPONS DE DESCONTO 🏷️", font=ctk.CTkFont(size=18, weight="bold"), text_color="#3A1A10").pack(anchor="w", padx=20, pady=15)

        # Criar Novo Cupom Form
        form_frame = ctk.CTkFrame(self, fg_color="#F3EBE1", corner_radius=10)
        form_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkEntry(form_frame, placeholder_text="Código (ex: PROMO50)").pack(side="left", padx=10, pady=10, expand=True, fill="x")
        ctk.CTkEntry(form_frame, placeholder_text="Desconto (%)").pack(side="left", padx=10, pady=10, expand=True, fill="x")
        ctk.CTkButton(form_frame, text="Criar Cupom", fg_color="#3A1A10").pack(side="left", padx=10, pady=10)

        # Lista de Cupons
        ctk.CTkLabel(self, text="Cupons Ativos:", font=ctk.CTkFont(size=14, weight="bold"), text_color="#000").pack(anchor="w", padx=20, pady=(10, 5))
        
        cupons = [("PROMO50", "50% OFF", "Ativo"), ("CATATAU10", "10% OFF", "Ativo"), ("BEMVINDO", "R$ 5,00", "Inativo")]
        for cod, desc, status in cupons:
            row = ctk.CTkFrame(self, fg_color="#F9F9F9", height=35)
            row.pack(fill="x", padx=20, pady=3)
            ctk.CTkLabel(row, text=cod, font=ctk.CTkFont(size=12, weight="bold"), text_color="#000").pack(side="left", padx=15)
            ctk.CTkLabel(row, text=desc, font=ctk.CTkFont(size=12), text_color="#555").pack(side="left", padx=20)
            ctk.CTkLabel(row, text=status, font=ctk.CTkFont(size=11, weight="bold"), text_color="#10B981" if status=="Ativo" else "#EF4444").pack(side="right", padx=15)