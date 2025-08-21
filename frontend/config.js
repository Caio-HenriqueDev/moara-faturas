// Configuração do Frontend - Sistema de Gestão de Faturas
// Moara Energia

const CONFIG = {
    // URLs da API
    API_BASE_URL: 'http://localhost:8000', // Desenvolvimento local
    // API_BASE_URL: 'https://moara.vercel.app', // Produção Vercel
    // API_BASE_URL: 'https://moaraenergiasolar.vercel.app', // Produção Vercel 2
    
    // Endpoints da API
    ENDPOINTS: {
        ROOT: '/',
        HEALTH: '/health',
        FATURAS: '/faturas/',
        PROCESSAR_EMAIL: '/processar_email/',
        CHECKOUT: '/create-checkout-session',
        WEBHOOK: '/stripe-webhook/',
        DOCS: '/docs'
    },
    
    // Configurações do Stripe
    STRIPE: {
        PUBLIC_KEY: 'pk_test_your_stripe_public_key_here', // Configure sua chave pública
        SUCCESS_URL: '/success',
        CANCEL_URL: '/cancel'
    },
    
    // Configurações da aplicação
    APP: {
        NAME: 'Moara Energia',
        VERSION: '2.0.0',
        DESCRIPTION: 'Sistema de Gestão de Faturas'
    }
};

// Função para obter URL completa da API
function getApiUrl(endpoint) {
    return CONFIG.API_BASE_URL + endpoint;
}

// Função para alternar entre ambientes
function switchEnvironment(env) {
    switch(env) {
        case 'local':
            CONFIG.API_BASE_URL = 'http://localhost:8000';
            break;
        case 'vercel':
            CONFIG.API_BASE_URL = 'https://moara.vercel.app';
            break;
        case 'vercel2':
            CONFIG.API_BASE_URL = 'https://moaraenergiasolar.vercel.app';
            break;
        default:
            CONFIG.API_BASE_URL = 'http://localhost:8000';
    }
    console.log(`🌍 Ambiente alterado para: ${CONFIG.API_BASE_URL}`);
}

// Exporta para uso global
window.CONFIG = CONFIG;
window.getApiUrl = getApiUrl;
window.switchEnvironment = switchEnvironment; 