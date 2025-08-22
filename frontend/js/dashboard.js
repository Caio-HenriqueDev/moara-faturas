/**
 * Módulo do Dashboard - Moara Energia
 * Gerencia o dashboard principal e estatísticas do sistema
 */

// Classe para gerenciar o dashboard
class DashboardManager {
    constructor() {
        this.stats = {
            totalFaturas: 0,
            faturasPendentes: 0,
            faturasPagas: 0,
            valorTotal: 0,
            valorPendente: 0,
            valorRecebido: 0
        };
    }
    
    // Inicializa o dashboard
    async initialize() {
        await this.carregarEstatisticas();
        this.renderizarDashboard();
        this.setupEventListeners();
    }
    
    // Carrega estatísticas do sistema
    async carregarEstatisticas() {
        try {
            // Carrega faturas para calcular estatísticas
            const faturas = await faturaManager.carregarFaturas();
            
            this.stats.totalFaturas = faturas.length;
            this.stats.faturasPendentes = faturas.filter(f => !f.ja_pago).length;
            this.stats.faturasPagas = faturas.filter(f => f.ja_pago).length;
            
            this.stats.valorTotal = faturas.reduce((sum, f) => sum + f.valor_total, 0);
            this.stats.valorPendente = faturas
                .filter(f => !f.ja_pago)
                .reduce((sum, f) => sum + f.valor_total, 0);
            this.stats.valorRecebido = faturas
                .filter(f => f.ja_pago)
                .reduce((sum, f) => sum + f.valor_total, 0);
                
        } catch (error) {
            console.error('❌ Erro ao carregar estatísticas:', error);
        }
    }
    
    // Renderiza o dashboard
    renderizarDashboard() {
        this.renderizarEstatisticas();
        this.renderizarGraficos();
        this.renderizarFaturasRecentes();
    }
    
    // Renderiza as estatísticas principais
    renderizarEstatisticas() {
        const container = document.getElementById('stats-container');
        if (!container) return;
        
        container.innerHTML = `
            <div class="stat-card">
                <div class="stat-icon">
                    <i class="fas fa-file-invoice-dollar"></i>
                </div>
                <div class="stat-content">
                    <h3>${this.stats.totalFaturas}</h3>
                    <p>Total de Faturas</p>
                </div>
            </div>
            
            <div class="stat-card">
                <div class="stat-icon pending">
                    <i class="fas fa-clock"></i>
                </div>
                <div class="stat-content">
                    <h3>${this.stats.faturasPendentes}</h3>
                    <p>Faturas Pendentes</p>
                </div>
            </div>
            
            <div class="stat-card">
                <div class="stat-icon paid">
                    <i class="fas fa-check-circle"></i>
                </div>
                <div class="stat-content">
                    <h3>${this.stats.faturasPagas}</h3>
                    <p>Faturas Pagas</p>
                </div>
            </div>
            
            <div class="stat-card">
                <div class="stat-icon">
                    <i class="fas fa-dollar-sign"></i>
                </div>
                <div class="stat-content">
                    <h3>R$ ${this.stats.valorTotal.toFixed(2)}</h3>
                    <p>Valor Total</p>
                </div>
            </div>
            
            <div class="stat-card">
                <div class="stat-icon pending">
                    <i class="fas fa-exclamation-triangle"></i>
                </div>
                <div class="stat-content">
                    <h3>R$ ${this.stats.valorPendente.toFixed(2)}</h3>
                    <p>Valor Pendente</p>
                </div>
            </div>
            
            <div class="stat-card">
                <div class="stat-icon paid">
                    <i class="fas fa-hand-holding-usd"></i>
                </div>
                <div class="stat-content">
                    <h3>R$ ${this.stats.valorRecebido.toFixed(2)}</h3>
                    <p>Valor Recebido</p>
                </div>
            </div>
        `;
    }
    
    // Renderiza gráficos (simples por enquanto)
    renderizarGraficos() {
        const container = document.getElementById('charts-container');
        if (!container) return;
        
        // Gráfico de pizza simples para status das faturas
        const chartHtml = `
            <div class="chart-container">
                <h3>Status das Faturas</h3>
                <div class="pie-chart">
                    <div class="chart-segment paid" style="--percentage: ${this.calcularPercentual(this.stats.faturasPagas, this.stats.totalFaturas)}%">
                        <span>Pagas: ${this.stats.faturasPagas}</span>
                    </div>
                    <div class="chart-segment pending" style="--percentage: ${this.calcularPercentual(this.stats.faturasPendentes, this.stats.totalFaturas)}%">
                        <span>Pendentes: ${this.stats.faturasPendentes}</span>
                    </div>
                </div>
            </div>
            
            <div class="chart-container">
                <h3>Valores por Status</h3>
                <div class="bar-chart">
                    <div class="bar-item">
                        <span class="bar-label">Pendente</span>
                        <div class="bar-container">
                            <div class="bar pending" style="width: ${this.calcularPercentual(this.stats.valorPendente, this.stats.valorTotal)}%"></div>
                            <span class="bar-value">R$ ${this.stats.valorPendente.toFixed(2)}</span>
                        </div>
                    </div>
                    <div class="bar-item">
                        <span class="bar-label">Recebido</span>
                        <div class="bar-container">
                            <div class="bar paid" style="width: ${this.calcularPercentual(this.stats.valorRecebido, this.stats.valorTotal)}%"></div>
                            <span class="bar-value">R$ ${this.stats.valorRecebido.toFixed(2)}</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        container.innerHTML = chartHtml;
    }
    
    // Renderiza faturas recentes
    renderizarFaturasRecentes() {
        const container = document.getElementById('recent-faturas-container');
        if (!container) return;
        
        const faturasRecentes = faturaManager.faturas
            .sort((a, b) => new Date(b.data_criacao) - new Date(a.data_criacao))
            .slice(0, 5);
        
        if (faturasRecentes.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-file-invoice-dollar"></i>
                    <h3>Nenhuma fatura encontrada</h3>
                    <p>Processe emails para buscar novas faturas</p>
                </div>
            `;
            return;
        }
        
        const html = `
            <h3>Faturas Recentes</h3>
            <div class="recent-faturas-list">
                ${faturasRecentes.map(fatura => this.renderizarFaturaResumo(fatura)).join('')}
            </div>
        `;
        
        container.innerHTML = html;
    }
    
    // Renderiza resumo de uma fatura para o dashboard
    renderizarFaturaResumo(fatura) {
        const statusClass = fatura.ja_pago ? 'pago' : 'pendente';
        const statusText = fatura.ja_pago ? 'Pago' : 'Pendente';
        const statusIcon = fatura.ja_pago ? 'fa-check-circle' : 'fa-clock';
        
        return `
            <div class="fatura-resumo ${statusClass}">
                <div class="fatura-resumo-header">
                    <span class="fatura-nome">${fatura.nome_cliente}</span>
                    <span class="fatura-status">
                        <i class="fas ${statusIcon}"></i>
                        ${statusText}
                    </span>
                </div>
                <div class="fatura-resumo-details">
                    <span class="instalacao">Inst. ${fatura.numero_instalacao}</span>
                    <span class="valor">R$ ${fatura.valor_total.toFixed(2)}</span>
                    <span class="vencimento">Vence: ${fatura.data_vencimento}</span>
                </div>
            </div>
        `;
    }
    
    // Calcula percentual para gráficos
    calcularPercentual(valor, total) {
        if (total === 0) return 0;
        return Math.round((valor / total) * 100);
    }
    
    // Configura event listeners
    setupEventListeners() {
        // Botão de processar emails
        const btnProcessarEmails = document.getElementById('btn-processar-emails');
        if (btnProcessarEmails) {
            btnProcessarEmails.addEventListener('click', async () => {
                await faturaManager.processarEmails();
                await this.carregarEstatisticas();
                this.renderizarDashboard();
            });
        }
        
        // Botão de atualizar dashboard
        const btnAtualizar = document.getElementById('btn-atualizar-dashboard');
        if (btnAtualizar) {
            btnAtualizar.addEventListener('click', async () => {
                await this.atualizarDashboard();
                showNotification('Dashboard atualizado', 'success');
            });
        }
        

    }
    
    // Atualiza o dashboard
    async atualizarDashboard() {
        await this.carregarEstatisticas();
        this.renderizarDashboard();
    }
    

}

// Instância global do gerenciador do dashboard
const dashboardManager = new DashboardManager();

// Função para carregar o dashboard
async function carregarDashboard() {
    await dashboardManager.initialize();
}

// Exporta para uso global
window.dashboardManager = dashboardManager;
window.carregarDashboard = carregarDashboard; 