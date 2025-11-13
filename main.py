import os
import uuid
import asyncio
from datetime import datetime
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from openai import OpenAI

app = FastAPI()

# Configuração do cliente OpenAI (usando variável de ambiente)
client = OpenAI()

# Armazenamento em memória para jobs e batches
jobs_db: Dict[str, dict] = {}
batches_db: Dict[str, dict] = {}

# ThreadPoolExecutor para processamento paralelo
executor = ThreadPoolExecutor(max_workers=5)

# Configurações culturais por idioma
CULTURAS_POR_IDIOMA = {
    "pt-BR": {
        "nome_exemplo": "João",
        "contexto": "no Brasil, em uma favela do Rio de Janeiro",
        "expressoes": ["mano", "cara", "tipo assim", "saca?"],
        "voz": "alloy"
    },
    "en-US": {
        "nome_exemplo": "Mike",
        "contexto": "in New York City, downtown Manhattan",
        "expressoes": ["dude", "like", "you know", "literally"],
        "voz": "echo"
    },
    "es-ES": {
        "nome_exemplo": "Carlos",
        "contexto": "en Madrid, España, en el barrio de Malasaña",
        "expressoes": ["tío", "vale", "ostras", "flipante"],
        "voz": "fable"
    },
    "fr-FR": {
        "nome_exemplo": "Pierre",
        "contexto": "à Paris, dans le Marais",
        "expressoes": ["putain", "grave", "en fait", "voilà"],
        "voz": "onyx"
    },
    "de-DE": {
        "nome_exemplo": "Hans",
        "contexto": "in Berlin, Deutschland, in Kreuzberg",
        "expressoes": ["krass", "echt", "genau", "halt"],
        "voz": "nova"
    },
    "it-IT": {
        "nome_exemplo": "Marco",
        "contexto": "a Roma, Italia, nel quartiere Trastevere",
        "expressoes": ["dai", "boh", "cioè", "vabbè"],
        "voz": "shimmer"
    }
}

# Modelos de dados
class ScriptRequest(BaseModel):
    title: str
    language: str = "pt-BR"

class AudioRequest(BaseModel):
    script: str
    language: str = "pt-BR"

class BatchRequest(BaseModel):
    titles: List[str]
    languages: List[str]
    batch_size: int = 5

# Funções auxiliares
def gerar_prompt_cultural(titulo: str, idioma: str) -> str:
    """Gera um prompt específico para o idioma com contexto cultural autêntico"""
    cultura = CULTURAS_POR_IDIOMA.get(idioma, CULTURAS_POR_IDIOMA["en-US"])
    
    if idioma == "pt-BR":
        prompt = f"""Você é um roteirista brasileiro criativo. Crie um roteiro ORIGINAL e AUTÊNTICO em português brasileiro sobre o tema: "{titulo}".

IMPORTANTE - Adaptação Cultural Brasileira:
- Use nomes brasileiros típicos (ex: {cultura['nome_exemplo']}, Maria, José)
- Inclua gírias e expressões brasileiras naturais: {', '.join(cultura['expressoes'])}
- Situe a história {cultura['contexto']}
- Use referências culturais brasileiras (comidas, lugares, costumes)
- Tom informal e próximo, como brasileiros falam no dia a dia

O roteiro deve ter entre 150-200 palavras, ser envolvente e soar 100% natural para um brasileiro.
Não traduza de outros idiomas - crie algo ORIGINAL em português brasileiro."""

    elif idioma == "en-US":
        prompt = f"""You are a creative American scriptwriter. Create an ORIGINAL and AUTHENTIC script in American English about: "{titulo}".

IMPORTANT - American Cultural Adaptation:
- Use typical American names (e.g., {cultura['nome_exemplo']}, Sarah, John)
- Include natural American slang and expressions: {', '.join(cultura['expressoes'])}
- Set the story {cultura['contexto']}
- Use American cultural references (foods, places, customs)
- Casual and relatable tone, like Americans speak in everyday life

The script should be 150-200 words, engaging, and sound 100% natural to an American.
Don't translate from other languages - create something ORIGINAL in American English."""

    elif idioma == "es-ES":
        prompt = f"""Eres un guionista español creativo. Crea un guion ORIGINAL y AUTÉNTICO en español de España sobre: "{titulo}".

IMPORTANTE - Adaptación Cultural Española:
- Usa nombres españoles típicos (ej: {cultura['nome_exemplo']}, María, Javier)
- Incluye jerga y expresiones españolas naturales: {', '.join(cultura['expressoes'])}
- Sitúa la historia {cultura['contexto']}
- Usa referencias culturales españolas (comidas, lugares, costumbres)
- Tono informal y cercano, como hablan los españoles en el día a día

El guion debe tener entre 150-200 palabras, ser atractivo y sonar 100% natural para un español.
No traduzcas de otros idiomas - crea algo ORIGINAL en español de España."""

    elif idioma == "fr-FR":
        prompt = f"""Tu es un scénariste français créatif. Crée un script ORIGINAL et AUTHENTIQUE en français sur: "{titulo}".

IMPORTANT - Adaptation Culturelle Française:
- Utilise des prénoms français typiques (ex: {cultura['nome_exemplo']}, Marie, Jean)
- Inclus de l'argot et des expressions françaises naturelles: {', '.join(cultura['expressoes'])}
- Situe l'histoire {cultura['contexto']}
- Utilise des références culturelles françaises (nourriture, lieux, coutumes)
- Ton informel et proche, comme les Français parlent au quotidien

Le script doit faire entre 150-200 mots, être captivant et sonner 100% naturel pour un Français.
Ne traduis pas d'autres langues - crée quelque chose d'ORIGINAL en français."""

    elif idioma == "de-DE":
        prompt = f"""Du bist ein kreativer deutscher Drehbuchautor. Erstelle ein ORIGINALES und AUTHENTISCHES Skript auf Deutsch über: "{titulo}".

WICHTIG - Deutsche Kulturelle Anpassung:
- Verwende typische deutsche Namen (z.B. {cultura['nome_exemplo']}, Anna, Michael)
- Füge natürliche deutsche Slang und Ausdrücke ein: {', '.join(cultura['expressoes'])}
- Setze die Geschichte {cultura['contexto']}
- Verwende deutsche kulturelle Referenzen (Essen, Orte, Bräuche)
- Informeller und nahbarer Ton, wie Deutsche im Alltag sprechen

Das Skript sollte 150-200 Wörter haben, fesselnd sein und 100% natürlich für einen Deutschen klingen.
Übersetze nicht aus anderen Sprachen - erstelle etwas ORIGINALES auf Deutsch."""

    elif idioma == "it-IT":
        prompt = f"""Sei uno sceneggiatore italiano creativo. Crea uno script ORIGINALE e AUTENTICO in italiano su: "{titulo}".

IMPORTANTE - Adattamento Culturale Italiano:
- Usa nomi italiani tipici (es: {cultura['nome_exemplo']}, Giulia, Luca)
- Includi slang ed espressioni italiane naturali: {', '.join(cultura['expressoes'])}
- Ambienta la storia {cultura['contexto']}
- Usa riferimenti culturali italiani (cibo, luoghi, costumi)
- Tono informale e vicino, come parlano gli italiani nella vita quotidiana

Lo script deve essere di 150-200 parole, coinvolgente e suonare 100% naturale per un italiano.
Non tradurre da altre lingue - crea qualcosa di ORIGINALE in italiano."""

    else:
        prompt = f"Create an original script about: {titulo}. Length: 150-200 words."
    
    return prompt

def processar_job_individual(job_id: str, titulo: str, idioma: str):
    """Processa um job individual (roteiro + áudio)"""
    try:
        # Atualizar status para "processing"
        jobs_db[job_id]["status"] = "processing"
        jobs_db[job_id]["updated_at"] = datetime.now().isoformat()
        
        # Gerar roteiro com prompt cultural
        prompt = gerar_prompt_cultural(titulo, idioma)
        
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are a creative scriptwriter who creates authentic, culturally-adapted content."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=500
        )
        
        roteiro = response.choices[0].message.content.strip()
        jobs_db[job_id]["script"] = roteiro
        
        # Gerar áudio
        cultura = CULTURAS_POR_IDIOMA.get(idioma, CULTURAS_POR_IDIOMA["en-US"])
        voz = cultura["voz"]
        
        audio_response = client.audio.speech.create(
            model="tts-1",
            voice=voz,
            input=roteiro
        )
        
        # Salvar áudio
        audio_filename = f"{job_id}.mp3"
        audio_path = f"static/audio/{audio_filename}"
        
        with open(audio_path, "wb") as f:
            f.write(audio_response.content)
        
        jobs_db[job_id]["audio_url"] = f"/static/audio/{audio_filename}"
        jobs_db[job_id]["status"] = "completed"
        jobs_db[job_id]["updated_at"] = datetime.now().isoformat()
        
    except Exception as e:
        jobs_db[job_id]["status"] = "failed"
        jobs_db[job_id]["error"] = str(e)
        jobs_db[job_id]["updated_at"] = datetime.now().isoformat()

# Endpoints
@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve a página HTML principal"""
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/generate_script")
async def generate_script(request: ScriptRequest):
    """Endpoint para gerar roteiro individual"""
    job_id = str(uuid.uuid4())
    
    jobs_db[job_id] = {
        "id": job_id,
        "title": request.title,
        "language": request.language,
        "status": "pending",
        "script": None,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    # Processar em background
    executor.submit(processar_job_individual, job_id, request.title, request.language)
    
    return {"job_id": job_id}

@app.post("/generate_audio")
async def generate_audio(request: AudioRequest):
    """Endpoint para gerar áudio individual"""
    job_id = str(uuid.uuid4())
    
    jobs_db[job_id] = {
        "id": job_id,
        "language": request.language,
        "status": "processing",
        "audio_url": None,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    try:
        cultura = CULTURAS_POR_IDIOMA.get(request.language, CULTURAS_POR_IDIOMA["en-US"])
        voz = cultura["voz"]
        
        audio_response = client.audio.speech.create(
            model="tts-1",
            voice=voz,
            input=request.script
        )
        
        audio_filename = f"{job_id}.mp3"
        audio_path = f"static/audio/{audio_filename}"
        
        with open(audio_path, "wb") as f:
            f.write(audio_response.content)
        
        jobs_db[job_id]["audio_url"] = f"/static/audio/{audio_filename}"
        jobs_db[job_id]["status"] = "completed"
        jobs_db[job_id]["updated_at"] = datetime.now().isoformat()
        
    except Exception as e:
        jobs_db[job_id]["status"] = "failed"
        jobs_db[job_id]["error"] = str(e)
        jobs_db[job_id]["updated_at"] = datetime.now().isoformat()
    
    return {"job_id": job_id}

@app.post("/generate_batch")
async def generate_batch(request: BatchRequest):
    """Endpoint para processamento em lote"""
    batch_id = str(uuid.uuid4())
    job_ids = []
    
    # Criar jobs para cada combinação título × idioma
    for titulo in request.titles:
        for idioma in request.languages:
            job_id = str(uuid.uuid4())
            
            jobs_db[job_id] = {
                "id": job_id,
                "batch_id": batch_id,
                "title": titulo,
                "language": idioma,
                "status": "pending",
                "script": None,
                "audio_url": None,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            job_ids.append(job_id)
    
    # Criar batch
    batches_db[batch_id] = {
        "id": batch_id,
        "job_ids": job_ids,
        "total_jobs": len(job_ids),
        "completed_jobs": 0,
        "failed_jobs": 0,
        "status": "processing",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    # Processar jobs em paralelo (máximo batch_size simultâneos)
    for job_id in job_ids:
        job = jobs_db[job_id]
        executor.submit(processar_job_individual, job_id, job["title"], job["language"])
    
    return {
        "batch_id": batch_id,
        "job_ids": job_ids,
        "total_jobs": len(job_ids)
    }

@app.get("/batch_status/{batch_id}")
async def batch_status(batch_id: str):
    """Retorna o status de um batch"""
    if batch_id not in batches_db:
        raise HTTPException(status_code=404, detail="Batch não encontrado")
    
    batch = batches_db[batch_id]
    jobs = [jobs_db[job_id] for job_id in batch["job_ids"]]
    
    # Atualizar contadores
    completed = sum(1 for job in jobs if job["status"] == "completed")
    failed = sum(1 for job in jobs if job["status"] == "failed")
    processing = sum(1 for job in jobs if job["status"] == "processing")
    pending = sum(1 for job in jobs if job["status"] == "pending")
    
    batch["completed_jobs"] = completed
    batch["failed_jobs"] = failed
    
    # Atualizar status do batch
    if completed + failed == batch["total_jobs"]:
        batch["status"] = "completed"
    
    batch["updated_at"] = datetime.now().isoformat()
    
    return {
        "batch": batch,
        "jobs": jobs,
        "progress": {
            "completed": completed,
            "failed": failed,
            "processing": processing,
            "pending": pending,
            "total": batch["total_jobs"]
        }
    }

@app.get("/job_status/{job_id}")
async def job_status(job_id: str):
    """Retorna o status de um job individual"""
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job não encontrado")
    
    return jobs_db[job_id]

# Montar arquivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
