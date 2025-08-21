#!/usr/bin/env python3
"""
Script de teste para verificar conexão com Stripe
"""
import os
import stripe
from dotenv import load_dotenv

def test_stripe_connection():
    """Testa a conexão com Stripe usando as credenciais do .env"""
    
    # Carrega as variáveis de ambiente
    load_dotenv()
    
    # Obtém as credenciais
    stripe_secret_key = os.getenv('STRIPE_SECRET_KEY')
    stripe_public_key = os.getenv('STRIPE_PUBLIC_KEY')
    
    print("🔍 Testando conexão com Stripe...")
    print(f"🔑 Secret Key: {stripe_secret_key[:20]}...{stripe_secret_key[-10:] if stripe_secret_key else 'N/A'}")
    print(f"🔑 Public Key: {stripe_public_key[:20]}...{stripe_public_key[-10:] if stripe_public_key else 'N/A'}")
    print("-" * 50)
    
    try:
        # Configura o Stripe
        stripe.api_key = stripe_secret_key
        
        # Testa a conexão fazendo uma requisição simples
        print("📡 Conectando ao Stripe...")
        account = stripe.Account.retrieve()
        print("✅ Conexão realizada com sucesso!")
        print(f"🏢 Conta: {account.business_profile.name or 'N/A'}")
        print(f"🌍 País: {account.country}")
        print(f"💰 Moeda padrão: {account.default_currency}")
        print(f"📊 Tipo de conta: {account.type}")
        
        # Testa criação de um PaymentIntent de teste
        print("\n💳 Testando criação de PaymentIntent...")
        payment_intent = stripe.PaymentIntent.create(
            amount=1000,  # R$ 10,00 em centavos
            currency='brl',
            description='Teste de conexão - Moara Gestão'
        )
        print(f"✅ PaymentIntent criado: {payment_intent.id}")
        print(f"💰 Valor: R$ {payment_intent.amount / 100:.2f}")
        print(f"📊 Status: {payment_intent.status}")
        
        # Cancela o PaymentIntent de teste
        stripe.PaymentIntent.cancel(payment_intent.id)
        print("✅ PaymentIntent de teste cancelado")
        
        print("\n🎉 Teste do Stripe concluído com sucesso!")
        print("✅ Stripe configurado corretamente!")
        
    except stripe.error.AuthenticationError as e:
        print(f"❌ Erro de autenticação Stripe: {e}")
        print("💡 Verifique se:")
        print("   - A STRIPE_SECRET_KEY está correta")
        print("   - A chave não foi revogada")
        print("   - A conta Stripe está ativa")
        
    except stripe.error.APIError as e:
        print(f"❌ Erro da API Stripe: {e}")
        print("💡 Verifique se:")
        print("   - A conta Stripe tem permissões adequadas")
        print("   - Não há restrições na conta")
        
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        print("💡 Verifique se:")
        print("   - O arquivo .env está na raiz do projeto")
        print("   - Todas as variáveis estão configuradas")
        print("   - A conexão com a internet está funcionando")

if __name__ == "__main__":
    test_stripe_connection() 