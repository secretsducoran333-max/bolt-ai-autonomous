// Estado da aplicação
let currentBatchId = null;
let pollingInterval = null;

// Idiomas disponíveis
const LANGUAGES = [
    { code: 'pt-BR', name: 'Português (BR)', flag: '🇧🇷' },
    { code: 'en-US', name: 'English (US)', flag: '🇺🇸' },
    { code: 'es-ES', name: 'Español (ES)', flag: '🇪🇸' },
    { code: 'fr-FR', name: 'Français (FR)', flag: '🇫🇷' },
    { code: 'de-DE', name: 'Deutsch (DE)', flag: '🇩🇪' },
    { code: 'it-IT', name: 'Italiano (IT)', flag: '🇮🇹' }
];

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    renderLanguageSelector();
    setupEventListeners();
});

// Renderizar seletor de idiomas
function renderLanguageSelector() {
    const container = document.getElementById('languageSelector');
    
    LANGUAGES.forEach(lang => {
        const checkbox = document.createElement('div');
        checkbox.className = 'language-checkbox';
        checkbox.innerHTML = `
            <input type="checkbox" id="lang-${lang.code}" value="${lang.code}">
            <span class="language-flag">${lang.flag}</span>
            <label for="lang-${lang.code}">${lang.name}</label>
        `;
        
        checkbox.addEventListener('click', (e) => {
            if (e.target.tagName !== 'INPUT') {
                const input = checkbox.querySelector('input');
                input.checked = !input.checked;
            }
            checkbox.classList.toggle('selected', checkbox.querySelector('input').checked);
        });
        
        container.appendChild(checkbox);
    });
}

// Configurar event listeners
function setupEventListeners() {
    document.getElementById('generateBtn').addEventListener('click', generateBatch);
}

// Obter títulos do textarea
function getTitles() {
    const textarea = document.getElementById('titlesInput');
    const titles = textarea.value
        .split('\n')
        .map(t => t.trim())
        .filter(t => t.length > 0);
    return titles;
}

// Obter idiomas selecionados
function getSelectedLanguages() {
    const checkboxes = document.querySelectorAll('#languageSelector input[type="checkbox"]:checked');
    return Array.from(checkboxes).map(cb => cb.value);
}

// Gerar batch
async function generateBatch() {
    const titles = getTitles();
    const languages = getSelectedLanguages();
    
    // Validações
    if (titles.length === 0) {
        alert('Por favor, insira pelo menos um título.');
        return;
    }
    
    if (languages.length === 0) {
        alert('Por favor, selecione pelo menos um idioma.');
        return;
    }
    
    // Desabilitar botão
    const btn = document.getElementById('generateBtn');
    btn.disabled = true;
    btn.innerHTML = 'Processando... <span class="loading-spinner"></span>';
    
    // Mostrar barra de progresso
    const progressBar = document.getElementById('progressBar');
    progressBar.classList.add('active');
    
    try {
        // Enviar requisição
        const response = await fetch('/generate_batch', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                titles: titles,
                languages: languages,
                batch_size: 5
            })
        });
        
        const data = await response.json();
        currentBatchId = data.batch_id;
        
        // Iniciar polling
        startPolling();
        
    } catch (error) {
        console.error('Erro ao gerar batch:', error);
        alert('Erro ao processar. Tente novamente.');
        resetUI();
    }
}

// Iniciar polling de status
function startPolling() {
    if (pollingInterval) {
        clearInterval(pollingInterval);
    }
    
    pollingInterval = setInterval(async () => {
        await updateBatchStatus();
    }, 2000); // Poll a cada 2 segundos
    
    // Primeira atualização imediata
    updateBatchStatus();
}

// Atualizar status do batch
async function updateBatchStatus() {
    if (!currentBatchId) return;
    
    try {
        const response = await fetch(`/batch_status/${currentBatchId}`);
        const data = await response.json();
        
        // Atualizar barra de progresso
        updateProgressBar(data.progress);
        
        // Atualizar resultados
        updateResults(data.jobs);
        
        // Verificar se completou
        if (data.batch.status === 'completed') {
            clearInterval(pollingInterval);
            resetUI();
        }
        
    } catch (error) {
        console.error('Erro ao atualizar status:', error);
    }
}

// Atualizar barra de progresso
function updateProgressBar(progress) {
    const progressText = document.getElementById('progressText');
    const progressFill = document.getElementById('progressFill');
    
    const percentage = (progress.completed / progress.total) * 100;
    
    progressText.textContent = `Processando: ${progress.completed}/${progress.total} concluídos (${progress.processing} em andamento, ${progress.pending} pendentes, ${progress.failed} falhas)`;
    progressFill.style.width = `${percentage}%`;
}

// Atualizar resultados
function updateResults(jobs) {
    const resultsContainer = document.getElementById('resultsContainer');
    const resultsGrid = document.getElementById('resultsGrid');
    
    // Mostrar container de resultados
    resultsContainer.style.display = 'block';
    
    // Limpar grid
    resultsGrid.innerHTML = '';
    
    // Ordenar jobs por título e idioma
    jobs.sort((a, b) => {
        if (a.title !== b.title) {
            return a.title.localeCompare(b.title);
        }
        return a.language.localeCompare(b.language);
    });
    
    // Renderizar cada job
    jobs.forEach(job => {
        const card = createResultCard(job);
        resultsGrid.appendChild(card);
    });
}

// Criar card de resultado
function createResultCard(job) {
    const card = document.createElement('div');
    card.className = 'result-card';
    card.id = `job-${job.id}`;
    
    const lang = LANGUAGES.find(l => l.code === job.language);
    const langFlag = lang ? lang.flag : '🌐';
    const langName = lang ? lang.name : job.language;
    
    const statusClass = `status-${job.status}`;
    const statusText = {
        'pending': 'Pendente',
        'processing': 'Processando',
        'completed': 'Concluído',
        'failed': 'Falhou'
    }[job.status] || job.status;
    
    card.innerHTML = `
        <div class="result-header" onclick="toggleResultBody('${job.id}')">
            <div class="result-title">
                ${langFlag} ${job.title}
            </div>
            <div>
                <span class="result-language">${langName}</span>
                <span class="status-badge ${statusClass}">${statusText}</span>
            </div>
        </div>
        <div class="result-body" id="body-${job.id}">
            ${renderResultBody(job)}
        </div>
    `;
    
    return card;
}

// Renderizar corpo do resultado
function renderResultBody(job) {
    if (job.status === 'pending' || job.status === 'processing') {
        return `
            <div style="text-align: center; padding: 20px;">
                <div class="loading-spinner" style="margin: 0 auto;"></div>
                <p style="margin-top: 15px; color: #666;">Processando...</p>
            </div>
        `;
    }
    
    if (job.status === 'failed') {
        return `
            <div style="text-align: center; padding: 20px; color: #dc3545;">
                <p>❌ Erro ao processar</p>
                <p style="font-size: 0.9em; margin-top: 10px;">${job.error || 'Erro desconhecido'}</p>
            </div>
        `;
    }
    
    if (job.status === 'completed') {
        return `
            <div class="script-container">
                <label class="script-label">📝 Roteiro:</label>
                <div class="script-text" id="script-${job.id}">${job.script}</div>
                <button class="btn-copy" onclick="copyScript('${job.id}')">📋 Copiar Roteiro</button>
            </div>
            
            <div class="audio-container">
                <label class="script-label">🎵 Áudio:</label>
                <audio class="audio-player" controls>
                    <source src="${job.audio_url}" type="audio/mpeg">
                    Seu navegador não suporta o elemento de áudio.
                </audio>
                <a href="${job.audio_url}" download class="btn-download">⬇️ Baixar Áudio</a>
            </div>
        `;
    }
    
    return '';
}

// Toggle corpo do resultado (accordion)
function toggleResultBody(jobId) {
    const body = document.getElementById(`body-${jobId}`);
    body.classList.toggle('active');
}

// Copiar roteiro
function copyScript(jobId) {
    const scriptElement = document.getElementById(`script-${jobId}`);
    const text = scriptElement.textContent;
    
    navigator.clipboard.writeText(text).then(() => {
        // Feedback visual
        const btn = event.target;
        const originalText = btn.textContent;
        btn.textContent = '✅ Copiado!';
        btn.style.background = '#28a745';
        
        setTimeout(() => {
            btn.textContent = originalText;
            btn.style.background = '#667eea';
        }, 2000);
    }).catch(err => {
        console.error('Erro ao copiar:', err);
        alert('Erro ao copiar roteiro');
    });
}

// Resetar UI
function resetUI() {
    const btn = document.getElementById('generateBtn');
    btn.disabled = false;
    btn.textContent = '🚀 Gerar Conteúdo em Lote';
    
    const progressBar = document.getElementById('progressBar');
    progressBar.classList.remove('active');
}

// Função para processar título individual (compatibilidade com versão antiga)
async function generateContent() {
    const titleInput = document.getElementById('titleInput');
    const languageSelect = document.getElementById('languageSelect');
    
    if (!titleInput || !languageSelect) {
        console.log('Modo individual não disponível - usando modo batch');
        return;
    }
    
    const title = titleInput.value.trim();
    const language = languageSelect.value;
    
    if (!title) {
        alert('Por favor, insira um título.');
        return;
    }
    
    // Usar endpoint de batch com um único título
    document.getElementById('titlesInput').value = title;
    
    // Selecionar apenas o idioma escolhido
    document.querySelectorAll('#languageSelector input[type="checkbox"]').forEach(cb => {
        cb.checked = cb.value === language;
        cb.parentElement.classList.toggle('selected', cb.checked);
    });
    
    await generateBatch();
}

// Polling de job individual (compatibilidade)
async function pollJobStatus(jobId) {
    try {
        const response = await fetch(`/job_status/${jobId}`);
        const job = await response.json();
        
        if (job.status === 'completed' || job.status === 'failed') {
            return job;
        }
        
        // Continuar polling
        await new Promise(resolve => setTimeout(resolve, 2000));
        return await pollJobStatus(jobId);
        
    } catch (error) {
        console.error('Erro ao verificar status:', error);
        throw error;
    }
}
