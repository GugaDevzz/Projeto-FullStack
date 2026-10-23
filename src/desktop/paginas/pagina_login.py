import customtkinter as ctk
from PIL import Image, ImageOps
# from Componentes.verificacoes import Verificacoes
from DB.models import Funcionario
from DB.Banco import SessionLocal
from paginas.paginaCozinha.pedidos import CozinhaApp  # Importa a classe da pagina principal
from paginas.paginasADM.pagina_adm import PaginaADM
# from paginas.paginaCozinha.historico import HistoricoApp

# Configurações globais de tema
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")


class CatatauLogin(ctk.CTk):

    def __init__(self):
        super().__init__()

        # Janela Principal
        self.title("Catatau Lanches - Autenticação")
        self.geometry("1200x675")
        self.resizable(False, False)


        # Configuração do Grid principal (50% | 50%)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1, uniform="metade")
        self.grid_columnconfigure(1, weight=1, uniform="metade")

        # Montagem dos componentes
        self.montar_lado_esquerdo_banner()
        self.montar_lado_direito_login()


    def montar_lado_esquerdo_banner(self):
        """LADO ESQUERDO: Imagem de fundo com a logo sobreposta em camadas"""
        self.frame_esquerdo = ctk.CTkFrame(
            self, corner_radius=0, fg_color="transparent"
        )
        self.frame_esquerdo.grid(row=0, column=0, sticky="nsew")

        # 1. CAMADA INFERIOR: Imagem de Fundo (Banner)
        pil_img = Image.open("Statics/banner_login.png")
        pil_img = ImageOps.fit(pil_img, (600, 675), Image.Resampling.LANCZOS)
        
        self.banner_img = ctk.CTkImage(
            light_image=pil_img, dark_image=pil_img, size=(600, 675)
        )

        self.lbl_banner = ctk.CTkLabel(
            self.frame_esquerdo, text="", image=self.banner_img
        )
        # Ocupa 100% da área do frame esquerdo
        self.lbl_banner.place(x=0, y=0, relwidth=1.0, relheight=1.0)

    def montar_lado_direito_login(self):
            self.frame_direito = ctk.CTkFrame(
                self, corner_radius=0, fg_color="#FDF8F2"
            )
            self.frame_direito.grid(row=0, column=1, sticky="nsew")
    
            # Card Central
            self.card = ctk.CTkFrame(
                self.frame_direito,
                corner_radius=28,
                fg_color="#FFFFFF",
                border_width=0,
            )
            self.card.place(
                relx=0.5, rely=0.5, anchor="center", relwidth=0.78, relheight=0.85
            )

        # 2. CAMADA SUPERIOR: Logo Sobreposta
            pil_logo_banner = Image.open("Statics/catatauimg.png")
            
            # Ajuste aqui o tamanho que deseja para a logo no banner (ex: 120x120)
            self.logo_banner_img = ctk.CTkImage(
                light_image=pil_logo_banner, dark_image=pil_logo_banner, size=(80, 80)
            )

            self.lbl_logo_banner = ctk.CTkLabel(
                self.frame_direito, text="", image=self.logo_banner_img
            )
        
            self.lbl_logo_banner.place(relx=0.5, rely=0.15, anchor="center")
            self.lbl_logo_banner.pack(pady=80)

    
            # 1. Título Modificado (Mais moderno)
            self.lbl_titulo = ctk.CTkLabel(
                self.card,
                text="Fazer Login",
                font=ctk.CTkFont(size=26, weight="bold"),
                text_color="#222222",
            )
            self.lbl_titulo.pack(pady=(130, 10))
    
            self.lbl_subtitulo = ctk.CTkLabel(
                self.card,
                text="Bem-vindo ao sistema Catatau",
                font=ctk.CTkFont(size=13),
                text_color="#777777",
            )
            self.lbl_subtitulo.pack(pady=(0, 30))
    
            # 2. Campo Usuário
            self.lbl_user = ctk.CTkLabel(
                self.card,
                text="Usuário",
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="#444444",
            )
            self.lbl_user.pack(anchor="w", padx=45, pady=(0, 4))
    
            self.ent_user = ctk.CTkEntry(
                self.card,
                placeholder_text="Digite seu usuário",
                height=46,
                corner_radius=12,
                fg_color="#F5F5F5",
                border_color="#E0E0E0",
                border_width=1,
                text_color="#000000",
            )
            self.ent_user.pack(fill="x", padx=45, pady=(0, 18))
    
            # 3. Campo Senha
            self.lbl_pass = ctk.CTkLabel(
                self.card,
                text="Senha",
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="#444444",
            )
            self.lbl_pass.pack(anchor="w", padx=45, pady=(0, 4))
    
            self.ent_pass = ctk.CTkEntry(
                self.card,
                placeholder_text="Digite sua senha",
                show="•",
                height=46,
                corner_radius=12,
                fg_color="#F5F5F5",
                border_color="#E0E0E0",
                border_width=1,
                text_color="#000000",
            )
            self.ent_pass.pack(fill="x", padx=45, pady=(0, 25))

            self.lbl_aviso = ctk.CTkLabel(
                    self.card,
                    text="",
                    font=ctk.CTkFont(size=13),
                    text_color="#FF0000",
                )
            self.lbl_aviso.pack(pady=(0, 30))
            
            # 4. Botão ENTRAR
            self.btn_login = ctk.CTkButton(
                self.card,
                text="ENTRAR",
                height=48,
                corner_radius=12,
                fg_color="#FF7338",
                hover_color="#E55D24",
                font=ctk.CTkFont(size=14, weight="bold"),
                command=self.acao_login  # Vincula o evento do botão
            )
            self.btn_login.pack(fill="x", padx=45, pady=(0, 20))

    def acao_login(self):
         
        usuario = self.ent_user.get().strip()
        senha = self.ent_pass.get().strip()

        # Reseta o estilo dos campos a cada tentativa
        self.ent_user.configure(border_color="#E0E0E0")
        self.ent_pass.configure(border_color="#E0E0E0")
        self.lbl_aviso.configure(text="")

        if not usuario or not senha:
            self.ent_user.configure(border_color="#FF3333")
            self.ent_pass.configure(border_color="#FF3333")
            return self.lbl_aviso.configure(text="Preencha todos os campos!")

        session = SessionLocal()

        try:
            # Consulta no banco pelo usuário
            usuario_db = session.query(Funcionario).filter(Funcionario.nome == usuario).first()

            if not usuario_db:
                self.ent_user.configure(border_color="#FF3333")
                return self.lbl_aviso.configure(text="Usuário não encontrado.")

            if usuario_db.senha != senha:
                self.ent_pass.configure(border_color="#FF3333")
                return self.lbl_aviso.configure(text="Senha incorreta.")

            self.destroy()   # Fecha a janela de login atual
            if usuario_db.controle == 1:
                # Abre a pagina principal (paginaadm)
                app_principal = PaginaADM()
                app_principal.mainloop()
            if usuario_db.controle == 2:    
                # Abre a pagina principal (CozinhaApp)
                app_principal = CozinhaApp()
                app_principal.mainloop()
        finally:
            session.close()
     
        