from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from datetime import datetime
from database import Base

class Imovel(Base):
    __tablename__ = "imoveis"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, index=True)
    bairro = Column(String, index=True)
    cidade = Column(String, default="Guarulhos")
    tipo = Column(String)  # casa, apartamento, kitnet
    preco_aluguel = Column(Float)
    condominio = Column(Float, default=0.0)
    iptu = Column(Float, default=0.0)
    quartos = Column(Integer)
    vagas = Column(Integer, default=0)
    area_m2 = Column(Float)
    link_original = Column(String, unique=True, index=True)
    fonte = Column(String)  # quinto_andar, zap, olx, vivareal
    data_captura = Column(DateTime, default=datetime.utcnow)

class AlertaUsuario(Base):
    __tablename__ = "alertas"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String)
    whatsapp = Column(String)
    bairro = Column(String)
    tipo = Column(String)
    preco_maximo = Column(Float)
    quartos_min = Column(Integer, default=1)
    ativo = Column(Boolean, default=True)
    data_criacao = Column(DateTime, default=datetime.utcnow)