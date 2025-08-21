/**
 * Aplicação Principal - Sistema de Gestão de Faturas
 * Moara Energia - Arquivo principal que inicializa o sistema
 */

// Inicialização da aplicação
document.addEventListener("DOMContentLoaded", () => {
    console.log("🚀 Moara Gestão - Sistema carregado com sucesso!");
    
    // Inicializa o sistema
    initializeSystem();
    
    // Carrega dados iniciais
    carregarDashboard();
    
    // Event listeners
    setupEventListeners();
    
    // Inicializa Stripe
    initializeStripe();
});

// Configuração de event listeners globais
function setupEventListeners() {
    // Event listeners específicos da aplicação principal
    setupGlobalEventListeners();
    setupFormSubmissions();
}

// Event listeners globais
function setupGlobalEventListeners() {
    // Filtros de busca
    const searchInput = document.querySelector('.search-bar input');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase();
            filtrarFaturas(query);
        });
    }
    
    // Filtros de status
    const statusFilters = document.querySelectorAll('.status-filter');
    statusFilters.forEach(filter => {
        filter.addEventListener('change', (e) => {
            const status = e.target.value;
            filtrarPorStatus(status);
        });
    });
}

// Configuração de submissões de formulários
function setupFormSubmissions() {
    // Formulário de nova fatura
    const formNovaFatura = document.getElementById('form-nova-fatura');
    if (formNovaFatura) {
        formNovaFatura.addEventListener('submit', async (e) => {
            e.preventDefault();
            await submeterNovaFatura();
        });
    }
    
    // Formulário de edição de fatura
    const formEditarFatura = document.getElementById('form-editar-fatura');
    if (formEditarFatura) {
        formEditarFatura.addEventListener('submit', async (e) => {
            e.preventDefault();
            await submeterEdicaoFatura();
        });
    }
}

// Filtragem de faturas
function filtrarFaturas(query) {
    if (!query.trim()) {
        faturaManager.renderizarFaturas();
        return;
    }
    
    const faturasFiltradas = faturaManager.buscarFaturas({
        cliente: query,
        instalacao: query
    });
    
    faturaManager.renderizarFaturas(faturasFiltradas);
}

// Filtragem por status
function filtrarPorStatus(status) {
    let faturasFiltradas;
    
    switch (status) {
        case 'todas':
            faturasFiltradas = faturaManager.faturas;
            break;
        case 'pendentes':
            faturasFiltradas = faturaManager.faturas.filter(f => !f.ja_pago);
            break;
        case 'pagas':
            faturasFiltradas = faturaManager.faturas.filter(f => f.ja_pago);
            break;
        default:
            faturasFiltradas = faturaManager.faturas;
    }
    
    faturaManager.renderizarFaturas(faturasFiltradas);
}

// Submissão de nova fatura
async function submeterNovaFatura() {
    const formData = new FormData(document.getElementById('form-nova-fatura'));
    const dadosFatura = {
        nome_cliente: formData.get('nome_cliente'),
        documento_cliente: formData.get('documento_cliente'),
        email_cliente: formData.get('email_cliente'),
        numero_instalacao: formData.get('numero_instalacao'),
        valor_total: parseFloat(formData.get('valor_total')),
        mes_referencia: formData.get('mes_referencia'),
        data_vencimento: formData.get('data_vencimento')
    };
    
    try {
        await faturaManager.criarFatura(dadosFatura);
        hideModal('modal-nova-fatura');
        document.getElementById('form-nova-fatura').reset();
        
        // Atualiza dashboard
        await dashboardManager.atualizarDashboard();
        
    } catch (error) {
        console.error('Erro ao criar fatura:', error);
        showNotification('Erro ao criar fatura', 'error');
    }
}

// Submissão de edição de fatura
async function submeterEdicaoFatura() {
    if (!faturaManager.currentFaturaId) return;
    
    const formData = new FormData(document.getElementById('form-editar-fatura'));
    const dadosFatura = {
        nome_cliente: formData.get('edit_nome_cliente'),
        documento_cliente: formData.get('edit_documento_cliente'),
        email_cliente: formData.get('edit_email_cliente'),
        numero_instalacao: formData.get('edit_numero_instalacao'),
        valor_total: parseFloat(formData.get('edit_valor_total')),
        mes_referencia: formData.get('edit_mes_referencia'),
        data_vencimento: formData.get('edit_data_vencimento')
    };
    
    try {
        await faturaManager.atualizarFatura(faturaManager.currentFaturaId, dadosFatura);
        hideModal('modal-editar-fatura');
        
        // Atualiza dashboard
        await dashboardManager.atualizarDashboard();
        
    } catch (error) {
        console.error('Erro ao atualizar fatura:', error);
        showNotification('Erro ao atualizar fatura', 'error');
    }
}

// Inicialização do Stripe
function initializeStripe() {
    try {
        // Verifica se o Stripe está disponível
        if (typeof Stripe !== 'undefined') {
            const stripeConfig = configManager.getStripeConfig();
            stripe = Stripe(stripeConfig.publicKey);
            console.log('✅ Stripe inicializado com sucesso');
        } else {
            console.warn('⚠️ Stripe não está disponível');
        }
    } catch (error) {
        console.error('❌ Erro ao inicializar Stripe:', error);
    }
}

// Funções de utilidade global
function formatarMoeda(valor) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(valor);
}

function formatarData(data) {
    if (!data) return 'N/A';
    
    try {
        const dataObj = new Date(data);
        return dataObj.toLocaleDateString('pt-BR');
    } catch {
        return data;
    }
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Exporta funções para uso global
window.filtrarFaturas = filtrarFaturas;
window.filtrarPorStatus = filtrarPorStatus;
window.submeterNovaFatura = submeterNovaFatura;
window.submeterEdicaoFatura = submeterEdicaoFatura;
window.formatarMoeda = formatarMoeda;
window.formatarData = formatarData;

