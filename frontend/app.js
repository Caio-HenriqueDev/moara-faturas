// Moara Gestão - Sistema de Gestão de Faturas
// JavaScript completamente funcional para interface moderna

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

// Variáveis globais
let stripe = null;
let currentFaturaId = null;
let allFaturas = [];

// Inicialização do sistema
function initializeSystem() {
    setupNavigation();
    setupMobileMenu();
    setupNotifications();
    setupModals();
}

// Configuração da navegação
function setupNavigation() {
    const navItems = document.querySelectorAll('.nav-item a');
    const pageTitle = document.getElementById('page-title');
    
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            
            navItems.forEach(nav => nav.parentElement.classList.remove('active'));
            item.parentElement.classList.add('active');
            
            const section = item.getAttribute('href').substring(1);
            pageTitle.textContent = getPageTitle(section);
            showSection(section);
        });
    });
}

// Configuração do menu mobile
function setupMobileMenu() {
    const menuToggle = document.getElementById('menu-toggle');
    const sidebar = document.querySelector('.sidebar');
    
    if (menuToggle) {
        menuToggle.addEventListener('click', () => {
            sidebar.classList.toggle('open');
        });
    }
    
    document.addEventListener('click', (e) => {
        if (window.innerWidth <= 1024) {
            if (!sidebar.contains(e.target) && !menuToggle.contains(e.target)) {
                sidebar.classList.remove('open');
            }
        }
    });
}

// Configuração das notificações
function setupNotifications() {
    const container = document.getElementById("notification-container");
    if (container) {
        container.innerHTML = '';
    }
}

// Configuração dos modais
function setupModals() {
    // Modal Nova Fatura
    const modalNovaFatura = document.getElementById('modal-nova-fatura');
    const btnNovaFatura = document.getElementById('nova-fatura');
    const closeNovaFatura = document.getElementById('close-nova-fatura');
    const cancelarNovaFatura = document.getElementById('cancelar-nova-fatura');
    
    if (btnNovaFatura) {
        btnNovaFatura.addEventListener('click', () => showModal('modal-nova-fatura'));
    }
    if (closeNovaFatura) {
        closeNovaFatura.addEventListener('click', () => hideModal('modal-nova-fatura'));
    }
    if (cancelarNovaFatura) {
        cancelarNovaFatura.addEventListener('click', () => hideModal('modal-nova-fatura'));
    }
    
    // Modal Novo Cliente
    const modalNovoCliente = document.getElementById('modal-novo-cliente');
    const btnNovoCliente = document.getElementById('novo-cliente');
    const closeNovoCliente = document.getElementById('close-novo-cliente');
    const cancelarNovoCliente = document.getElementById('cancelar-novo-cliente');
    
    if (btnNovoCliente) {
        btnNovoCliente.addEventListener('click', () => showModal('modal-novo-cliente'));
    }
    if (closeNovoCliente) {
        closeNovoCliente.addEventListener('click', () => hideModal('modal-novo-cliente'));
    }
    if (cancelarNovoCliente) {
        cancelarNovoCliente.addEventListener('click', () => hideModal('modal-novo-cliente'));
    }
    
    // Modal Detalhes Fatura
    const modalDetalhesFatura = document.getElementById('modal-detalhes-fatura');
    const closeDetalhesFatura = document.getElementById('close-detalhes-fatura');
    const fecharDetalhes = document.getElementById('fechar-detalhes');
    
    if (closeDetalhesFatura) {
        closeDetalhesFatura.addEventListener('click', () => hideModal('modal-detalhes-fatura'));
    }
    if (fecharDetalhes) {
        fecharDetalhes.addEventListener('click', () => hideModal('modal-detalhes-fatura'));
    }
    
    // Modal Confirmação
    const modalConfirmacao = document.getElementById('modal-confirmacao');
    const closeConfirmacao = document.getElementById('close-confirmacao');
    const cancelarAcao = document.getElementById('cancelar-acao');
    
    if (closeConfirmacao) {
        closeConfirmacao.addEventListener('click', () => hideModal('modal-confirmacao'));
    }
    if (cancelarAcao) {
        cancelarAcao.addEventListener('click', () => hideModal('modal-confirmacao'));
    }
    
    // Fechar modais ao clicar fora
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                hideModal(modal.id);
            }
        });
    });
}

// Event listeners principais
function setupEventListeners() {
    // Botão processar emails
    const btnProcessarEmails = document.getElementById('processar-emails');
    if (btnProcessarEmails) {
        btnProcessarEmails.addEventListener('click', processarEmails);
    }
    
    // Botão ver todas faturas
    const btnVerTodasFaturas = document.getElementById('ver-todas-faturas');
    if (btnVerTodasFaturas) {
        btnVerTodasFaturas.addEventListener('click', () => {
            showSection('faturas');
            document.querySelector('.nav-item a[href="#faturas"]').parentElement.classList.add('active');
            document.querySelector('.nav-item a[href="#dashboard"]').parentElement.classList.remove('active');
        });
    }
    
    // Formulário nova fatura
    const formNovaFatura = document.getElementById('form-nova-fatura');
    if (formNovaFatura) {
        formNovaFatura.addEventListener('submit', handleNovaFatura);
    }
    
    // Formulário novo cliente
    const formNovoCliente = document.getElementById('form-novo-cliente');
    if (formNovoCliente) {
        formNovoCliente.addEventListener('submit', handleNovoCliente);
    }
    
    // Filtros de faturas
    const searchFilter = document.getElementById('search-filter');
    const statusFilter = document.getElementById('status-filter');
    const dateFilter = document.getElementById('date-filter');
    const limparFiltros = document.getElementById('limpar-filtros');
    
    if (searchFilter) {
        searchFilter.addEventListener('input', aplicarFiltros);
    }
    if (statusFilter) {
        statusFilter.addEventListener('change', aplicarFiltros);
    }
    if (dateFilter) {
        dateFilter.addEventListener('change', aplicarFiltros);
    }
    if (limparFiltros) {
        limparFiltros.addEventListener('click', limparFiltrosFaturas);
    }
    
    // Botão pagar fatura no modal
    const btnPagarFaturaModal = document.getElementById('pagar-fatura-modal');
    if (btnPagarFaturaModal) {
        btnPagarFaturaModal.addEventListener('click', () => {
            if (currentFaturaId) {
                pagarFatura(currentFaturaId);
            }
        });
    }
}

// Inicializa Stripe
function initializeStripe() {
    // Em produção, use sua chave pública do Stripe
    const stripePublicKey = 'pk_test_...'; // Substitua pela sua chave pública
    
    if (typeof Stripe !== 'undefined' && stripePublicKey !== 'pk_test_...') {
        stripe = Stripe(stripePublicKey);
        console.log('✅ Stripe inicializado');
    } else {
        console.log('⚠️ Stripe não configurado - usando modo de demonstração');
    }
}

// Carrega dados do dashboard
async function carregarDashboard() {
    try {
        console.log("📊 Carregando dados do dashboard...");
        
        await carregarEstatisticas();
        await carregarFaturasRecentes();
        
    } catch (err) {
        console.error("❌ Erro ao carregar dashboard:", err);
        mostrarNotificacao("Erro ao carregar dashboard: " + err.message, "error");
    }
}

// Carrega estatísticas do dashboard
async function carregarEstatisticas() {
    try {
        const response = await fetch(getApiUrl("/faturas/"));
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const faturas = await response.json();
        allFaturas = faturas; // Guarda para uso global
        
        const totalClientes = new Set(faturas.map(f => f.numero_instalacao)).size;
        const faturasPendentes = faturas.filter(f => !f.ja_pago).length;
        const receitaTotal = faturas.reduce((sum, f) => sum + (f.valor_total || 0), 0);
        const pagamentosConfirmados = faturas.filter(f => f.ja_pago).length;
        
        document.getElementById('total-clientes').textContent = totalClientes;
        document.getElementById('faturas-pendentes').textContent = faturasPendentes;
        document.getElementById('receita-total').textContent = `R$ ${receitaTotal.toFixed(2)}`;
        document.getElementById('pagamentos-confirmados').textContent = pagamentosConfirmados;
        
        const changeElements = document.querySelectorAll('.stat-change');
        changeElements.forEach((el, index) => {
            if (index === 1) {
                el.textContent = `${faturasPendentes} pendentes`;
                el.className = `stat-change ${faturasPendentes > 0 ? 'negative' : 'positive'}`;
            }
        });
        
    } catch (err) {
        console.error("❌ Erro ao carregar estatísticas:", err);
    }
}

// Carrega faturas recentes para o dashboard
async function carregarFaturasRecentes() {
    try {
        const response = await fetch(getApiUrl("/faturas/"));
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const faturas = await response.json();
        console.log(`📋 ${faturas.length} faturas encontradas:`, faturas);
        
        const container = document.getElementById("faturas-container");
        
        document.getElementById("loading").style.display = "none";
        document.getElementById("no-faturas").style.display = "none";
        
        container.querySelectorAll(".fatura-card").forEach(card => card.remove());
        
        if (faturas.length === 0) {
            document.getElementById("no-faturas").style.display = "block";
            return;
        }
        
        const faturasRecentes = faturas.slice(0, 5);
        faturasRecentes.forEach((fatura, index) => {
            criarCardFaturaDashboard(fatura, index);
        });
        
    } catch (err) {
        console.error("❌ Erro ao carregar faturas:", err);
        mostrarNotificacao("Erro ao carregar faturas: " + err.message, "error");
        
        document.getElementById("loading").style.display = "none";
        document.getElementById("no-faturas").style.display = "block";
        document.getElementById("no-faturas").innerHTML = "❌ Erro ao carregar faturas";
    }
}

// Cria card de fatura para o dashboard
function criarCardFaturaDashboard(fatura, index) {
    const container = document.getElementById("faturas-container");
    
    const card = document.createElement("div");
    card.className = "fatura-card";
    card.setAttribute("data-fatura-id", fatura.id);
    
    const valorFormatado = fatura.valor_total ? 
        `R$ ${parseFloat(fatura.valor_total).toFixed(2)}` : 
        "Valor não informado";
    
    const statusPagamento = fatura.ja_pago ? 
        '<span class="status-badge status-pago">PAGO</span>' : 
        '<span class="status-badge status-pendente">PENDENTE</span>';
    
    card.innerHTML = `
        <div class="fatura-card-header">
            <h3>${fatura.nome_cliente || "Cliente não identificado"}</h3>
            ${statusPagamento}
        </div>
        
        <div class="fatura-card-content">
            <div class="fatura-info">
                <span class="info-label">Instalação:</span>
                <span class="info-value">${fatura.numero_instalacao || "Não informado"}</span>
            </div>
            
            <div class="fatura-info">
                <span class="info-label">Mês Ref.:</span>
                <span class="info-value">${fatura.mes_referencia || "Não informado"}</span>
            </div>
            
            <div class="fatura-info">
                <span class="info-label">Vencimento:</span>
                <span class="info-value">${fatura.data_vencimento || "Não informado"}</span>
            </div>
            
            <div class="fatura-valor">
                <span class="valor-label">Valor Total:</span>
                <span class="valor-value">${valorFormatado}</span>
            </div>
        </div>
        
        <div class="fatura-card-actions">
            <button class="btn btn-sm btn-primary" onclick="pagarFatura(${fatura.id})" ${fatura.ja_pago ? 'disabled' : ''}>
                ${fatura.ja_pago ? '✅ Pago' : '💳 Pagar'}
            </button>
            
            <button class="btn btn-sm btn-outline" onclick="verDetalhesFatura(${fatura.id})">
                <i class="fas fa-eye"></i>
            </button>
        </div>
    `;
    
    container.appendChild(card);
}

// Processa emails automaticamente
async function processarEmails() {
        const btn = document.getElementById("processar-emails");
    if (!btn) return;
    
        btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processando...';

        try {
        console.log("📧 Iniciando processamento automático de e-mails...");
        
        const response = await fetch(getApiUrl("/processar_email/"), {
                method: "POST",
            });

            if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
        console.log("✅ Processamento concluído:", data);
        
        mostrarNotificacao("✅ " + (data.message || "Processamento concluído com sucesso!"), "success");
        
        await carregarDashboard();
        
        } catch (err) {
        console.error("❌ Erro ao processar e-mails:", err);
        mostrarNotificacao("❌ Erro: " + err.message, "error");
        } finally {
            btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-envelope"></i> Processar Novos E-mails';
    }
}

// Mostra seção específica
function showSection(sectionName) {
    const sections = ['dashboard-content', 'clientes-content', 'faturas-content', 'pagamentos-content', 'relatorios-content'];
    sections.forEach(section => {
        const element = document.getElementById(section);
        if (element) element.style.display = 'none';
    });
    
    const targetSection = document.getElementById(`${sectionName}-content`);
    if (targetSection) {
        targetSection.style.display = 'block';
        
        if (sectionName === 'faturas') {
            carregarFaturasTabela();
        } else if (sectionName === 'clientes') {
            carregarClientes();
        } else if (sectionName === 'pagamentos') {
            carregarPagamentos();
        } else if (sectionName === 'relatorios') {
            carregarRelatorios();
        }
    }
}

// Carrega faturas para tabela
async function carregarFaturasTabela() {
    try {
        const response = await fetch(getApiUrl("/faturas/"));
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const faturas = await response.json();
        allFaturas = faturas;
        const tbody = document.getElementById('faturas-table-body');
        
        if (!tbody) return;
        
        tbody.innerHTML = '';
        
        faturas.forEach(fatura => {
            const row = document.createElement('tr');
            const valorFormatado = fatura.valor_total ? 
                `R$ ${parseFloat(fatura.valor_total).toFixed(2)}` : 
                "N/A";
            
            const status = fatura.ja_pago ? 
                '<span class="status-badge status-pago">PAGO</span>' : 
                '<span class="status-badge status-pendente">PENDENTE</span>';
            
            row.innerHTML = `
                <td>${fatura.nome_cliente || "N/A"}</td>
                <td>${fatura.numero_instalacao || "N/A"}</td>
                <td>${fatura.mes_referencia || "N/A"}</td>
                <td>${fatura.data_vencimento || "N/A"}</td>
                <td>${valorFormatado}</td>
                <td>${status}</td>
                <td>
                    <button class="btn btn-sm btn-primary" onclick="pagarFatura(${fatura.id})" ${fatura.ja_pago ? 'disabled' : ''}>
                        ${fatura.ja_pago ? '✅ Pago' : '💳 Pagar'}
                    </button>
                    <button class="btn btn-sm btn-outline" onclick="verDetalhesFatura(${fatura.id})">
                        <i class="fas fa-eye"></i>
                    </button>
                </td>
            `;
            
            tbody.appendChild(row);
        });
        
    } catch (err) {
        console.error("❌ Erro ao carregar faturas para tabela:", err);
        mostrarNotificacao("Erro ao carregar faturas: " + err.message, "error");
    }
}

// Carrega clientes
async function carregarClientes() {
    try {
        const response = await fetch(getApiUrl("/faturas/"));
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const faturas = await response.json();
        const clientesGrid = document.getElementById('clientes-grid');

        if (!clientesGrid) return;

        const clientes = {};
        faturas.forEach(fatura => {
            const key = fatura.numero_instalacao;
            if (!clientes[key]) {
                clientes[key] = {
                    nome: fatura.nome_cliente,
                    instalacao: fatura.numero_instalacao,
                    documento: fatura.documento_cliente,
                    email: fatura.email_cliente,
                    faturas: []
                };
            }
            clientes[key].faturas.push(fatura);
        });
        
        clientesGrid.innerHTML = '';
        Object.values(clientes).forEach(cliente => {
            const clienteCard = document.createElement('div');
            clienteCard.className = 'cliente-card';
            clienteCard.innerHTML = `
                <div class="cliente-header">
                    <h3>${cliente.nome || "Cliente não identificado"}</h3>
                    <span class="cliente-instalacao">${cliente.instalacao}</span>
                </div>
                <div class="cliente-info">
                    <p><strong>Documento:</strong> ${cliente.documento || "N/A"}</p>
                    <p><strong>Email:</strong> ${cliente.email || "N/A"}</p>
                    <p><strong>Total de Faturas:</strong> ${cliente.faturas.length}</p>
                </div>
            `;
            clientesGrid.appendChild(clienteCard);
        });
        
    } catch (err) {
        console.error("❌ Erro ao carregar clientes:", err);
        mostrarNotificacao("Erro ao carregar clientes: " + err.message, "error");
    }
}

// Carrega pagamentos
async function carregarPagamentos() {
    try {
        const response = await fetch(getApiUrl("/faturas/"));
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const faturas = await response.json();
        const pagamentosGrid = document.getElementById('pagamentos-grid');
        
        if (!pagamentosGrid) return;
        
        const faturasPagas = faturas.filter(f => f.ja_pago);
        
        pagamentosGrid.innerHTML = '';
        
        if (faturasPagas.length === 0) {
            pagamentosGrid.innerHTML = `
                <div class="no-data">
                    <i class="fas fa-credit-card"></i>
                    <h3>Nenhum pagamento encontrado</h3>
                    <p>Processe e-mails ou crie faturas para começar.</p>
                </div>
            `;
            return;
        }
        
        faturasPagas.forEach(fatura => {
            const pagamentoCard = document.createElement('div');
            pagamentoCard.className = 'pagamento-card';
            pagamentoCard.innerHTML = `
                <h3>${fatura.nome_cliente || "Cliente não identificado"}</h3>
                <p><strong>Instalação:</strong> ${fatura.numero_instalacao}</p>
                <p><strong>Valor:</strong> R$ ${fatura.valor_total?.toFixed(2) || "N/A"}</p>
                <p><strong>Mês Ref.:</strong> ${fatura.mes_referencia || "N/A"}</p>
                <span class="status-badge status-pago">PAGO</span>
            `;
            pagamentosGrid.appendChild(pagamentoCard);
        });
        
    } catch (err) {
        console.error("❌ Erro ao carregar pagamentos:", err);
        mostrarNotificacao("Erro ao carregar pagamentos: " + err.message, "error");
    }
}

// Carrega relatórios
async function carregarRelatorios() {
    try {
        const response = await fetch(getApiUrl("/faturas/"));
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const faturas = await response.json();
        
        // Simula gráficos (em produção, use Chart.js ou similar)
        const faturasChart = document.getElementById('faturas-chart');
        const receitaChart = document.getElementById('receita-chart');
        
        if (faturasChart) {
            faturasChart.innerHTML = `
                <div class="chart-placeholder">
                    <i class="fas fa-chart-pie"></i>
                    <p>Gráfico de Faturas</p>
                    <small>Total: ${faturas.length} | Pendentes: ${faturas.filter(f => !f.ja_pago).length} | Pagas: ${faturas.filter(f => f.ja_pago).length}</small>
                </div>
            `;
        }
        
        if (receitaChart) {
            const receitaTotal = faturas.reduce((sum, f) => sum + (f.valor_total || 0), 0);
            const receitaPaga = faturas.filter(f => f.ja_pago).reduce((sum, f) => sum + (f.valor_total || 0), 0);
            
            receitaChart.innerHTML = `
                <div class="chart-placeholder">
                    <i class="fas fa-chart-line"></i>
                    <p>Receita Total</p>
                    <small>Total: R$ ${receitaTotal.toFixed(2)} | Recebido: R$ ${receitaPaga.toFixed(2)}</small>
                </div>
            `;
        }
        
    } catch (err) {
        console.error("❌ Erro ao carregar relatórios:", err);
        mostrarNotificacao("Erro ao carregar relatórios: " + err.message, "error");
    }
}

// Aplica filtros às faturas
function aplicarFiltros() {
    const searchTerm = document.getElementById('search-filter')?.value.toLowerCase() || '';
    const statusFilter = document.getElementById('status-filter')?.value || '';
    const dateFilter = document.getElementById('date-filter')?.value || '';
    
    const tbody = document.getElementById('faturas-table-body');
    if (!tbody) return;
    
    const rows = tbody.querySelectorAll('tr');
    
    rows.forEach(row => {
        const cliente = row.cells[0]?.textContent.toLowerCase() || '';
        const instalacao = row.cells[1]?.textContent.toLowerCase() || '';
        const status = row.cells[5]?.textContent.toLowerCase() || '';
        const vencimento = row.cells[3]?.textContent || '';
        
        let show = true;
        
        // Filtro de busca
        if (searchTerm && !cliente.includes(searchTerm) && !instalacao.includes(searchTerm)) {
            show = false;
        }
        
        // Filtro de status
        if (statusFilter) {
            if (statusFilter === 'pendente' && status.includes('pago')) {
                show = false;
            } else if (statusFilter === 'pago' && status.includes('pendente')) {
                show = false;
            }
        }
        
        // Filtro de data
        if (dateFilter && vencimento !== dateFilter) {
            show = false;
        }
        
        row.style.display = show ? '' : 'none';
    });
}

// Limpa filtros
function limparFiltrosFaturas() {
    document.getElementById('search-filter').value = '';
    document.getElementById('status-filter').value = '';
    document.getElementById('date-filter').value = '';
    aplicarFiltros();
}

// Funções auxiliares
function getPageTitle(section) {
    const titles = {
        'dashboard': 'Dashboard',
        'clientes': 'Gestão de Clientes',
        'faturas': 'Gestão de Faturas',
        'pagamentos': 'Histórico de Pagamentos',
        'relatorios': 'Relatórios e Analytics'
    };
    return titles[section] || 'Dashboard';
}

// Funções de pagamento
async function pagarFatura(faturaId) {
    try {
        currentFaturaId = faturaId;
        
        if (!stripe) {
            mostrarNotificacao("💳 Stripe não configurado - usando modo de demonstração", "info");
            simularPagamento(faturaId);
            return;
        }
        
        mostrarNotificacao("💳 Iniciando pagamento...", "info");
        
        const response = await fetch(getApiUrl(`/create-checkout-session/${faturaId}`), {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const session = await response.json();
        
        // Redireciona para o Stripe
        window.location.href = session.checkout_url;
        
    } catch (err) {
        console.error("❌ Erro ao iniciar pagamento:", err);
        mostrarNotificacao("❌ Erro ao iniciar pagamento: " + err.message, "error");
        
        // Fallback para modo de demonstração
        simularPagamento(faturaId);
    }
}

// Simula pagamento (modo de demonstração)
function simularPagamento(faturaId) {
    mostrarConfirmacao(
        "Simular Pagamento",
        "Deseja simular o pagamento desta fatura? (Modo de demonstração)",
        () => {
            // Simula sucesso
            setTimeout(() => {
                mostrarNotificacao("✅ Pagamento simulado com sucesso!", "success");
                carregarDashboard();
                carregarFaturasTabela();
            }, 1000);
        }
    );
}

// Ver detalhes da fatura
async function verDetalhesFatura(faturaId) {
    try {
        const fatura = allFaturas.find(f => f.id === faturaId);
        if (!fatura) {
            mostrarNotificacao("❌ Fatura não encontrada", "error");
            return;
        }
        
        currentFaturaId = faturaId;
        
        const modal = document.getElementById('modal-detalhes-fatura');
        const content = document.getElementById('detalhes-fatura-content');
        const btnPagar = document.getElementById('pagar-fatura-modal');
        
        content.innerHTML = `
            <div class="fatura-detalhes">
                <h4>${fatura.nome_cliente || "Cliente não identificado"}</h4>
                
                <div class="detalhes-grid">
                    <div class="detalhe-item">
                        <strong>Instalação:</strong>
                        <span>${fatura.numero_instalacao || "N/A"}</span>
                    </div>
                    
                    <div class="detalhe-item">
                        <strong>Documento:</strong>
                        <span>${fatura.documento_cliente || "N/A"}</span>
                    </div>
                    
                    <div class="detalhe-item">
                        <strong>Email:</strong>
                        <span>${fatura.email_cliente || "N/A"}</span>
                    </div>
                    
                    <div class="detalhe-item">
                        <strong>Mês Ref.:</strong>
                        <span>${fatura.mes_referencia || "N/A"}</span>
                    </div>
                    
                    <div class="detalhe-item">
                        <strong>Vencimento:</strong>
                        <span>${fatura.data_vencimento || "N/A"}</span>
                    </div>
                    
                    <div class="detalhe-item">
                        <strong>Valor Total:</strong>
                        <span class="valor-destaque">R$ ${fatura.valor_total?.toFixed(2) || "N/A"}</span>
                    </div>
                    
                    <div class="detalhe-item">
                        <strong>Status:</strong>
                        <span class="status-badge ${fatura.ja_pago ? 'status-pago' : 'status-pendente'}">
                            ${fatura.ja_pago ? 'PAGO' : 'PENDENTE'}
                        </span>
                    </div>
                </div>
            </div>
        `;
        
        // Mostra/esconde botão de pagar
        if (btnPagar) {
            btnPagar.style.display = fatura.ja_pago ? 'none' : 'inline-flex';
        }
        
        showModal('modal-detalhes-fatura');
        
    } catch (err) {
        console.error("❌ Erro ao carregar detalhes:", err);
        mostrarNotificacao("❌ Erro ao carregar detalhes: " + err.message, "error");
    }
}

// Handlers de formulários
async function handleNovaFatura(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const faturaData = {
        nome_cliente: formData.get('nome_cliente'),
        documento_cliente: formData.get('documento_cliente'),
        email_cliente: formData.get('email_cliente'),
        numero_instalacao: formData.get('numero_instalacao'),
        valor_total: parseFloat(formData.get('valor_total')),
        mes_referencia: formData.get('mes_referencia'),
        data_vencimento: formData.get('data_vencimento'),
        ja_pago: false
    };
    
    try {
        // Em produção, enviaria para o backend
        mostrarNotificacao("✅ Fatura criada com sucesso! (Modo de demonstração)", "success");
        
        // Adiciona à lista local
        faturaData.id = Date.now(); // ID temporário
        allFaturas.push(faturaData);
        
        hideModal('modal-nova-fatura');
        e.target.reset();
        
        // Recarrega dados
        await carregarDashboard();
        
    } catch (err) {
        console.error("❌ Erro ao criar fatura:", err);
        mostrarNotificacao("❌ Erro ao criar fatura: " + err.message, "error");
    }
}

async function handleNovoCliente(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const clienteData = {
        nome: formData.get('nome'),
        documento: formData.get('documento'),
        email: formData.get('email'),
        telefone: formData.get('telefone'),
        endereco: formData.get('endereco')
    };
    
    try {
        // Em produção, enviaria para o backend
        mostrarNotificacao("✅ Cliente cadastrado com sucesso! (Modo de demonstração)", "success");
        
        hideModal('modal-novo-cliente');
        e.target.reset();
        
        // Recarrega clientes se estiver na seção
        if (document.getElementById('clientes-content').style.display !== 'none') {
            await carregarClientes();
        }
        
    } catch (err) {
        console.error("❌ Erro ao cadastrar cliente:", err);
        mostrarNotificacao("❌ Erro ao cadastrar cliente: " + err.message, "error");
    }
}

// Funções de modal
function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('show');
        document.body.style.overflow = 'hidden';
    }
}

function hideModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('show');
        document.body.style.overflow = '';
    }
}

// Função de confirmação
function mostrarConfirmacao(titulo, mensagem, onConfirm) {
    const modal = document.getElementById('modal-confirmacao');
    const tituloEl = document.getElementById('confirmacao-titulo');
    const mensagemEl = document.getElementById('confirmacao-mensagem');
    const btnConfirmar = document.getElementById('confirmar-acao');
    
    if (tituloEl) tituloEl.textContent = titulo;
    if (mensagemEl) mensagemEl.textContent = mensagem;
    
    if (btnConfirmar) {
        btnConfirmar.onclick = () => {
            onConfirm();
            hideModal('modal-confirmacao');
        };
    }
    
    showModal('modal-confirmacao');
}

// Sistema de notificações
function mostrarNotificacao(mensagem, tipo = "info") {
    const container = document.getElementById("notification-container");
    if (!container) return;
    
    const notificacaoAnterior = container.querySelector(".notification");
    if (notificacaoAnterior) {
        notificacaoAnterior.remove();
    }
    
    const notificacao = document.createElement("div");
    notificacao.className = `notification ${tipo}`;
    notificacao.textContent = mensagem;
    
    container.appendChild(notificacao);
    
    setTimeout(() => {
        if (notificacao.parentNode) {
            notificacao.remove();
        }
    }, 5000);
}

// Atualização automática
function iniciarAtualizacaoAutomatica() {
    setInterval(() => {
        if (document.getElementById('dashboard-content').style.display !== 'none') {
            carregarDashboard();
        }
    }, 30000);
}

// Inicia atualização automática
iniciarAtualizacaoAutomatica();

// Funções globais para uso nos botões HTML
window.pagarFatura = pagarFatura;
window.verDetalhesFatura = verDetalhesFatura;

