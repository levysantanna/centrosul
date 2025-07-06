#!/usr/bin/env python3
"""
Script de Deploy Automatizado para Coolify
Executa git push e triggera o deploy no Coolify
"""

import os
import sys
import subprocess
import requests
import json
from datetime import datetime

# Configurações do Coolify
COOLIFY_BASE_URL = "https://comunatec.org"
PROJECT_ID = "egksg0wwcowg8k8k48kccok4"
ENVIRONMENT_ID = "p4w4gg8s0k8s00oookgg4ckk"
APPLICATION_ID = "l8cgg88cw00wosow0cc4gw0s"
DEPLOYMENT_ID = "okko8k008gok8g848gccgos0"

# Token de API do Coolify (deve ser configurado como variável de ambiente)
COOLIFY_API_TOKEN = os.environ.get('COOLIFY_API_TOKEN')

def log(message):
    """Log com timestamp"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")

def run_command(command, cwd=None):
    """Executa comando shell e retorna resultado"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            cwd=cwd
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def git_push():
    """Faz git push para origin main"""
    log("Verificando status do git...")
    
    # Verifica se há mudanças
    success, stdout, stderr = run_command("git status --porcelain")
    if not success:
        log(f"Erro ao verificar status do git: {stderr}")
        return False
    
    if stdout.strip():
        log("Há mudanças não commitadas. Fazendo commit...")
        
        # Add all changes
        success, _, stderr = run_command("git add .")
        if not success:
            log(f"Erro ao fazer git add: {stderr}")
            return False
        
        # Commit changes
        commit_message = f"Auto deploy - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        success, _, stderr = run_command(f'git commit -m "{commit_message}"')
        if not success:
            log(f"Erro ao fazer commit: {stderr}")
            return False
        
        log(f"Commit realizado: {commit_message}")
    else:
        log("Não há mudanças para commitar")
    
    # Push to origin main
    log("Fazendo git push...")
    success, stdout, stderr = run_command("git push origin main")
    if not success:
        log(f"Erro ao fazer git push: {stderr}")
        return False
    
    log("Git push realizado com sucesso!")
    return True

def trigger_coolify_deploy():
    """Triggera deploy no Coolify via API"""
    if not COOLIFY_API_TOKEN:
        log("AVISO: COOLIFY_API_TOKEN não configurado. Tentando deploy via webhook...")
        return trigger_deploy_webhook()
    
    log("Triggerando deploy no Coolify via API...")
    
    # URL da API do Coolify para deploy
    deploy_url = f"{COOLIFY_BASE_URL}/api/v1/applications/{APPLICATION_ID}/deploy"
    
    headers = {
        "Authorization": f"Bearer {COOLIFY_API_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    try:
        response = requests.post(deploy_url, headers=headers, timeout=30)
        
        if response.status_code in [200, 201, 202]:
            log("Deploy triggerrado com sucesso no Coolify!")
            return True
        else:
            log(f"Erro ao triggerar deploy: HTTP {response.status_code}")
            log(f"Resposta: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        log(f"Erro na requisição para Coolify: {e}")
        return False

def trigger_deploy_webhook():
    """Tenta triggerar deploy via webhook (método alternativo)"""
    log("Tentando triggerar deploy via webhook...")
    
    # URL do webhook (pode ser diferente, ajuste conforme necessário)
    webhook_url = f"{COOLIFY_BASE_URL}/webhooks/deploy/{APPLICATION_ID}"
    
    try:
        response = requests.post(webhook_url, timeout=30)
        
        if response.status_code in [200, 201, 202]:
            log("Deploy triggerrado via webhook!")
            return True
        else:
            log(f"Webhook falhou: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        log(f"Erro no webhook: {e}")
        log("Deploy manual necessário via interface do Coolify")
        return False

def check_deployment_status():
    """Verifica status do deployment (se API token disponível)"""
    if not COOLIFY_API_TOKEN:
        log("Para verificar status, configure COOLIFY_API_TOKEN")
        return
    
    log("Verificando status do deployment...")
    
    status_url = f"{COOLIFY_BASE_URL}/api/v1/applications/{APPLICATION_ID}/deployments"
    
    headers = {
        "Authorization": f"Bearer {COOLIFY_API_TOKEN}",
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(status_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            deployments = response.json()
            if deployments and len(deployments) > 0:
                latest = deployments[0]
                status = latest.get('status', 'unknown')
                log(f"Status do último deployment: {status}")
            else:
                log("Nenhum deployment encontrado")
        else:
            log(f"Erro ao verificar status: HTTP {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        log(f"Erro ao verificar status: {e}")

def main():
    """Função principal"""
    log("=== INICIANDO DEPLOY AUTOMATIZADO ===")
    
    # Verifica se estamos no diretório correto
    if not os.path.exists('.git'):
        log("ERRO: Não é um repositório git. Execute o script na raiz do projeto.")
        sys.exit(1)
    
    # 1. Git push
    if not git_push():
        log("ERRO: Falha no git push")
        sys.exit(1)
    
    # 2. Trigger deploy no Coolify
    if not trigger_coolify_deploy():
        log("AVISO: Falha ao triggerar deploy automaticamente")
        log("Acesse manualmente o Coolify para fazer o deploy:")
        log(f"{COOLIFY_BASE_URL}/project/{PROJECT_ID}/environment/{ENVIRONMENT_ID}/application/{APPLICATION_ID}")
        sys.exit(1)
    
    # 3. Verificar status (opcional)
    check_deployment_status()
    
    log("=== DEPLOY CONCLUÍDO ===")
    log("Aguarde alguns minutos para o deploy ser processado no Coolify")

if __name__ == "__main__":
    main() 