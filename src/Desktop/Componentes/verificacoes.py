# from models import Usuario
# from DB.Banco import SessionLocal


# class Verificacoes:

#     @staticmethod
#     def validar_login(nome, senha):
#         # Validação inicial de campos vazios
#         if not nome or not senha:
#             return "Preencha todos os campos!"

#         session = SessionLocal()
        
#         # Consulta no banco pelo usuário
#         usuario_db = session.query(Usuario).filter(Usuario.nome == nome).first()

#         if not usuario_db:
#             return "Usuário não encontrado."

#         if usuario_db.senha != senha:
#             return "Senha incorreta."
#         return "Login realizado com sucesso!"


#     def logout(self):
#         from paginas.pagina_login import CatatauLogin
#         self.destroy()
#         app_principal = CatatauLogin()
#         app_principal.mainloop()


#         # tenta arrumar isso cara, depois apaga esse cara no cozinha e no adm tmj