import os
import uuid
import time
from datetime import datetime
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel

app = FastAPI()

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

# Roteiros de demonstração por idioma
DEMO_SCRIPTS = {
    "pt-BR": """Fala, galera! Hoje vou ensinar como fazer {titulo}. 

Olha só, mano, isso aqui é tipo assim, super fácil de fazer, saca? O João, meu vizinho aqui da favela do Rio, me ensinou esse truque e cara, mudou minha vida!

Primeiro, você vai precisar de alguns ingredientes básicos. Nada muito complicado, pode comprar tudo no mercadinho da esquina mesmo. A dica de ouro é: não tenha pressa, vai com calma que dá certo.

O segredo tá nos detalhes, mano. Muita gente erra porque quer fazer correndo. Mas se você seguir essas dicas, garanto que vai ficar show de bola!

E aí, curtiu? Deixa nos comentários se funcionou pra você! Valeu, galera!""",
    
    "en-US": """Hey guys! Today I'm gonna show you how to do {titulo}.

So, like, this is literally the easiest thing ever, you know what I mean? My buddy Mike from downtown Manhattan showed me this trick and dude, it's a total game changer!

First off, you're gonna need some basic stuff. Nothing too crazy, you can grab everything at your local store. The key thing is: don't rush it, take your time and you'll be fine.

The secret is in the details, dude. A lot of people mess up because they're in a hurry. But if you follow these tips, I guarantee you it's gonna turn out awesome!

So yeah, did you like it? Let me know in the comments if it worked for you! Peace out!""",
    
    "es-ES": """¡Hola, tíos! Hoy os voy a enseñar cómo hacer {titulo}.

Ostras, esto es flipante de fácil, ¿vale? Mi colega Carlos del barrio de Malasaña me enseñó este truco y tío, me cambió la vida por completo.

Primero, vais a necesitar algunos ingredientes básicos. Nada del otro mundo, podéis comprar todo en el súper de la esquina. El consejo de oro es: no tengáis prisa, hacedlo con calma que sale bien.

El secreto está en los detalles, tíos. Mucha gente la lía porque quiere hacerlo corriendo. Pero si seguís estos consejos, os garantizo que va a quedar de lujo.

¿Y qué? ¿Os ha gustado? Dejadme en los comentarios si os ha funcionado. ¡Hasta luego!""",
    
    "fr-FR": """Salut les gars ! Aujourd'hui je vais vous montrer comment faire {titulo}.

Putain, c'est grave facile, en fait. Mon pote Pierre du Marais m'a montré cette astuce et voilà, ça a changé ma vie !

D'abord, vous allez avoir besoin de quelques trucs de base. Rien de fou, vous pouvez tout acheter au supermarché du coin. Le conseil en or c'est : ne vous précipitez pas, prenez votre temps et ça va le faire.

Le secret c'est dans les détails, les gars. Beaucoup de gens se plantent parce qu'ils veulent aller trop vite. Mais si vous suivez ces conseils, je vous garantis que ça va être nickel !

Alors, ça vous a plu ? Dites-moi dans les commentaires si ça a marché pour vous ! À plus !""",
    
    "de-DE": """Hey Leute! Heute zeige ich euch, wie man {titulo} macht.

Also, das ist echt krass einfach, genau. Mein Kumpel Hans aus Kreuzberg hat mir diesen Trick gezeigt und halt, das hat mein Leben verändert!

Zuerst braucht ihr ein paar grundlegende Sachen. Nichts Verrücktes, ihr könnt alles im Supermarkt um die Ecke kaufen. Der goldene Tipp ist: Lasst euch Zeit, macht es in Ruhe, dann klappt's.

Das Geheimnis liegt in den Details, Leute. Viele Leute machen Fehler, weil sie es zu schnell machen wollen. Aber wenn ihr diese Tipps befolgt, garantiere ich euch, dass es super wird!

Also, hat's euch gefallen? Schreibt in die Kommentare, ob es bei euch funktioniert hat! Tschüss!""",
    
    "it-IT": """Ciao ragazzi! Oggi vi mostro come fare {titulo}.

Dai, questa cosa è boh, facilissima, cioè. Il mio amico Marco di Trastevere mi ha insegnato questo trucco e vabbè, mi ha cambiato la vita!

Prima di tutto, vi servono alcune cose base. Niente di che, potete comprare tutto al supermercato sotto casa. Il consiglio d'oro è: non abbiate fretta, fatelo con calma che viene bene.

Il segreto sta nei dettagli, ragazzi. Tanta gente sbaglia perché vuole fare di corsa. Ma se seguite questi consigli, vi garantisco che verrà benissimo!

Allora, vi è piaciuto? Scrivetemi nei commenti se ha funzionato per voi! Ciao!"""
}

def processar_job_individual(job_id: str, titulo: str, idioma: str):
    """Processa um job individual (roteiro + áudio) - VERSÃO DEMO"""
    try:
        # Atualizar status para "processing"
        jobs_db[job_id]["status"] = "processing"
        jobs_db[job_id]["updated_at"] = datetime.now().isoformat()
        
        # Simular tempo de processamento
        time.sleep(2)
        
        # Gerar roteiro de demonstração
        template = DEMO_SCRIPTS.get(idioma, DEMO_SCRIPTS["en-US"])
        roteiro = template.format(titulo=titulo)
        
        jobs_db[job_id]["script"] = roteiro
        
        # Simular geração de áudio (criar arquivo vazio de demonstração)
        audio_filename = f"{job_id}.mp3"
        audio_path = f"static/audio/{audio_filename}"
        
        # Criar arquivo de áudio de demonstração (vazio)
        with open(audio_path, "wb") as f:
            f.write(b"")  # Arquivo vazio para demonstração
        
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
        # Simular geração de áudio
        time.sleep(1)
        
        audio_filename = f"{job_id}.mp3"
        audio_path = f"static/audio/{audio_filename}"
        
        with open(audio_path, "wb") as f:
            f.write(b"")
        
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
    uvicorn.run(app, host="0.0.0.0", port=8001)
