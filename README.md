# ⚡ Bolt AI - Gerador de Roteiros e Áudios em Lote

Ferramenta de produtividade para criar roteiros e áudios para vídeos com suporte a **processamento em lote** e **adaptação cultural autêntica** em múltiplos idiomas.

## 🎯 Características Principais

### ✨ Processamento em Lote
- Processe **múltiplos títulos** de uma só vez
- Gere conteúdo em **múltiplos idiomas** simultaneamente
- Processamento paralelo (até 5 jobs simultâneos)
- Interface organizada com cards/accordions para cada resultado

### 🌍 Adaptação Cultural Autêntica
**IMPORTANTE:** Não fazemos tradução! Cada idioma recebe um roteiro 100% ORIGINAL com:

- **Nuances culturais específicas** (gírias, expressões locais)
- **Nomes típicos da cultura** (João para PT-BR, Pierre para FR-FR, Carlos para ES-ES)
- **Referências culturais locais** (lugares, comidas, costumes)
- **Contexto cultural autêntico** para cada idioma

### 🎵 Geração de Áudio
- Síntese de voz com vozes específicas para cada idioma
- Player de áudio integrado
- Download de arquivos MP3

## 🚀 Tecnologias Utilizadas

### Backend
- **FastAPI** - Framework web moderno e rápido
- **OpenAI API** - Geração de roteiros (GPT-4.1-mini) e áudios (TTS-1)
- **ThreadPoolExecutor** - Processamento paralelo de jobs
- **Pydantic** - Validação de dados

### Frontend
- **HTML5/CSS3** - Interface moderna e responsiva
- **JavaScript (Vanilla)** - Lógica de interação sem frameworks
- **Polling** - Atualização em tempo real do status dos jobs

## 📋 Idiomas Suportados

| Idioma | Código | Voz | Contexto Cultural |
|--------|--------|-----|-------------------|
| 🇧🇷 Português (BR) | `pt-BR` | alloy | Brasil, favela do Rio de Janeiro |
| 🇺🇸 English (US) | `en-US` | echo | New York City, downtown Manhattan |
| 🇪🇸 Español (ES) | `es-ES` | fable | Madrid, España, barrio de Malasaña |
| 🇫🇷 Français (FR) | `fr-FR` | onyx | Paris, dans le Marais |
| 🇩🇪 Deutsch (DE) | `de-DE` | nova | Berlin, Deutschland, in Kreuzberg |
| 🇮🇹 Italiano (IT) | `it-IT` | shimmer | Roma, Italia, nel quartiere Trastevere |

## 🛠️ Instalação e Execução

### Pré-requisitos
- Python 3.11+
- Chave de API da OpenAI configurada em `OPENAI_API_KEY`

### Passos

1. **Clone o repositório**
```bash
git clone https://github.com/secretsducoran333-max/bolt-ai-autonomous.git
cd bolt-ai-autonomous
```

2. **Instale as dependências**
```bash
pip3 install -r requirements.txt
```

3. **Configure a variável de ambiente**
```bash
export OPENAI_API_KEY="sua-chave-api-aqui"
```

4. **Execute a aplicação**
```bash
python3 main.py
```

5. **Acesse no navegador**
```
http://localhost:8000
```

## 📖 Como Usar

### Interface Web

1. **Digite os títulos** - Um por linha no campo de texto
2. **Selecione os idiomas** - Marque os checkboxes dos idiomas desejados
3. **Clique em "Gerar Conteúdo em Lote"** - O processamento começará
4. **Acompanhe o progresso** - Barra de progresso mostra status em tempo real
5. **Visualize os resultados** - Cards organizados por título e idioma
6. **Copie roteiros** - Botão para copiar texto
7. **Ouça/Baixe áudios** - Player integrado e botão de download

### Exemplo de Uso

**Entrada:**
```
Como fazer um bolo de chocolate
Dicas para economizar dinheiro
Benefícios da meditação
```

**Idiomas selecionados:** 🇧🇷 Português (BR), 🇺🇸 English (US), 🇪🇸 Español (ES)

**Resultado:** 9 jobs (3 títulos × 3 idiomas), cada um com roteiro único e áudio

## 🔌 API Endpoints

### POST `/generate_batch`
Processa múltiplos títulos em múltiplos idiomas

**Request:**
```json
{
  "titles": ["Título 1", "Título 2"],
  "languages": ["pt-BR", "en-US"],
  "batch_size": 5
}
```

**Response:**
```json
{
  "batch_id": "uuid-do-batch",
  "job_ids": ["uuid-job-1", "uuid-job-2", ...],
  "total_jobs": 4
}
```

### GET `/batch_status/{batch_id}`
Retorna o status de um batch e todos os seus jobs

**Response:**
```json
{
  "batch": {
    "id": "uuid-do-batch",
    "status": "processing",
    "total_jobs": 4,
    "completed_jobs": 2,
    "failed_jobs": 0
  },
  "jobs": [...],
  "progress": {
    "completed": 2,
    "failed": 0,
    "processing": 1,
    "pending": 1,
    "total": 4
  }
}
```

### GET `/job_status/{job_id}`
Retorna o status de um job individual

**Response:**
```json
{
  "id": "uuid-do-job",
  "title": "Como fazer um bolo",
  "language": "pt-BR",
  "status": "completed",
  "script": "Roteiro gerado...",
  "audio_url": "/static/audio/uuid.mp3"
}
```

### POST `/generate_script`
Gera apenas o roteiro (endpoint individual)

**Request:**
```json
{
  "title": "Como fazer um bolo",
  "language": "pt-BR"
}
```

### POST `/generate_audio`
Gera apenas o áudio (endpoint individual)

**Request:**
```json
{
  "script": "Texto do roteiro...",
  "language": "pt-BR"
}
```

## 🏗️ Estrutura do Projeto

```
bolt-ai-autonomous/
├── main.py                 # Backend FastAPI
├── requirements.txt        # Dependências Python
├── README.md              # Documentação
└── static/
    ├── index.html         # Interface principal
    ├── css/
    │   └── style.css      # Estilos
    ├── js/
    │   └── script.js      # Lógica frontend
    └── audio/             # Áudios gerados (criado automaticamente)
```

## 🎨 Recursos da Interface

### Design Moderno
- Gradiente roxo/azul no header
- Cards com hover effects
- Accordions para organizar resultados
- Badges de status coloridos
- Loading spinners animados

### Responsividade
- Layout adaptável para mobile
- Grid responsivo para idiomas
- Interface otimizada para diferentes tamanhos de tela

### UX/UI
- Feedback visual imediato
- Barra de progresso em tempo real
- Botões de copiar com confirmação visual
- Player de áudio integrado
- Download direto de arquivos

## 🔒 Segurança

- API Key da OpenAI configurada via variável de ambiente
- Validação de entrada com Pydantic
- Tratamento de erros em todos os endpoints
- Armazenamento seguro de arquivos de áudio

## 📊 Performance

- **Processamento paralelo:** Até 5 jobs simultâneos
- **Polling eficiente:** Atualização a cada 2 segundos
- **ThreadPoolExecutor:** Gerenciamento otimizado de threads
- **Armazenamento em memória:** Acesso rápido aos dados

## 🐛 Tratamento de Erros

- Jobs com falha são marcados com status `failed`
- Mensagens de erro são exibidas na interface
- Logs detalhados no console
- Retry automático não implementado (pode ser adicionado)

## 🚧 Melhorias Futuras

- [ ] Persistência em banco de dados (SQLite/PostgreSQL)
- [ ] Autenticação de usuários
- [ ] Histórico de batches
- [ ] Exportação em massa (ZIP)
- [ ] Mais idiomas e vozes
- [ ] Customização de prompts
- [ ] Retry automático para jobs com falha
- [ ] Webhooks para notificações
- [ ] Dashboard de analytics

## 📝 Licença

Este projeto é de código aberto e está disponível sob a licença MIT.

## 👨‍💻 Autor

Desenvolvido como ferramenta de produtividade para criadores de conteúdo.

## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues e pull requests.

---

**⚡ Bolt AI** - Criando conteúdo autêntico em múltiplos idiomas, um lote por vez!
