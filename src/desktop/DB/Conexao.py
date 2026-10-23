# 🚨 ESSENCIAL: Importar o arquivo das suas tabelas para registrá-las no Base
from Banco import Base, engine
from models import Funcionario, Produto, Pedido, ItemPedido, Ingredientes

def criar_tabelas():
    print("Criando tabelas no banco de dados...")
    Base.metadata.create_all(bind=engine)
    print("Tabelas criadas com sucesso!")

if __name__ == "__main__":
    try:
        conexao = engine.connect()
        print("Conexão com SQL Server OK!")
        conexao.close()

        criar_tabelas()
    except Exception as e:
        print(f"Erro: {e}")
