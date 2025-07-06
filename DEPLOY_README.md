# Script de Deploy Automatizado

Este script automatiza o processo de deploy da aplicação no Coolify, fazendo git push e triggerando o deploy via API.

## Como usar

### Uso básico (sem API token)
```bash
python deploy.py
```

### Uso com API token (recomendado)
```bash
export COOLIFY_API_TOKEN="seu_token_aqui"
python deploy.py
```

## Configuração

### 1. Instalar dependências
```bash
pip install requests
```

### 2. Obter API Token do Coolify (opcional mas recomendado)
1. Acesse o Coolify: https://comunatec.org
2. Vá em Settings > API Tokens
3. Crie um novo token
4. Configure como variável de ambiente:
   ```bash
   export COOLIFY_API_TOKEN="seu_token_aqui"
   ```

### 3. Tornar o script executável (Linux/Mac)
```bash
chmod +x deploy.py
```

## O que o script faz

1. **Verifica mudanças**: Checa se há arquivos modificados
2. **Commit automático**: Se houver mudanças, faz commit automaticamente
3. **Git push**: Envia as mudanças para `origin main`
4. **Trigger deploy**: Aciona o deploy no Coolify via API ou webhook
5. **Verifica status**: Mostra o status do deployment (se API token configurado)

## URLs importantes

- **Coolify Dashboard**: https://comunatec.org
- **Aplicação**: https://centrosul.comunatec.org
- **Deploy Manual**: https://comunatec.org/project/egksg0wwcowg8k8k48kccok4/environment/p4w4gg8s0k8s00oookgg4ckk/application/l8cgg88cw00wosow0cc4gw0s

## Troubleshooting

### Se o deploy automático falhar
O script tentará usar webhook como fallback. Se ambos falharem, acesse manualmente o Coolify e clique em "Deploy".

### Se houver erro de API
- Verifique se o COOLIFY_API_TOKEN está correto
- Confirme se o token tem permissões de deploy
- Tente fazer deploy manual primeiro

### Se git push falhar
- Verifique suas credenciais git
- Confirme se você tem permissão para push na branch main
- Resolva conflitos de merge se necessário

## Exemplo de uso completo

```bash
# Configurar token (uma vez)
export COOLIFY_API_TOKEN="your_token_here"

# Fazer deploy
python deploy.py
```

Saída esperada:
```
[2025-01-06 20:30:00] === INICIANDO DEPLOY AUTOMATIZADO ===
[2025-01-06 20:30:01] Verificando status do git...
[2025-01-06 20:30:01] Há mudanças não commitadas. Fazendo commit...
[2025-01-06 20:30:02] Commit realizado: Auto deploy - 2025-01-06 20:30:02
[2025-01-06 20:30:03] Fazendo git push...
[2025-01-06 20:30:05] Git push realizado com sucesso!
[2025-01-06 20:30:06] Triggerando deploy no Coolify via API...
[2025-01-06 20:30:08] Deploy triggerrado com sucesso no Coolify!
[2025-01-06 20:30:09] Verificando status do deployment...
[2025-01-06 20:30:10] Status do último deployment: running
[2025-01-06 20:30:10] === DEPLOY CONCLUÍDO ===
[2025-01-06 20:30:10] Aguarde alguns minutos para o deploy ser processado no Coolify
``` 