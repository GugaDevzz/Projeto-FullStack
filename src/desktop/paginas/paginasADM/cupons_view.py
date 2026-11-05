import customtkinter as ctk
# IMPORTANTE: Ajuste o import abaixo para apontar para o seu modelo e sua sessão do banco
from DB.models import Cupom  # Exemplo do seu modelo mostrado na imagem
from DB.Banco import SessionLocal
# from DB.Conexao import Sessao # Descomente e ajuste conforme sua conexão

class CuponsView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#FFFFFF", corner_radius=15)

        # Título da Seção
        ctk.CTkLabel(
            self, 
            text="CUPONS DE DESCONTO 🏷️", 
            font=ctk.CTkFont(size=18, weight="bold"), 
            text_color="#3A1A10"
        ).pack(anchor="w", padx=20, pady=15)

        # --- Formulário para Criar Novo Cupom ---
        form_frame = ctk.CTkFrame(self, fg_color="#F3EBE1", corner_radius=10)
        form_frame.pack(fill="x", padx=20, pady=10)

        self.entry_cod = ctk.CTkEntry(
            form_frame, 
            placeholder_text="Código (ex: PROMO50)"
        )
        self.entry_cod.pack(side="left", padx=10, pady=10, expand=True, fill="x")

        self.entry_desc = ctk.CTkEntry(
            form_frame, 
            placeholder_text="Desconto (%)"
        )
        self.entry_desc.pack(side="left", padx=10, pady=10, expand=True, fill="x")

        btn_criar = ctk.CTkButton(
            form_frame, 
            text="Criar Cupom", 
            fg_color="#3A1A10", 
            hover_color="#27120B",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.adicionar_cupom
        )
        btn_criar.pack(side="left", padx=10, pady=10)

        # --- Lista de Cupons ---
        ctk.CTkLabel(
            self, 
            text="Cupons Ativos:", 
            font=ctk.CTkFont(size=14, weight="bold"), 
            text_color="#000"
        ).pack(anchor="w", padx=20, pady=(10, 5))

        # Container rolável para a lista de cupons
        self.lista_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.lista_frame.pack(fill="both", expand=True, padx=20, pady=5)

        # Carrega os dados do banco e renderiza a interface
        self.renderizar_lista()


    def adicionar_cupom(self):
        """Salva o novo cupom diretamente na tabela Cupom do banco."""
        cod = self.entry_cod.get().strip().upper()
        desc = self.entry_desc.get().strip()

        if cod and desc:
            if desc.isdigit():
                desc = f"{desc}% OFF"

            session = SessionLocal()
            try:
                novo_cupom = Cupom(
                    codigo=cod, 
                    desconto=desc, 
                    controle=True  # Inicia ativo por padrão
                )
                session.add(novo_cupom)
                session.commit()
            except Exception as e:
                session.rollback()
                print(f"Erro ao salvar cupom no banco: {e}")
            finally:
                session.close()

            # Limpa os inputs e atualiza a tela
            self.entry_cod.delete(0, "end")
            self.entry_desc.delete(0, "end")
            self.renderizar_lista()

    def alternar_status(self, cupom_id):
        """Alterna o campo 'controle' (True/False) do cupom no banco."""
        session = SessionLocal()
        try:
            cupom = session.query(Cupom).filter_by(id=cupom_id).first()
            if cupom:
                cupom.controle = not cupom.controle
                session.commit()
        except Exception as e:
            session.rollback()
            print(f"Erro ao atualizar status: {e}")
        finally:
            session.close()

        self.renderizar_lista()

    def deletar_cupom(self, cupom_id):
        """Remove o cupom do banco de dados com base no ID."""
        session = SessionLocal()
        try:
            cupom = session.query(Cupom).filter_by(id=cupom_id).first()
            if cupom:
                session.delete(cupom)
                session.commit()
        except Exception as e:
            session.rollback()
            print(f"Erro ao deletar cupom: {e}")
        finally:
            session.close()

        self.renderizar_lista()

    def renderizar_lista(self):
        """Busca todos os registros da tabela Cupom e desenha na tela."""
        for widget in self.lista_frame.winfo_children():
            widget.destroy()

        session = SessionLocal()
        try:
            cupons = session.query(Cupom).all()
        except Exception as e:
            print(f"Erro ao buscar cupons: {e}")
            cupons = []
        finally:
            session.close()

        for item in cupons:
            row = ctk.CTkFrame(self.lista_frame, fg_color="#F9F9F9", height=35)
            row.pack(fill="x", pady=3)

            # Código do Cupom (mapeado para item.codigo)
            ctk.CTkLabel(
                row, 
                text=item.codigo, 
                font=ctk.CTkFont(size=12, weight="bold"), 
                text_color="#000"
            ).pack(side="left", padx=15)

            # Descrição do Desconto (mapeado para item.desconto)
            ctk.CTkLabel(
                row, 
                text=item.desconto if item.desconto else "", 
                font=ctk.CTkFont(size=12), 
                text_color="#555"
            ).pack(side="left", padx=20)

            # Botão de Deletar (Lixeira) usando o ID do banco
            btn_deletar = ctk.CTkButton(
                row,
                text="🗑️",
                font=ctk.CTkFont(size=12),
                fg_color="transparent",
                hover_color="#FDE8E8",
                text_color="#EF4444",
                width=30,
                height=25,
                command=lambda cid=item.id: self.deletar_cupom(cid)
            )
            btn_deletar.pack(side="right", padx=5)

            # Botão de Status (Ativo / Inativo baseado em item.controle)
            is_ativo = bool(item.controle)
            texto_status = "Ativo" if is_ativo else "Inativo"
            cor_texto = "#109811" if is_ativo else "#EF4444"

            btn_status = ctk.CTkButton(
                row,
                text=texto_status,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=cor_texto,
                fg_color="transparent",
                hover_color="#EAEAEA",
                width=60,
                height=25,
                command=lambda cid=item.id: self.alternar_status(cid)
            )
            btn_status.pack(side="right", padx=5)