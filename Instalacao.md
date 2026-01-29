# 🚀 GUIA RÁPIDO DE INSTALAÇÃO

## Passo 1: Instalação das Dependências

bash
# Instale as bibliotecas necessárias
pip install -r requirements.txt


Ou instale manualmente:
bash
pip install requests beautifulsoup4 flask flask-cors apscheduler


## Passo 2: Configuração Inicial

### ⚠️ IMPORTANTE: Atualizar Seletores CSS

Os sites mudam frequentemente sua estrutura. Você precisa atualizar os seletores CSS para cada site.

*Como descobrir os seletores corretos:*

1. Abra o site (ex: Americanas) no navegador
2. Pressione F12 para abrir as ferramentas de desenvolvedor
3. Clique no ícone de seleção (canto superior esquerdo)
4. Clique em um produto na página
5. Veja no HTML destacado as classes CSS usadas
6. Atualize no código buscador_precos.py

*Exemplo:*
python
def _parse_americanas(self, soup, termo_busca):
    # ATUALIZE ESTAS CLASSES conforme o site atual
    items = soup.find_all('div', class_='CLASSE_AQUI')  # Ex: 'product-grid-item'
    
    for item in items[:10]:
        nome = item.find('h2', class_='CLASSE_AQUI')    # Ex: 'product-name'
        preco = item.find('span', class_='CLASSE_AQUI') # Ex: 'price'
        link = item.find('a', href=True)


## Passo 3: Escolha seu Modo de Uso

### 🎯 MODO 1: Execução Simples (Teste)

bash
python buscador_precos.py


Este modo:
- Busca produtos uma vez
- Gera arquivos JSON e HTML
- Para após a execução

### 🔄 MODO 2: Automação com Agendamento

bash
python automacao.py


Escolha entre:
1. *Execução única* - Roda agora e para
2. *Modo contínuo* - Roda a cada X horas
3. *Horários fixos* - Roda em horários específicos (ex: 9h, 15h, 21h)

### 🌐 MODO 3: API com Interface Web Interativa

bash
python api_flask.py


Depois de iniciar a API, abra seu navegador e acesse:

http://localhost:5000

Isso abrirá uma interface web onde você pode buscar produtos em tempo real.

## Passo 4: Personalização

### Adicionar Produtos para Monitorar

Edite o arquivo automacao.py:

python
automacao = AutomacaoBusca()

# Adicione seus produtos aqui
automacao.adicionar_produto_monitoramento("notebook dell")
automacao.adicionar_produto_monitoramento("iphone 15")
automacao.adicionar_produto_monitoramento("smart tv 55")
automacao.adicionar_produto_monitoramento("ar condicionado")


### Adicionar Novos Sites

No arquivo buscador_precos.py, adicione na seção sites_config:

python
'magazine_luiza': {
    'url_busca': 'https://www.magazineluiza.com.br/busca/',
    'ativo': True,
    'parser': self._parse_magazine_luiza
}


E crie a função parser:

python
def _parse_magazine_luiza(self, soup, termo_busca):
    produtos = []
    # Adicione a lógica de extração aqui
    return produtos


## Passo 5: Integração com seu Site

### Opção A: Usar arquivos JSON gerados

javascript
// No JavaScript do seu site
fetch('produtos.json')
    .then(response => response.json())
    .then(produtos => {
        // Use os dados aqui
        console.log(produtos);
    });


### Opção B: Usar a API

javascript
// No JavaScript do seu site
fetch('http://localhost:5000/api/buscar/notebook')
    .then(response => response.json())
    .then(data => {
        console.log(data.produtos);
    });


### Opção C: Usar o HTML gerado

Abra o arquivo `produtos.html` (gerado pelo Modo 1 ou 2) diretamente no navegador.

## 🔧 Troubleshooting Comum

### ❌ Nenhum produto encontrado

*Solução:* Atualize os seletores CSS conforme instruções acima.

### ❌ Erro de módulo não encontrado

bash
pip install requests beautifulsoup4 flask flask-cors apscheduler


### ❌ API não responde

- Verifique se a API está rodando: python api_flask.py
- Acesse http://localhost:5000 no navegador para ver a interface, ou http://localhost:5000/api/status para ver o status da API.
- Verifique firewall/antivirus

### ❌ CORS error no frontend

Instale flask-cors:
bash
pip install flask-cors


## 📅 Agendamento Automático

### Windows (Task Scheduler)

1. Crie arquivo executar.bat:
batch
@echo off
cd C:\caminho\para\seu\projeto
python automacao.py


2. Abra "Agendador de Tarefas"
3. Criar Tarefa Básica
4. Escolha horários
5. Ação: Iniciar programa → selecione seu .bat

### Linux/Mac (Crontab)

bash
crontab -e

# Adicione (roda todo dia às 9h):
0 9 * * * /usr/bin/python3 /caminho/completo/automacao.py

# Roda a cada 6 horas:
0 */6 * * * /usr/bin/python3 /caminho/completo/automacao.py


## 📊 Estrutura de Arquivos Gerada

Após executar, você terá:


projeto/
├── buscador_precos.py       # Código principal
├── automacao.py              # Script de automação
├── api_flask.py              # API REST
├── frontend.html             # Interface Web principal
├── requirements.txt          # Dependências
├── produtos.json             # Dados em JSON
├── produtos.html             # Página com produtos
└── README.md                 # Documentação


## 🎨 Customização do HTML

Edite a função gerar_html() em buscador_precos.py para personalizar:
- Cores
- Layout
- Informações exibidas
- Estilo dos cards

## 🔐 Boas Práticas

1. *Rate Limiting*: Já implementado delays entre requisições
2. *User-Agent*: Já configurado um User-Agent apropriado
3. *Respeite robots.txt*: Não abuse das requisições
4. *Cache*: Evite buscas repetidas no mesmo minuto

## 💡 Próximos Passos Recomendados

1. ✅ Testar com python buscador_precos.py
2. ✅ Atualizar seletores CSS se necessário
3. ✅ Adicionar seus produtos em automacao.py
4. ✅ Configurar agendamento
5. ✅ Integrar com seu site

## 📞 Suporte

Para dúvidas sobre:
- *Seletores CSS*: Use F12 no navegador e inspecione o site
- *Python*: Verifique versão com python --version (requer 3.7+)
- *Dependências*: Execute pip list para ver instalados

## ⚡ Comandos Rápidos

bash
# Instalação
pip install -r requirements.txt

# Teste rápido
python buscador_precos.py

# Automação
python automacao.py

# API
python api_flask.py # e acesse http://localhost:5000

# Ver produtos gerados
# Abra produtos.html no navegador


---

*Última atualização:* Janeiro 2025
*Versão:* 1.0