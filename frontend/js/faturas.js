/**
 * Módulo de Gerenciamento de Faturas - Moara Energia
 * Todas as operações CRUD e lógica de negócio para faturas
 */

// Classe para gerenciar faturas
class FaturaManager {
    constructor() {
        this.faturas = [];
        this.currentFaturaId = null;
    }
    
    // Carrega todas as faturas da API
    async carregarFaturas() {
        try {
            showNotification('Carregando faturas...', 'info');
            
            const response = await fetch(CONFIG.API_BASE_URL + CONFIG.ENDPOINTS.FATURAS);
            
            if (response.ok) {
                this.faturas = await response.json();
                this.renderizarFaturas();
                showNotification(`✅ ${this.faturas.length} faturas carregadas`, 'success');
                return this.faturas;
            } else {
                const errorData = await response.json().catch(() => ({}));
                const errorMessage = errorData.detail || `Erro HTTP ${response.status}`;
                throw new Error(errorMessage);
            }
        } catch (error) {
            console.error('❌ Erro ao carregar faturas:', error);
            
            let errorMessage = 'Erro ao carregar faturas';
            if (error.message.includes('Banco de dados não disponível')) {
                errorMessage = 'Erro de conexão com banco de dados';
            } else if (error.message.includes('Failed to fetch')) {
                errorMessage = 'Erro de conexão com a API';
            }
            
            showNotification(errorMessage, 'error');
            
            // Mostra estado vazio com mensagem de erro
            this.renderizarFaturas([]);
            return [];
        }
    }
    
    // Processa emails para buscar novas faturas
    async processarEmails() {
        try {
            // Mostra loading
            const btnProcessar = document.querySelector('#btn-processar-emails, #btn-processar-emails-faturas');
            if (btnProcessar) {
                const originalText = btnProcessar.innerHTML;
                btnProcessar.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processando...';
                btnProcessar.disabled = true;
            }
            
            // Mostra notificação de início
            showNotification('🚀 Iniciando processamento de emails...', 'info');
            
            // Cria área de logs se não existir
            this.criarAreaLogs();
            
            // Adiciona log inicial
            this.adicionarLog('info', 'Iniciando processamento de emails...');
            
            const response = await fetch(CONFIG.API_BASE_URL + CONFIG.ENDPOINTS.PROCESSAR_EMAIL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                const result = await response.json();
                
                // Adiciona log de resultado
                if (result.status === 'success') {
                    if (result.faturas_processadas > 0) {
                        this.adicionarLog('success', `✅ Processamento concluído: ${result.faturas_processadas} faturas encontradas, ${result.faturas_salvas || 0} salvas`);
                        showNotification(`✅ Processamento concluído: ${result.faturas_processadas} faturas processadas`, 'success');
                    } else {
                        this.adicionarLog('info', 'ℹ️ Nenhuma nova fatura encontrada nos emails');
                        showNotification('ℹ️ Nenhuma nova fatura encontrada nos emails', 'info');
                    }
                } else {
                    this.adicionarLog('error', `❌ Erro no processamento: ${result.message}`);
                    showNotification(`❌ Erro: ${result.message}`, 'error');
                }
                
                // Recarrega as faturas
                await this.carregarFaturas();
                return result;
            } else {
                const errorData = await response.json().catch(() => ({}));
                const errorMessage = errorData.detail || `Erro HTTP ${response.status}`;
                this.adicionarLog('error', `❌ Erro HTTP ${response.status}: ${errorMessage}`);
                throw new Error(errorMessage);
            }
        } catch (error) {
            console.error('❌ Erro ao processar emails:', error);
            
            let errorMessage = 'Erro ao processar emails';
            if (error.message.includes('Banco de dados não disponível')) {
                errorMessage = 'Erro de conexão com banco de dados';
            } else if (error.message.includes('Erro no processamento')) {
                errorMessage = 'Erro interno no processamento';
            } else if (error.message.includes('Failed to fetch')) {
                errorMessage = 'Erro de conexão com a API';
            }
            
            this.adicionarLog('error', `❌ ${errorMessage}`);
            showNotification(errorMessage, 'error');
            return null;
        } finally {
            // Restaura botão
            const btnProcessar = document.querySelector('#btn-processar-emails, #btn-processar-emails-faturas');
            if (btnProcessar) {
                btnProcessar.innerHTML = '<i class="fas fa-envelope"></i> Processar Emails';
                btnProcessar.disabled = false;
            }
        }
    }
    
    // Cria área de logs para mostrar o progresso
    criarAreaLogs() {
        let logsArea = document.getElementById('logs-area');
        if (!logsArea) {
            logsArea = document.createElement('div');
            logsArea.id = 'logs-area';
            logsArea.className = 'logs-area';
            logsArea.innerHTML = `
                <div class="logs-header">
                    <h4><i class="fas fa-terminal"></i> Logs do Processamento</h4>
                    <button onclick="this.parentElement.parentElement.remove()" class="btn-close">×</button>
                </div>
                <div class="logs-content"></div>
            `;
            
            // Insere após o botão de processar emails
            const btnProcessar = document.querySelector('#btn-processar-emails, #btn-processar-emails-faturas');
            if (btnProcessar) {
                btnProcessar.parentNode.insertBefore(logsArea, btnProcessar.nextSibling);
            }
        }
    }
    
    // Adiciona um log à área de logs
    adicionarLog(level, message) {
        const logsArea = document.getElementById('logs-area');
        if (!logsArea) return;
        
        const logsContent = logsArea.querySelector('.logs-content');
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry log-${level}`;
        
        const timestamp = new Date().toLocaleTimeString();
        logEntry.innerHTML = `
            <span class="log-timestamp">${timestamp}</span>
            <span class="log-level">${level.toUpperCase()}</span>
            <span class="log-message">${message}</span>
        `;
        
        logsContent.appendChild(logEntry);
        logsContent.scrollTop = logsContent.scrollHeight;
    }
    
    // Cria uma nova fatura
    async criarFatura(dadosFatura) {
        try {
            const response = await fetch(CONFIG.API_BASE_URL + CONFIG.ENDPOINTS.FATURAS, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(dadosFatura)
            });
            
            if (response.ok) {
                const novaFatura = await response.json();
                this.faturas.push(novaFatura);
                this.renderizarFaturas();
                showNotification('Fatura criada com sucesso', 'success');
                return novaFatura;
            } else {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
        } catch (error) {
            console.error('❌ Erro ao criar fatura:', error);
            showNotification('Erro ao criar fatura', 'error');
            return null;
        }
    }
    
    // Atualiza uma fatura existente
    async atualizarFatura(id, dadosFatura) {
        try {
            const response = await fetch(`${CONFIG.API_BASE_URL}${CONFIG.ENDPOINTS.FATURAS}${id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(dadosFatura)
            });
            
            if (response.ok) {
                const faturaAtualizada = await response.json();
                const index = this.faturas.findIndex(f => f.id === id);
                if (index !== -1) {
                    this.faturas[index] = faturaAtualizada;
                }
                this.renderizarFaturas();
                showNotification('Fatura atualizada com sucesso', 'success');
                return faturaAtualizada;
            } else {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
        } catch (error) {
            console.error('❌ Erro ao atualizar fatura:', error);
            showNotification('Erro ao atualizar fatura', 'error');
            return null;
        }
    }
    
    // Remove uma fatura
    async removerFatura(id) {
        if (!confirm('Tem certeza que deseja remover esta fatura?')) {
            return false;
        }
        
        try {
            const response = await fetch(`${CONFIG.API_BASE_URL}${CONFIG.ENDPOINTS.FATURAS}${id}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                this.faturas = this.faturas.filter(f => f.id !== id);
                this.renderizarFaturas();
                showNotification('Fatura removida com sucesso', 'success');
                return true;
            } else {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
        } catch (error) {
            console.error('❌ Erro ao remover fatura:', error);
            showNotification('Erro ao remover fatura', 'error');
            return false;
        }
    }
    
    // Busca faturas por filtros
    buscarFaturas(filtros = {}) {
        let faturasFiltradas = [...this.faturas];
        
        if (filtros.cliente) {
            faturasFiltradas = faturasFiltradas.filter(f => 
                f.nome_cliente.toLowerCase().includes(filtros.cliente.toLowerCase())
            );
        }
        
        if (filtros.instalacao) {
            faturasFiltradas = faturasFiltradas.filter(f => 
                f.numero_instalacao.includes(filtros.instalacao)
            );
        }
        
        if (filtros.status !== undefined) {
            faturasFiltradas = faturasFiltradas.filter(f => f.ja_pago === filtros.status);
        }
        
        return faturasFiltradas;
    }
    
    // Renderiza a lista de faturas na interface
    renderizarFaturas(faturas = null) {
        const container = document.getElementById('faturas-container');
        if (!container) return;
        
        const faturasParaRenderizar = faturas || this.faturas;
        
        if (faturasParaRenderizar.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-file-invoice-dollar"></i>
                    <h3>Nenhuma fatura encontrada</h3>
                    <p>Clique em "Processar Emails" para buscar novas faturas</p>
                    <div class="empty-state-actions">
                        <button class="btn btn-primary" onclick="faturaManager.processarEmails()">
                            <i class="fas fa-envelope"></i>
                            Processar Emails Agora
                        </button>
                    </div>
                </div>
            `;
            return;
        }
        
        const html = faturasParaRenderizar.map(fatura => this.renderizarFaturaItem(fatura)).join('');
        container.innerHTML = html;
        
        // Adiciona event listeners aos botões
        this.setupFaturaEventListeners();
    }
    
    // Renderiza um item individual de fatura
    renderizarFaturaItem(fatura) {
        const statusClass = fatura.ja_pago ? 'pago' : 'pendente';
        const statusText = fatura.ja_pago ? 'Pago' : 'Pendente';
        const statusIcon = fatura.ja_pago ? 'fa-check-circle' : 'fa-clock';
        
        return `
            <div class="fatura-item ${statusClass}" data-id="${fatura.id}">
                <div class="fatura-header">
                    <div class="fatura-status">
                        <i class="fas ${statusIcon}"></i>
                        <span>${statusText}</span>
                    </div>
                    <div class="fatura-acoes">
                        <button class="btn-edit" onclick="faturaManager.editarFatura(${fatura.id})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn-delete" onclick="faturaManager.removerFatura(${fatura.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
                
                <div class="fatura-content">
                    <div class="fatura-info">
                        <h4>${fatura.nome_cliente}</h4>
                        <p><strong>Instalação:</strong> ${fatura.numero_instalacao}</p>
                        <p><strong>Documento:</strong> ${fatura.documento_cliente}</p>
                        <p><strong>Email:</strong> ${fatura.email_cliente}</p>
                    </div>
                    
                    <div class="fatura-valores">
                        <div class="valor-total">
                            <span class="label">Valor Total</span>
                            <span class="valor">R$ ${fatura.valor_total.toFixed(2)}</span>
                        </div>
                        <div class="mes-referencia">
                            <span class="label">Mês Ref.</span>
                            <span class="valor">${fatura.mes_referencia}</span>
                        </div>
                        <div class="data-vencimento">
                            <span class="label">Vencimento</span>
                            <span class="valor">${fatura.data_vencimento}</span>
                        </div>
                    </div>
                </div>
                
                ${!fatura.ja_pago ? `
                    <div class="fatura-footer">
                        <button class="btn-pagar" onclick="faturaManager.iniciarPagamento(${fatura.id})">
                            <i class="fas fa-credit-card"></i>
                            Pagar Fatura
                        </button>
                    </div>
                ` : ''}
            </div>
        `;
    }
    
    // Configura event listeners para as faturas
    setupFaturaEventListeners() {
        // Event listeners específicos podem ser adicionados aqui
    }
    
    // Inicia o processo de pagamento
    async iniciarPagamento(faturaId) {
        try {
            this.currentFaturaId = faturaId;
            
            const response = await fetch(`${CONFIG.API_BASE_URL}${CONFIG.ENDPOINTS.CHECKOUT}/${faturaId}`, {
                method: 'POST'
            });
            
            if (response.ok) {
                const result = await response.json();
                window.location.href = result.checkout_url;
            } else {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
        } catch (error) {
            console.error('❌ Erro ao iniciar pagamento:', error);
            showNotification('Erro ao iniciar pagamento', 'error');
        }
    }
    
    // Edita uma fatura
    editarFatura(faturaId) {
        const fatura = this.faturas.find(f => f.id === faturaId);
        if (!fatura) return;
        
        // Preenche o modal de edição
        document.getElementById('edit-nome-cliente').value = fatura.nome_cliente;
        document.getElementById('edit-documento-cliente').value = fatura.documento_cliente;
        document.getElementById('edit-email-cliente').value = fatura.email_cliente;
        document.getElementById('edit-numero-instalacao').value = fatura.numero_instalacao;
        document.getElementById('edit-valor-total').value = fatura.valor_total;
        document.getElementById('edit-mes-referencia').value = fatura.mes_referencia;
        document.getElementById('edit-data-vencimento').value = fatura.data_vencimento;
        
        this.currentFaturaId = faturaId;
        showModal('modal-editar-fatura');
    }
}

// Instância global do gerenciador de faturas
const faturaManager = new FaturaManager();

// Exporta para uso global
window.faturaManager = faturaManager; 