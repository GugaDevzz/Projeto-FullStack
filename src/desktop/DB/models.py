from sqlalchemy import Column, Integer, String, Float, ForeignKey
from DB.Banco import Base
from sqlalchemy.orm import relationship

class Funcionario(Base):
    __tablename__ = "funcionario"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100), nullable=False)
    senha = Column(String(255), nullable=False)
    controle = Column(Integer, nullable=False)

class Cliente(Base):
    __tablename__ = "cliente"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(150), unique=True)
    cpf = Column(String(255), nullable=False)
    telefone = Column(String(20), unique=True)
    senha = Column(String(255), nullable=False)

class Pedido(Base):
    __tablename__ = "pedido"

    id = Column(Integer, primary_key=True, autoincrement=True)
    num_mesa = Column(Integer, nullable=False)
    status = Column(String(50), nullable=False)
    valor_final = Column(Float, default=0.0)
    nome_cliente = Column(String(100), nullable=True)
    descricao = Column(String(255), nullable=True) 

    # Relacionamento com itens do pedido
    itens = relationship("ItemPedido", back_populates="pedido", cascade="all, delete-orphan")


class ItemPedido(Base):
    __tablename__ = "itens_pedido"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fk_id_pedido = Column(Integer, ForeignKey("pedido.id"), nullable=False)
    fk_id_produto = Column(Integer, ForeignKey("produto.id"), nullable=False)
    quantidade = Column(Integer, nullable=False)

    # Relacionamentos
    pedido = relationship("Pedido", back_populates="itens")
    produto = relationship("Produto")


class Produto(Base):
    __tablename__ = "produto"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100), nullable=False)
    descricao = Column(String(255), nullable=True)
    valor = Column(Float, nullable=False)

    # Relacionamentos
    itens_pedido = relationship("ItemPedido", back_populates="produto")
    ingredientes = relationship("ProdutoEstoque", back_populates="produto", cascade="all, delete-orphan")


class ProdutoEstoque(Base):
    __tablename__ = "produto_estoque"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fk_id_produto = Column(Integer, ForeignKey("produto.id"), nullable=False)
    fk_id_estoque = Column(Integer, ForeignKey("ingredientes.id"), nullable=False)
    quantidade_necessaria = Column(Float, nullable=False)

    # Relacionamentos com especificação correta das chaves estrangeiras
    produto = relationship("Produto", back_populates="ingredientes", foreign_keys=[fk_id_produto])
    ingrediente = relationship("Ingredientes", back_populates="produtos_utilizados", foreign_keys=[fk_id_estoque])


class Ingredientes(Base):
    __tablename__ = "ingredientes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100), nullable=False)
    unidade_medida = Column(String(20), nullable=False) 
    quantidade = Column(Float, nullable=False)          
    status = Column(String(20), nullable=False)

    # Relacionamento reverso para a tabela associativa
    produtos_utilizados = relationship("ProdutoEstoque", back_populates="ingrediente", cascade="all, delete-orphan")