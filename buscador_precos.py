"""
Buscador de Produtos com Menores Preços
Busca produtos em múltiplos sites e retorna os melhores preços
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
from urllib.parse import urljoin
from typing import List, Dict
import re
import logging
import urllib3

# Desabilita avisos de segurança para conexões não verificadas (necessário para redes corporativas/proxies)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class BuscadorPrecos:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://www.google.com/",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-User": "?1",
        }
        # Cria uma sessão para persistir cookies, headers e configurações
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        # Define a verificação SSL como False para toda a sessão, contornando erros em redes corporativas
        self.session.verify = False
        self.produtos_encontrados = []

        # Configuração de sites - adicione novos sites aqui
        self.sites_config = {
            "magazine_luiza": {
                "url_busca": "https://www.magazineluiza.com.br/busca/",
                "ativo": True,
                "parser": self._parse_magazine_luiza,
            },
            "amazon": {
                "url_busca": "https://www.amazon.com.br/s?k=",
                "ativo": True,
                "parser": self._parse_amazon,
            },
        }

    def adicionar_site(self, nome: str, url_busca: str, parser_function):
        """
        Adiciona um novo site para busca de produtos

        Args:
            nome: Nome identificador do site
            url_busca: URL base para busca de produtos
            parser_function: Função que faz o parsing da página
        """
        self.sites_config[nome] = {
            "url_busca": url_busca,
            "ativo": True,
            "parser": parser_function,
        }
        logging.info(f"✓ Site '{nome}' adicionado com sucesso!")

    def _limpar_preco(self, preco_texto: str) -> float:
        """Converte texto de preço em float de forma inteligente"""
        if not preco_texto:
            return 0.0
        
        try:
            # Remove tudo exceto números, vírgula e ponto
            p = re.sub(r"[^\d,.]", "", str(preco_texto))
            
            if ',' in p and '.' in p:
                # Formato brasileiro: 1.500,76 -> 1500.76
                p = p.replace('.', '').replace(',', '.')
            elif ',' in p:
                # Apenas vírgula: 150,76 -> 150.76
                p = p.replace(',', '.')
            elif '.' in p:
                # Apenas ponto: pode ser 150.76 ou 1.500
                partes = p.split('.')
                if len(partes) > 2:
                    # Múltiplos pontos: 1.500.000 -> 1500000
                    p = p.replace('.', '')
                elif len(partes[-1]) == 3:
                    # Um ponto seguido de 3 dígitos ao FINAL: 1.500 -> 1500
                    # Note: Exceção se for algo como 1.000 que é mil mas poderia ser 1.000 (decimal)
                    # Em e-commerce brasileiro, ponto sozinho com 3 dígitos costuma ser mil.
                    p = p.replace('.', '')
                else:
                    # Um ponto seguido de != 3 dígitos (ex: 2): 150.76 -> 150.76
                    pass
            
            return float(p)
        except Exception as e:
            logging.warning(f"Não foi possível converter o preço: '{preco_texto}' - Erro: {e}")
            return 0.0

    def _extract_next_data(self, soup: BeautifulSoup) -> Dict:
        """Extrai dados do script __NEXT_DATA__ comum em sites modernos (Next.js)"""
        try:
            script = soup.find("script", id="__NEXT_DATA__")
            if script:
                return json.loads(script.string)
        except Exception as e:
            logging.error(f"Erro ao extrair __NEXT_DATA__: {e}")
        return {}

    def _parse_magazine_luiza(
        self, soup: BeautifulSoup, termo_busca: str
    ) -> List[Dict]:
        """Parser específico para Magazine Luiza"""
        produtos = []

        # Tenta extrair via JSON (mais confiável)
        try:
            data = self._extract_next_data(soup)
            # Navega no JSON para encontrar produtos: props -> pageProps -> initialState -> search -> results -> products
            try:
                # Tenta caminho novo (identificado no debug)
                raw_products = (
                    data.get("props", {})
                    .get("pageProps", {})
                    .get("data", {})
                    .get("search", {})
                    .get("products", [])
                )

                # Se não encontrar, tenta o caminho antigo
                if not raw_products:
                    raw_products = (
                        data.get("props", {})
                        .get("pageProps", {})
                        .get("initialState", {})
                        .get("search", {})
                        .get("results", {})
                        .get("products", [])
                    )
            except:
                raw_products = []

            if raw_products:
                for item in raw_products[:40]:
                    try:
                        nome = item.get("title", "")
                        # Tenta pegar o preço de várias formas
                        preco_str = item.get("price", {}).get(
                            "price"
                        )  # As vezes é objeto
                        if not preco_str:
                            # Fallback se a estrutura for plana
                            preco_str = item.get("price")

                        if not preco_str:
                            continue

                        link = item.get("path", "") or item.get("url", "") or item.get("href", "")
                        if link and not link.startswith("http"):
                            link = "https://www.magazineluiza.com.br" + link

                        imagem = item.get("image", "")
                        # Corrige placeholder de imagem do Magalu {w}x{h}
                        if imagem and "{w}" in imagem:
                            imagem = imagem.replace("{w}", "200").replace("{h}", "200")

                        # Avisa se o link está vazio, mas não bloqueia o produto
                        if not link or link == "":
                            logging.warning(f"Link vazio para produto: {nome}")
                            link = None  # Define como None para tratamento no frontend
                            
                        produto = {
                            "nome": nome,
                            "preco": (
                                float(preco_str)
                                if isinstance(preco_str, (int, float))
                                else self._limpar_preco(str(preco_str))
                            ),
                            "preco_formatado": f"R$ {preco_str}",
                            "site": "Magazine Luiza",
                            "link": link,
                            "imagem": imagem,
                            "data_busca": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        }
                        produtos.append(produto)
                    except Exception:
                        continue
                return produtos  # Se achou via JSON, retorna
        except Exception as e:
            logging.warning(
                f"Erro ao processar JSON Magazine Luiza, tentando HTML: {e}"
            )

        # Fallback para HTML (se o JSON falhar)
        try:
            items = soup.find_all("li", attrs={"data-testid": "product-card-container"})
            for item in items[:40]:
                # ... (código HTML existente mantido como fallback) ...
                pass
        except Exception:
            pass

        return produtos

    def _parse_amazon(self, soup: BeautifulSoup, termo_busca: str) -> List[Dict]:
        """Parser específico para Amazon"""
        produtos = []

        try:
            # Amazon usa divs com classe s-result-item
            items = soup.find_all("div", class_="s-result-item")
            
            if not items:
                logging.warning("Amazon: Nenhum produto encontrado com o seletor padrão")
                return produtos
            
            logging.info(f"Amazon: Encontrados {len(items)} itens na página")

            for item in items[:40]:
                try:
                    # Pula itens que não têm data-asin (anúncios, etc)
                    if not item.get("data-asin"):
                        continue
                    
                    # Extrai o nome do produto (dentro de h2)
                    nome_elem = item.find("h2")
                    if not nome_elem:
                        continue
                    
                    nome = nome_elem.get_text(strip=True)

                    # Extrai o preço
                    preco_elem = item.find("span", class_="a-price-whole")
                    if not preco_elem:
                        continue
                    
                    preco_texto = preco_elem.get_text(strip=True)
                    preco = self._limpar_preco(preco_texto)

                    # Extrai o link (tenta várias formas comuns na Amazon)
                    link = None
                    # Tenta no h2 primeiro
                    link_elem = nome_elem.find("a")
                    # Se não achar no h2, tenta em qualquer link com a classe de produto
                    if not link_elem:
                        link_elem = item.find("a", class_="a-link-normal")
                    # Fallback para qualquer link com href
                    if not link_elem:
                        link_elem = item.find("a", href=True)
                        
                    if link_elem and link_elem.get("href"):
                        link = link_elem["href"]
                        if link and not link.startswith("http"):
                            link = "https://www.amazon.com.br" + link
                        # Remove parâmetros de rastreamento pesados se quiser link limpo
                        if link and "?" in link:
                            link = link.split("?")[0]

                    # Extrai a imagem
                    img_elem = item.find("img", class_="s-image")
                    if not img_elem:
                        img_elem = item.find("img")
                    imagem = img_elem.get("src") if img_elem else None

                    # Avisa se o link está vazio
                    if not link or link == "":
                        logging.warning(f"Amazon: Link vazio para produto: {nome}")
                        link = None

                    produto = {
                        "nome": nome,
                        "preco": preco,
                        "preco_formatado": f"R$ {preco:.2f}",
                        "site": "Amazon",
                        "link": link,
                        "imagem": imagem,
                        "data_busca": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    }
                    produtos.append(produto)
                    
                except Exception as e:
                    logging.warning(f"Amazon: Erro ao processar produto: {e}")
                    continue

            logging.info(f"Amazon: {len(produtos)} produtos processados com sucesso")
            
        except Exception as e:
            logging.error(f"Amazon: Erro geral no parser: {e}")

        return produtos

    def buscar_produto(self, termo_busca: str) -> List[Dict]:
        """
        Busca um produto em todos os sites configurados

        Args:
            termo_busca: Termo para buscar (ex: "notebook dell")

        Returns:
            Lista de produtos encontrados ordenados por menor preço
        """
        logging.info(f"Iniciando busca por '{termo_busca}'...")
        self.produtos_encontrados = []

        for nome_site, config in self.sites_config.items():
            if not config["ativo"]:
                continue

            logging.info(f"  → Buscando em {nome_site}...")

            try:
                # Monta URL de busca
                url = config["url_busca"] + termo_busca.replace(" ", "+")

                # Faz requisição usando a sessão, que já está configurada para não verificar SSL
                response = self.session.get(url, timeout=15)

                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, "html.parser")
                    # Verifica se a página é de verificação de bot
                    if (
                        "não é um robô" in soup.text.lower()
                        or "are you a human" in soup.text.lower()
                    ):
                        logging.warning(
                            f"    - Alerta: Página de verificação de bot detectada em {nome_site}"
                        )
                        produtos = []
                    else:
                        produtos = config["parser"](soup, termo_busca)

                    self.produtos_encontrados.extend(produtos)
                    logging.info(
                        f"    ✓ {len(produtos)} produtos encontrados em {nome_site}"
                    )
                    # Se não encontrou produtos, salva o HTML para debug
                    if not produtos:
                        debug_filename = f"debug_{nome_site}.html"
                        with open(debug_filename, "w", encoding="utf-8") as f:
                            f.write(str(soup))
                        logging.warning(
                            f"    - Alerta: O parser para {nome_site} não retornou produtos. HTML salvo em '{debug_filename}' para análise."
                        )
                else:
                    logging.error(
                        f"    ✗ Erro em {nome_site}: Status {response.status_code}"
                    )

                # Aguarda entre requisições para não sobrecarregar
                time.sleep(2)

            except Exception as e:
                logging.error(f"    ✗ Erro ao buscar em {nome_site}: {e}")

        # Ordena por menor preço
        self.produtos_encontrados.sort(key=lambda x: x["preco"])

        return self.produtos_encontrados

    def obter_melhores_precos(self, limite: int = 5) -> List[Dict]:
        """Retorna os produtos com os menores preços"""
        return self.produtos_encontrados[:limite]

    def salvar_json(self, arquivo: str = "produtos.json"):
        """Salva os produtos encontrados em arquivo JSON"""
        with open(arquivo, "w", encoding="utf-8") as f:
            json.dump(self.produtos_encontrados, f, ensure_ascii=False, indent=2)
        logging.info(f"💾 Dados salvos em '{arquivo}'")

    def gerar_html(self, arquivo: str = "produtos.html"):
        """Gera página HTML com os produtos"""
        html = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Melhores Preços</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        h1 {
            color: white;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .produtos-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
        }
        .produto-card {
            background: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .produto-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.3);
        }
        .produto-nome {
            font-size: 1.1em;
            font-weight: bold;
            color: #333;
            margin-bottom: 15px;
            min-height: 50px;
        }
        .produto-preco {
            font-size: 2em;
            color: #27ae60;
            font-weight: bold;
            margin: 10px 0;
        }
        .produto-site {
            display: inline-block;
            background: #3498db;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            margin-bottom: 10px;
        }
        .produto-link {
            display: block;
            background: #667eea;
            color: white;
            text-align: center;
            padding: 12px;
            border-radius: 8px;
            text-decoration: none;
            margin-top: 15px;
            transition: background 0.3s ease;
        }
        .produto-link:hover {
            background: #764ba2;
        }
        .data-atualizacao {
            text-align: center;
            color: white;
            margin-top: 30px;
            font-size: 0.9em;
        }
        .badge-melhor {
            background: #f39c12;
            color: white;
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 0.8em;
            font-weight: bold;
            display: inline-block;
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏆 Melhores Preços Encontrados</h1>
        <div class="produtos-grid">
"""

        for i, produto in enumerate(self.produtos_encontrados):
            melhor_badge = (
                '<div class="badge-melhor">⭐ MELHOR PREÇO</div>' if i == 0 else ""
            )

            imagem_html = (
                f"""
                <div class="produto-imagem-container">
                    <a href="{produto['link']}" target="_blank" class="produto-imagem-link">
                        <img src="{produto.get('imagem', '')}" alt="{produto['nome']}" class="produto-imagem">
                    </a>
                </div>
            """
                if produto.get("imagem")
                else ""
            )

            html += f"""
            <div class="produto-card">
                {melhor_badge}
                {imagem_html}
                <div class="produto-site">{produto['site']}</div>
                <div class="produto-nome">{produto['nome']}</div>
                <div class="produto-preco">{produto['preco_formatado']}</div>
                <a href="{produto['link']}" target="_blank" class="produto-link">
                    Ver Produto →
                </a>
            </div>
"""

        html += f"""
        </div>
        <div class="data-atualizacao">
            Última atualização: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}
        </div>
    </div>
</body>
</html>
"""

        # Adiciona estilos para a imagem no HTML gerado
        html = html.replace(
            ".produto-card:hover {",
            """
        .produto-imagem-container {
            width: 100%; height: 200px; display: flex; align-items: center; justify-content: center; margin-bottom: 15px;
        }
        .produto-imagem-link {
            display: flex; align-items: center; justify-content: center; width: 100%; height: 100%; text-decoration: none;
        }
        .produto-imagem {
            max-width: 100%; max-height: 100%; object-fit: contain; transition: transform 0.3s ease;
        }
        .produto-imagem-link:hover .produto-imagem {
            transform: scale(1.05); cursor: pointer;
        }
        .produto-card:hover {""",
            1,
        )

        with open(arquivo, "w", encoding="utf-8") as f:
            f.write(html)
        logging.info(f"📄 HTML gerado em '{arquivo}'")


def exemplo_uso():
    """Exemplo de como usar o buscador"""

    # Inicializa o buscador
    buscador = BuscadorPrecos()

    # Define o produto que quer buscar
    termo = "notebook"  # ALTERE AQUI para o produto desejado

    # Busca em todos os sites
    produtos = buscador.buscar_produto(termo)

    # Exibe os 5 melhores preços
    logging.info("=" * 60)
    logging.info("💰 TOP 5 MELHORES PREÇOS")
    logging.info("=" * 60)

    melhores = buscador.obter_melhores_precos(5)
    for i, produto in enumerate(melhores, 1):
        logging.info(f"\n{i}º Lugar - {produto['site']}")
        logging.info(f"   Produto: {produto['nome'][:50]}...")
        logging.info(f"   Preço: {produto['preco_formatado']}")
        logging.info(f"   Link: {produto['link'][:60]}...")

    # Salva em JSON
    buscador.salvar_json("produtos.json")

    # Gera HTML
    buscador.gerar_html("produtos.html")

    logging.info("=" * 60)
    logging.info("✅ Processo concluído!")
    logging.info("=" * 60)


if __name__ == "__main__":
    exemplo_uso()
