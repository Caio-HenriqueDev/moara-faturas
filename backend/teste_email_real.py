#!/usr/bin/env python3
"""
Script para testar o processamento completo de emails
Simula o que acontece quando o sistema processa um email real
"""

import os
import sys
import tempfile
from pathlib import Path

# Adiciona o diretório pai ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.utils.bot_mail import gerar_hash
from backend.utils.pdf_parser import extrair_dados_fatura_pdf
from backend.config import settings

def criar_pdf_teste():
    """Cria um PDF de teste com dados de fatura"""
    try:
        from fpdf import FPDF
        
        # Cria PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        # Adiciona conteúdo da fatura
        pdf.cell(200, 10, txt="FATURA DE ENERGIA ELETRICA", ln=True, align='C')
        pdf.ln(10)
        
        pdf.cell(200, 10, txt="JOSE SILVA", ln=True, align='L')
        pdf.cell(200, 10, txt="MURIAE", ln=True, align='L')
        pdf.ln(5)
        
        pdf.cell(200, 10, txt="CNPJ/CPF/RANI: 123.456.789-00", ln=True, align='L')
        pdf.cell(200, 10, txt="Instalacao: 123456 Ponta", ln=True, align='L')
        pdf.cell(200, 10, txt="Mes Referencia: Agosto/2025", ln=True, align='L')
        pdf.cell(200, 10, txt="Data Vencimento: 15/09/2025", ln=True, align='L')
        pdf.ln(5)
        
        pdf.cell(200, 10, txt="Consumo em kWh:", ln=True, align='L')
        pdf.cell(200, 10, txt="250,00", ln=True, align='L')
        pdf.ln(5)
        
        pdf.cell(200, 10, txt="Preco Unitario: R$ 0,30", ln=True, align='L')
        pdf.cell(200, 10, txt="Valor Total: R$ 75,00", ln=True, align='L')
        pdf.ln(5)
        
        pdf.cell(200, 10, txt="Saldo Acumulado: 0,00", ln=True, align='L')
        
        # Salva em arquivo temporário
        temp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        pdf.output(temp_file.name)
        temp_file.close()
        
        print(f"✅ PDF de teste criado: {temp_file.name}")
        return temp_file.name
        
    except Exception as e:
        print(f"❌ Erro ao criar PDF: {e}")
        import traceback
        traceback.print_exc()
        return None

def testar_processamento_completo():
    """Testa o processamento completo de uma fatura"""
    print("🚀 INICIANDO TESTE COMPLETO DE PROCESSAMENTO")
    print("=" * 60)
    
    # 1. Cria PDF de teste
    arquivo_teste = criar_pdf_teste()
    if not arquivo_teste:
        return False
    
    try:
        # 2. Gera hash do arquivo
        with open(arquivo_teste, 'rb') as f:
            conteudo = f.read()
        
        hash_arquivo = gerar_hash(conteudo)
        print(f"🔐 Hash gerado: {hash_arquivo}")
        
        # 3. Cria diretório de armazenamento
        storage_path = settings.PDF_STORAGE_PATH
        os.makedirs(storage_path, exist_ok=True)
        print(f"📁 Diretório criado: {storage_path}")
        
        # 4. Salva arquivo com hash
        path_final = os.path.join(storage_path, f"{hash_arquivo}.pdf")
        with open(path_final, 'wb') as f:
            f.write(conteudo)
        print(f"💾 Arquivo salvo: {path_final}")
        
        # 5. Testa extração de dados
        print("\n🔍 TESTANDO EXTRAÇÃO DE DADOS...")
        dados_extraidos = extrair_dados_fatura_pdf(path_final)
        
        if dados_extraidos:
            print("✅ DADOS EXTRAÍDOS COM SUCESSO:")
            for campo, valor in dados_extraidos.items():
                print(f"   - {campo}: {valor}")
            
            # 6. Valida dados obrigatórios
            campos_obrigatorios = ["nome_cliente", "numero_instalacao"]
            campos_faltando = [campo for campo in campos_obrigatorios if not dados_extraidos.get(campo)]
            
            if not campos_faltando:
                print("\n🎯 VALIDAÇÃO: Todos os campos obrigatórios encontrados!")
                return True
            else:
                print(f"\n❌ VALIDAÇÃO: Campos faltando: {campos_faltando}")
                return False
        else:
            print("❌ Falha na extração de dados")
            return False
            
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Limpa arquivos temporários
        try:
            if arquivo_teste and os.path.exists(arquivo_teste):
                os.unlink(arquivo_teste)
            if 'path_final' in locals() and os.path.exists(path_final):
                os.unlink(path_final)
        except:
            pass

if __name__ == "__main__":
    print("🧪 TESTE DO SISTEMA DE PROCESSAMENTO DE FATURAS")
    print("=" * 60)
    
    sucesso = testar_processamento_completo()
    
    print("\n" + "=" * 60)
    if sucesso:
        print("🎉 TESTE CONCLUÍDO COM SUCESSO!")
        print("✅ O sistema está funcionando perfeitamente")
    else:
        print("❌ TESTE FALHOU!")
        print("🔧 Verifique os logs acima para identificar o problema")
    
    print("=" * 60) 