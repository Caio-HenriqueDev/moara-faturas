/**
 * Configuração do Frontend - Sistema de Gestão de Faturas
 * Moara Energia - Gerencia configurações e ambiente da aplicação
 */

// Configuração base da aplicação
const CONFIG = {
    // Informações da aplicação
    APP: {
        NAME: 'Moara Energia',
        VERSION: '2.0.0',
        DESCRIPTION: 'Sistema de Gestão de Faturas'
    },
    
    // Configurações do Stripe
    STRIPE: {
        PUBLIC_KEY: process.env.STRIPE_PUBLIC_KEY || 'pk_test_your_stripe_public_key_here',
        SUCCESS_URL: '/success',
        CANCEL_URL: '/cancel'
    },
    
    // Configurações de ambiente
    ENVIRONMENTS: {
        local: {
            name: 'Local',
            apiUrl: 'http://localhost:8000',
            icon: '🏠'
        },
        vercel: {
            name: 'Vercel Atual',
            apiUrl: 'https://moara-solar-l7whuoy74-diretoriamoovestudio-5505s-projects.vercel.app',
            icon: '☁️'
        },
        vercel2: {
            name: 'Vercel Backup',
            apiUrl: 'https://moara-solar-48c8u9u4c-diretoriamoovestudio-5505s-projects.vercel.app',
            icon: '☁️'
        }
    }
};

// Classe para gerenciar configurações
class ConfigManager {
    constructor() {
        this.currentEnvironment = this.loadSavedEnvironment();
        this.apiBaseUrl = this.getCurrentApiUrl();
        this.endpoints = this.buildEndpoints();
    }
    
    // Carrega ambiente salvo
    loadSavedEnvironment() {
        return localStorage.getItem('selected_environment') || 'local';
    }
    
    // Obtém URL da API atual
    getCurrentApiUrl() {
        return CONFIG.ENVIRONMENTS[this.currentEnvironment]?.apiUrl || CONFIG.ENVIRONMENTS.local.apiUrl;
    }
    
    // Constrói endpoints baseados na URL atual
    buildEndpoints() {
        return {
            ROOT: '/',
            HEALTH: '/health',
            FATURAS: '/faturas/',
            PROCESSAR_EMAIL: '/processar_email/',

            CHECKOUT: '/create-checkout-session',
            WEBHOOK: '/stripe-webhook/',
            DOCS: '/docs'
        };
    }
    
    // Alterna entre ambientes
    switchEnvironment(env) {
        if (!CONFIG.ENVIRONMENTS[env]) {
            console.warn(`Ambiente '${env}' não reconhecido`);
            return false;
        }
        
        this.currentEnvironment = env;
        this.apiBaseUrl = this.getCurrentApiUrl();
        
        // Salva a preferência
        localStorage.setItem('selected_environment', env);
        
        // Atualiza o seletor visual
        this.updateEnvironmentSelector();
        
        console.log(`🌍 Ambiente alterado para: ${this.apiBaseUrl}`);
        
        // Dispara evento de mudança de ambiente
        this.dispatchEnvironmentChangeEvent();
        
        return true;
    }
    
    // Atualiza o seletor visual de ambiente
    updateEnvironmentSelector() {
        const envSelector = document.getElementById('env-selector');
        if (envSelector) {
            envSelector.value = this.currentEnvironment;
        }
    }
    
    // Dispara evento de mudança de ambiente
    dispatchEnvironmentChangeEvent() {
        const event = new CustomEvent('environmentChanged', {
            detail: {
                environment: this.currentEnvironment,
                apiUrl: this.apiBaseUrl
            }
        });
        document.dispatchEvent(event);
    }
    
    // Obtém URL completa da API
    getApiUrl(endpoint) {
        return this.apiBaseUrl + endpoint;
    }
    
    // Testa conectividade da API
    async testApiConnection() {
        try {
            const response = await fetch(this.getApiUrl('/health'));
            if (response.ok) {
                const data = await response.json();
                console.log('✅ API conectada:', data);
                return { success: true, data };
            } else {
                console.log('❌ API retornou erro:', response.status);
                return { success: false, error: `HTTP ${response.status}` };
            }
        } catch (error) {
            console.log('❌ Erro ao conectar com API:', error);
            return { success: false, error: error.message };
        }
    }
    
    // Obtém informações do ambiente atual
    getEnvironmentInfo() {
        const env = this.currentEnvironment;
        const envConfig = CONFIG.ENVIRONMENTS[env];
        
        return {
            environment: env,
            name: envConfig.name,
            apiUrl: envConfig.apiUrl,
            icon: envConfig.icon,
            isProduction: env !== 'local'
        };
    }
    
    // Obtém configuração do Stripe
    getStripeConfig() {
        return {
            ...CONFIG.STRIPE,
            publicKey: CONFIG.STRIPE.PUBLIC_KEY
        };
    }
    
    // Valida configurações
    validateConfig() {
        const issues = [];
        
        if (!this.apiBaseUrl) {
            issues.push('URL da API não configurada');
        }
        
        if (!CONFIG.STRIPE.PUBLIC_KEY || CONFIG.STRIPE.PUBLIC_KEY.includes('your_stripe_public_key')) {
            issues.push('Chave pública do Stripe não configurada');
        }
        
        return issues;
    }
}

// Instância global do gerenciador de configuração
const configManager = new ConfigManager();

// Cria variáveis globais para compatibilidade com código existente
const CONFIG = {
    API_BASE_URL: configManager.apiBaseUrl,
    ENDPOINTS: configManager.endpoints
};

// Atualiza as variáveis globais quando o ambiente muda
document.addEventListener('environmentChanged', (event) => {
    CONFIG.API_BASE_URL = event.detail.apiUrl;
    CONFIG.ENDPOINTS = configManager.buildEndpoints();
    console.log('🌍 Configuração atualizada:', CONFIG);
});

// Inicializa o seletor de ambiente
document.addEventListener('DOMContentLoaded', () => {
    configManager.updateEnvironmentSelector();
    
    // Adiciona listener para mudança de ambiente
    const envSelector = document.getElementById('env-selector');
    if (envSelector) {
        envSelector.addEventListener('change', (e) => {
            configManager.switchEnvironment(e.target.value);
        });
    }
    
    console.log('🚀 Configuração inicializada:', CONFIG);
});

// Exporta para uso em outros módulos
window.CONFIG = CONFIG;
window.configManager = configManager;

// Funções de conveniência para compatibilidade
function getApiUrl(endpoint) {
    return configManager.getApiUrl(endpoint);
}

function switchEnvironment(env) {
    return configManager.switchEnvironment(env);
}

function loadSavedEnvironment() {
    return configManager.loadSavedEnvironment();
}

function testApiConnection() {
    return configManager.testApiConnection();
}

function getEnvironmentInfo() {
    return configManager.getEnvironmentInfo();
}

// Exporta para uso global
window.CONFIG = CONFIG;
window.configManager = configManager;
window.getApiUrl = getApiUrl;
window.switchEnvironment = switchEnvironment;
window.loadSavedEnvironment = loadSavedEnvironment;
window.testApiConnection = testApiConnection;
window.getEnvironmentInfo = getEnvironmentInfo;

// Inicialização quando a página carrega
document.addEventListener('DOMContentLoaded', function() {
    // Atualiza seletor visual
    configManager.updateEnvironmentSelector();
    
    // Testa conectividade da API
    setTimeout(() => {
        testApiConnection();
    }, 1000);
    
    // Listener para mudanças de ambiente
    document.addEventListener('environmentChanged', (event) => {
        console.log('Ambiente alterado:', event.detail);
        
        // Recarrega dados se necessário
        if (typeof loadDashboardData === 'function') {
            loadDashboardData();
        }
    });
}); 