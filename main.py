from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import engine, Base, get_db
import models
from ai_service import processar_prompt_usuario
from scraper import buscar_imoveis_reais

# Criar tabelas no banco SQLite ao iniciar
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Aluga.ai Backend - API Brasil com Playwright",
    description="API para busca nacional de imóveis com processamento de linguagem natural via Gemini e Scraping com Playwright",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RequisicaoBuscaNLP(BaseModel):
    prompt: str

class RequisicaoAlerta(BaseModel):
    nome: str
    whatsapp: str
    cidade: str = "Guarulhos"
    bairro: str
    tipo: str
    preco_maximo: float

@app.get("/")
def home():
    return {"status": "online", "projeto": "Aluga.ai Brasil API com Scraping Real"}

@app.post("/api/v1/buscar-nlp")
def buscar_por_linguagem_natural(req: RequisicaoBuscaNLP):
    """
    Recebe um texto livre, extrai os filtros via Gemini e executa o Playwright
    para extrair dados e imagens reais dos portais.
    """
    if not req.prompt:
        raise HTTPException(status_code=400, detail="O prompt não pode estar vazio")

    # 1. Processa a frase com a API do Gemini
    filtros = processar_prompt_usuario(req.prompt)

    # 2. Executa a raspagem real com Playwright
    imoveis_encontrados = buscar_imoveis_reais(
        cidade=filtros.get("cidade", "Guarulhos"),
        estado_uf=filtros.get("estado_uf", "sp"),
        bairro=filtros.get("bairro", "Bosque Maia"),
        preco_max=filtros.get("preco_max", 3000),
        tipo=filtros.get("tipo", "casa")
    )

    return {
        "prompt_original": req.prompt,
        "filtros_extraidos": filtros,
        "imoveis": imoveis_encontrados,
        "mensagem": f"Resultados raspados em tempo real para {filtros.get('tipo')} no bairro {filtros.get('bairro')} em {filtros.get('cidade')}-{filtros.get('estado_uf').upper()}."
    }

@app.post("/api/v1/alertas/cadastrar")
def cadastrar_alerta(alerta: RequisicaoAlerta, db: Session = Depends(get_db)):
    novo_alerta = models.AlertaUsuario(
        nome=alerta.nome,
        whatsapp=alerta.whatsapp,
        bairro=alerta.bairro,
        tipo=alerta.tipo,
        preco_maximo=alerta.preco_maximo
    )
    db.add(novo_alerta)
    db.commit()
    db.refresh(novo_alerta)

    return {
        "sucesso": True,
        "alerta_id": novo_alerta.id,
        "mensagem": f"Alerta ativado para {alerta.nome}! Enviaremos novidades no número {alerta.whatsapp}."
    }

@app.get("/api/v1/alertas/listar")
def listar_alertas(db: Session = Depends(get_db)):
    return db.query(models.AlertaUsuario).filter(models.AlertaUsuario.ativo == True).all()