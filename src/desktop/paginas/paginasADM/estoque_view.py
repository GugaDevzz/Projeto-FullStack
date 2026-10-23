import customtkinter as ctk
# Importe a sessão e o modelo do seu banco (ajuste o caminho se necessário)
from DB.Banco import SessionLocal as Session
from DB.models import Ingredientes

class ModalItemEstoque(ctk.CTkToplevel):
    def __init__(self, parent, item_dados=None, callback_salvar=None):
        super().__init__(parent)
        
        self.callback_salvar = callback_salvar
        self.item_dados = item_dados

        # Configurações do Pop-up Modal
        self.title("Editar Item" if item_dados else "Adicionar Novo Item")
        self.geometry("400x320")
        self.configure(fg_color="#F3EBE1")
        self.resizable(False, False)
        
        # Garante que o modal fique sobreposto e em foco
        self.transient(parent)
        self.grab_set()

        # Título do Modal
        titulo_txt = "EDITAR ITEM DO ESTOQUE" if item_dados else "NOVO ITEM NO ESTOQUE"
        ctk.CTkLabel(
            self, text=titulo_txt, 
            font=ctk.CTkFont(size=16, weight="bold"), 
            text_color="#3A1A10"
        ).pack(pady=(15, 10))

        # Campos de Entrada
        self.entry_nome = ctk.CTkEntry(self, placeholder_text="Nome (ex: Pão (uni.))", width=320)
        self.entry_nome.pack(pady=8)

        self.entry_qtd = ctk.CTkEntry(self, placeholder_text="Quantidade (ex: 15)", width=320)
        self.entry_qtd.pack(pady=8)

        self.combo_status = ctk.CTkOptionMenu(
            self, 
            values=["Ok", "Atenção", "Crítico"],
            width=320,
            fg_color="#3A1A10",
            button_color="#52291B",
            dropdown_fg_color="#F3EBE1"
        )
        self.combo_status.pack(pady=8)

        # Se for EDIÇÃO, preenche os campos com os dados existentes
        if item_dados:
            self.entry_nome.insert(0, item_dados["nome"])
            self.entry_qtd.insert(0, item_dados["qtd"])
            self.combo_status.set(item_dados["status"])

        # Botão Salvar
        ctk.CTkButton(
            self, 
            text="Salvar Alterações" if item_dados else "Cadastrar Item",
            fg_color="#3A1A10",
            hover_color="#52291B",
            width=320,
            height=35,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.salvar
        ).pack(pady=15)

    def salvar(self):
        nome = self.entry_nome.get()
        qtd = self.entry_qtd.get()
        status = self.combo_status.get()

        if not nome or not qtd:
            return  # Evita salvar se estiver vazio

        # Retorna os dados para a tela principal
        if self.callback_salvar:
            self.callback_salvar(nome, qtd, status, self.item_dados)

        self.destroy()


class EstoqueView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#FFFFFF", corner_radius=15)

        # Lista que vai guardar os dados vindos do banco
        self.itens_estoque = []

        # Topo
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(
            header_frame, 
            text="CONTROLE DE ESTOQUE 📦", 
            font=ctk.CTkFont(size=18, weight="bold"), 
            text_color="#3A1A10"
        ).pack(side="left")

        ctk.CTkButton(
            header_frame, 
            text="+ Adicionar Item", 
            fg_color="#3A1A10", 
            hover_color="#52291B",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.abrir_modal_adicionar
        ).pack(side="right")

        # ÁREA ROLÁVEL DOS ITENS
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Carrega do banco e renderiza os itens na tela
        self.atualizar_lista()

    def get_cor_status(self, status):
        coreshash = {
            "Crítico": "#D97706",
            "Atenção": "#F59E0B",
            "Ok": "#10B981"
        }
        return coreshash.get(status, "#000000")

    def carregar_do_banco(self):
        """Busca os itens diretamente na tabela 'estoque' do banco de dados"""
        session = Session()
        try:
            resultados = session.query(Ingredientes).all()
            self.itens_estoque = []
            for item in resultados:
                # Separamos o nome e a unidade caso queira exibir formatado, 
                # ou salvamos inteiro se preferir. Aqui mantemos como string direta.
                self.itens_estoque.append({
                    "id": item.id,
                    "nome": item.nome, 
                    "qtd": round(float(item.quantidade), 2),
                    "status": item.status
                })
        except Exception as e:
            print(f"Erro ao carregar estoque do banco: {e}")
            self.itens_estoque = []
        finally:
            session.close()

    def atualizar_lista(self):
        # Atualiza a lista interna buscando do banco de dados
        self.carregar_do_banco()

        # Limpa os widgets antigos da tela
        for widget in self.scroll.winfo_children():
            widget.destroy()

        # Renderiza cada item na interface
        for item in self.itens_estoque:
            row = ctk.CTkFrame(self.scroll, fg_color="#F9F9F9", height=40)
            row.pack(fill="x", pady=4, padx=5)

            ctk.CTkLabel(
                row, text=item["nome"], 
                font=ctk.CTkFont(size=13, weight="bold"), 
                text_color="#000", width=200, anchor="w"
            ).pack(side="left", padx=15)

            ctk.CTkLabel(
                row, text=item["qtd"], 
                font=ctk.CTkFont(size=12), 
                text_color="#000", width=100
            ).pack(side="left", padx=15)

            ctk.CTkLabel(
                row, text=item["status"], 
                font=ctk.CTkFont(size=12, weight="bold"), 
                text_color=self.get_cor_status(item["status"]), width=100
            ).pack(side="left", padx=15)

            # Botão Editar ligado à função do Modal repassando o item atual
            ctk.CTkButton(
                row, 
                text="Editar", 
                width=60, 
                height=24, 
                fg_color="#C09267",
                hover_color="#A37851",
                font=ctk.CTkFont(size=11, weight="bold"),
                command=lambda item_alvo=item: self.abrir_modal_editar(item_alvo)
            ).pack(side="right", padx=10)

    def abrir_modal_adicionar(self):
        ModalItemEstoque(self, item_dados=None, callback_salvar=self.salvar_item)

    def abrir_modal_editar(self, item):
        ModalItemEstoque(self, item_dados=item, callback_salvar=self.salvar_item)

    def salvar_item(self, nome, qtd, status, item_original=None):
        session = Session()
        try:
            if item_original:
                # Edição: busca o registro no banco pelo ID e atualiza
                item_db = session.query(Ingredientes).filter_by(id=item_original["id"]).first()
                if item_db:
                    item_db.nome = nome
                    item_db.quantidade = round(float(qtd), 2)
                    item_db.status = status
                    session.commit()
            else:
                # Criação: adiciona um novo registro no banco
                novo_item = Ingredientes(
                    nome=nome,
                    quantidade=round(float(qtd), 2),
                    status=status
                )
                session.add(novo_item)
                session.commit()
        except Exception as e:
            session.rollback()
            print(f"Erro ao salvar item no banco: {e}")
        finally:
            session.close()

        # Recarrega a tabela diretamente do banco na tela
        self.atualizar_lista()