/**
 * Core do Sistema de Gestão de Faturas - Moara Energia
 * Funcionalidades principais e inicialização do sistema
 */

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
    setupEnvironmentSelector();
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
}

// Configuração do seletor de ambiente
function setupEnvironmentSelector() {
    const envSelector = document.getElementById('env-selector');
    if (envSelector) {
        envSelector.addEventListener('change', (e) => {
            switchEnvironment(e.target.value);
        });
    }
}

// Funções de utilidade
function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }
}

function hideModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
}

function showSection(sectionId) {
    const sections = document.querySelectorAll('.content-section');
    sections.forEach(section => {
        section.style.display = 'none';
    });
    
    const targetSection = document.getElementById(sectionId);
    if (targetSection) {
        targetSection.style.display = 'block';
    }
}

function getPageTitle(section) {
    const titles = {
        'dashboard': 'Dashboard',
        'clientes': 'Gestão de Clientes',
        'faturas': 'Gestão de Faturas',
        'pagamentos': 'Pagamentos',
        'relatorios': 'Relatórios'
    };
    return titles[section] || 'Dashboard';
}

// Função para mostrar notificações
function showNotification(message, type = 'info') {
    const container = document.getElementById('notification-container');
    if (!container) return;
    
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <span>${message}</span>
        <button onclick="this.parentElement.remove()">×</button>
    `;
    
    container.appendChild(notification);
    
    // Remove automaticamente após 5 segundos
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

// Exporta funções para uso global
window.initializeSystem = initializeSystem;
window.showModal = showModal;
window.hideModal = hideModal;
window.showSection = showSection;
window.showNotification = showNotification; 