"""
API REST para servir dados de produtos
Use esta API para integrar com seu site
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from buscador_precos import BuscadorPrecos
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Permite requisições de outros domínios

# Instância global do buscador
buscador = BuscadorPrecos()


@app.route("/")
def serve_frontend():
    """Serve a página principal do frontend."""
    return send_from_directory(".", "frontend.html")


@app.route("/api/status")
def api_status():
    """Retorna o status e informações da API"""
    return jsonify(
        {
            "status": "online",
            "versao": "1.0",
            "endpoints": {
                "/api/buscar/<termo>": "Busca produtos por termo",
                "/api/produtos": "Lista todos os produtos salvos",
                "/api/melhores/<limite>": "Retorna os N melhores preços",
                "/api/sites": "Lista sites configurados",
            },
        }
    )


@app.route("/api/buscar/<termo>")
def buscar_produto(termo):
    """
    Busca produtos em tempo real
    Exemplo: /api/buscar/notebook
    """
    try:
        produtos = buscador.buscar_produto(termo)

        return jsonify(
            {
                "sucesso": True,
                "termo_busca": termo,
                "total_encontrados": len(produtos),
                "data_busca": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "produtos": produtos,
            }
        )

    except Exception as e:
        return jsonify({"sucesso": False, "erro": str(e)}), 500


@app.route("/api/melhores/<int:limite>")
def melhores_precos(limite):
    """
    Retorna os N produtos com melhores preços
    Exemplo: /api/melhores/5
    """
    try:
        if not buscador.produtos_encontrados:
            return (
                jsonify(
                    {"sucesso": False, "mensagem": "Nenhuma busca realizada ainda"}
                ),
                404,
            )

        melhores = buscador.obter_melhores_precos(limite)

        return jsonify({"sucesso": True, "limite": limite, "produtos": melhores})

    except Exception as e:
        return jsonify({"sucesso": False, "erro": str(e)}), 500


@app.route("/api/produtos")
def listar_produtos():
    """
    Lista todos os produtos da última busca
    """
    try:
        if not buscador.produtos_encontrados:
            return (
                jsonify(
                    {"sucesso": False, "mensagem": "Nenhuma busca realizada ainda"}
                ),
                404,
            )

        return jsonify(
            {
                "sucesso": True,
                "total": len(buscador.produtos_encontrados),
                "produtos": buscador.produtos_encontrados,
            }
        )

    except Exception as e:
        return jsonify({"sucesso": False, "erro": str(e)}), 500


@app.route("/api/sites")
def listar_sites():
    """
    Lista todos os sites configurados
    """
    sites = []
    for nome, config in buscador.sites_config.items():
        sites.append(
            {"nome": nome, "url_busca": config["url_busca"], "ativo": config["ativo"]}
        )

    return jsonify({"sucesso": True, "total_sites": len(sites), "sites": sites})


@app.route("/api/carregar/<arquivo>")
def carregar_arquivo(arquivo):
    """
    Carrega produtos de um arquivo JSON salvo
    Exemplo: /api/carregar/notebook.json
    """
    try:
        if not arquivo.endswith(".json"):
            arquivo += ".json"

        if os.path.exists(arquivo):
            with open(arquivo, "r", encoding="utf-8") as f:
                produtos = json.load(f)

            return jsonify(
                {
                    "sucesso": True,
                    "arquivo": arquivo,
                    "total": len(produtos),
                    "produtos": produtos,
                }
            )
        else:
            return (
                jsonify(
                    {"sucesso": False, "mensagem": f"Arquivo {arquivo} não encontrado"}
                ),
                404,
            )

    except Exception as e:
        return jsonify({"sucesso": False, "erro": str(e)}), 500


@app.route("/api/webhook", methods=["POST"])
def webhook():
    """
    Endpoint para receber webhooks externos
    Permite que outros sistemas disparem buscas
    """
    try:
        dados = request.json
        termo = dados.get("termo_busca")

        if not termo:
            return (
                jsonify(
                    {"sucesso": False, "mensagem": "Campo termo_busca é obrigatório"}
                ),
                400,
            )

        produtos = buscador.buscar_produto(termo)

        # Salva automaticamente
        nome_arquivo = termo.replace(" ", "_").lower()
        buscador.salvar_json(f"{nome_arquivo}.json")

        return jsonify(
            {
                "sucesso": True,
                "termo_busca": termo,
                "total_encontrados": len(produtos),
                "arquivo_salvo": f"{nome_arquivo}.json",
            }
        )

    except Exception as e:
        return jsonify({"sucesso": False, "erro": str(e)}), 500


if __name__ == "__main__":
    print("API DE BUSCA DE PREÇOS")
    app.run(debug=True, port=5000)
