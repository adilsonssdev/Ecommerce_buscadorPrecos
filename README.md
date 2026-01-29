# Buscador de Preços 🏹💰

**Seu assistente pessoal para encontrar os menores preços na web!**

[![Python](https://img.shields.io/badge/Python-3.7%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0-black.svg)](https://flask.palletsprojects.com/)
[![Beautiful Soup](https://img.shields.io/badge/Scraping-BeautifulSoup-orange.svg)](https://www.crummy.com/software/BeautifulSoup/)
[![GitHub Pages](https://img.shields.io/badge/Deploy-GitHub%20Pages-brightgreen)](https://pages.github.com/)

## 🎯 Sobre o Projeto

Cansado de abrir dezenas de abas para comparar o preço daquele produto que você tanto deseja? O **Buscador de Preços** é a sua solução!

Este projeto é um poderoso buscador de preços que varre automaticamente os principais e-commerces do Brasil (começando com **Magazine Luiza** e **Amazon**) para encontrar as melhores ofertas para você. Seja para uma busca rápida ou para monitorar um produto por dias, o Buscador de Preços trabalha por você, economizando seu tempo e, o mais importante, seu dinheiro!

## ✨ Funcionalidades Principais

-   🔎 **Busca Multi-Site:** Compara preços em várias lojas simultaneamente.
-   🌐 **Interface Web Interativa:** Uma interface moderna e amigável para você fazer suas buscas em tempo real.
-   🤖 **Automação Inteligente:** Agende buscas para monitorar a queda de preços dos seus produtos favoritos.
-   📊 **Relatórios Detalhados:** Gera arquivos `HTML` e `JSON` com os resultados, perfeitos para análise ou integração.
-   🔌 **API RESTful:** Integre os resultados de busca em seus próprios sites ou aplicações.
-   🧩 **Fácil de Estender:** Adicione novas lojas para buscar com apenas algumas linhas de código.
-   🎨 **Design Responsivo:** Acesse de qualquer dispositivo, seja no desktop ou no celular.

## 🛠️ Tecnologias Utilizadas

-   **Backend:** Python
-   **Scraping:** Beautiful Soup & Requests
-   **Web Framework & API:** Flask
-   **Agendamento:** Schedule
-   **Frontend:** HTML5, CSS3, JavaScript (sem frameworks)

## 🚀 Instalação e Uso

Siga os passos abaixo para ter seu próprio caçador de ofertas rodando em minutos.

### 1. Pré-requisitos

-   Python 3.7 ou superior
-   `pip` (gerenciador de pacotes do Python)

### 2. Instalação

```bash
# 1. Clone o repositório
git clone https://github.com/<SEU-USUARIO-GITHUB>/<SEU-REPOSITORIO>.git
cd <SEU-REPOSITORIO>

# 2. (Opcional, mas recomendado) Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# 3. Instale as dependências
pip install requests beautifulsoup4 flask flask-cors schedule
```

### ⚠️ Atenção: A Web Muda!

Os sites de e-commerce alteram sua estrutura (HTML/CSS) com frequência. Se o buscador parar de encontrar produtos, você provavelmente precisará **atualizar os seletores** no arquivo `buscador_precos.py`. O arquivo `Instalacao.md` contém um guia sobre como fazer isso.

## 🏃‍♂️ Modos de Execução

Você pode usar o Buscador de Preços de três maneiras diferentes:

### Modo 1: Busca Rápida (Linha de Comando)

Ideal para um teste rápido. Ele busca um produto, exibe os melhores resultados no terminal e gera os arquivos `produtos.html` e `produtos.json`.

```bash
# Edite o "termo" dentro do arquivo antes de rodar
python buscador_precos.py
```

### Modo 2: Automação e Monitoramento

Configure uma lista de produtos e deixe o script rodar em intervalos definidos, salvando os resultados para cada produto.

```bash
# O script perguntará o modo de automação (único, contínuo, horários fixos)
python automacao.py
```
> **Dica:** Configure os produtos que deseja monitorar diretamente no arquivo `automacao.py`.

### Modo 3: API Web Interativa (Recomendado)

Inicie o servidor Flask para usar a interface web completa, fazer buscas em tempo real e visualizar os resultados de forma dinâmica.

```bash
python api_flask.py
```
Abra seu navegador e acesse: **http://localhost:5000**

## 📂 Estrutura do Projeto

```
.
├── 📂 static/              # Arquivos do frontend (CSS, JS)
├── 📂 .github/             # Workflow de deploy para GitHub Pages
├── 📜 api_flask.py         # Servidor Flask que provê a API e o frontend
├── 📜 automacao.py         # Script para agendamento e monitoramento de buscas
├── 📜 buscador_precos.py    # O coração do projeto: classe que faz o scraping
├── 📜 frontend.html         # A página principal da interface web
├── 📜 Instalacao.md         # Guia rápido de instalação
└── 📜 README.md             # Este arquivo :)
```

## 🧩 Como Adicionar um Novo Site

O projeto foi pensado para ser extensível. Para adicionar uma nova loja:

1.  **Abra `buscador_precos.py`**.
2.  **Adicione a configuração da loja** no dicionário `self.sites_config`:
    ```python
    self.sites_config = {
        # ... sites existentes
        "nome_da_loja": {
            "url_busca": "https://www.novaloja.com.br/buscar?q=",
            "ativo": True,
            "parser": self._parse_nova_loja, # Crie esta função
        },
    }
    ```
3.  **Crie a função de parsing** `_parse_nova_loja(self, soup, termo_busca)`. Use as funções `_parse_amazon` ou `_parse_magazine_luiza` como modelo para extrair o nome, preço, link e imagem dos produtos.

## 🤝 Contribuições

Contribuições são o que tornam a comunidade open-source um lugar incrível para aprender, inspirar e criar. Qualquer contribuição que você fizer será **muito bem-vinda**.

1.  Faça um **Fork** do projeto
2.  Crie sua **Feature Branch** (`git checkout -b feature/NovaFuncionalidade`)
3.  Faça o **Commit** de suas mudanças (`git commit -m 'Adiciona NovaFuncionalidade'`)
4.  Faça o **Push** para a Branch (`git push origin feature/NovaFuncionalidade`)
5.  Abra um **Pull Request**

## 📄 Licença

Distribuído sob a licença MIT. Sinta-se à vontade para usar e modificar o código.

---

*Este projeto foi criado como um portfólio para demonstrar habilidades em desenvolvimento Python, web scraping e criação de APIs. Divirta-se caçando ofertas!*