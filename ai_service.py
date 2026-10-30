import os
import json
from google import genai
from google.genai import types
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

# Inicializa o cliente do SDK oficial `google-genai`
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

class FiltroBusca(BaseModel):
    cidade: str = "Guarulhos"
    estado_uf: str = "sp"
    bairro: str
    tipo: str  # casa, apartamento, kitnet, sobrado
    preco_max: float
    quartos: int = 1
    diferenciais: list[str] = []

def processar_prompt_usuario(prompt_texto: str) -> dict:
    """
    Usa o Gemini 2.5 Flash com Structured Outputs para converter texto livre em JSON de busca nacional.
    """
    system_instruction = """
    Você é o cérebro da plataforma 'Aluga.ai Brasil'.
    Sua missão é extrair as intenções de busca do usuário para encontrar imóveis em QUALQUER cidade do Brasil.
    
    Retorne estritamente um JSON padronizado com os campos:
    - cidade (ex: Guarulhos, São Paulo, Rio de Janeiro, Belo Horizonte, Curitiba, Recife)
    - estado_uf (sigla em minúsculo com 2 letras: sp, rj, mg, pr, pe, sc, etc.)
    - bairro (nome exato do bairro)
    - tipo (casa, apartamento, sobrado, kitnet)
    - preco_max (número float do preço limite)
    - quartos (número inteiro)
    - diferenciais (lista de strings, ex: ['quintal', 'pet friendly', 'garagem', 'piscina'])
    
    Regras de fallback:
    - Se a cidade não for informada na frase, defina 'Guarulhos' e 'sp'.
    - Garanta que estado_uf contenha apenas a sigla de 2 letras do estado em minúsculo.
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt_texto,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                response_schema=FiltroBusca,
                temperature=0.1
            )
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Erro no Gemini: {e}")
        return {
            "cidade": "Guarulhos",
            "estado_uf": "sp",
            "bairro": "Bosque Maia",
            "tipo": "casa",
            "preco_max": 3500.0,
            "quartos": 2,
            "diferenciais": []
        }