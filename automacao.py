"""
Script de Automação - Executa busca de preços automaticamente
"""

import schedule
import time
from datetime import datetime
from buscador_precos import BuscadorPrecos


class AutomacaoBusca:
    def __init__(self):
        self.buscador = BuscadorPrecos()
        self.produtos_para_monitorar = []

    def adicionar_produto_monitoramento(self, termo: str):
        """Adiciona produto para monitoramento automático"""
        if termo not in self.produtos_para_monitorar:
            self.produtos_para_monitorar.append(termo)
            print(f"✓ '{termo}' adicionado ao monitoramento")

    def executar_busca(self):
        """Executa busca para todos os produtos monitorados"""
        print("\n" + "=" * 70)
        print(f"🤖 AUTOMAÇÃO INICIADA - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print("=" * 70)

        for produto in self.produtos_para_monitorar:
            try:
                print(f"\n🔍 Buscando: {produto}")

                # Busca o produto
                resultados = self.buscador.buscar_produto(produto)

                if resultados:
                    # Salva arquivos
                    nome_arquivo = produto.replace(" ", "_").lower()
                    self.buscador.salvar_json(f"{nome_arquivo}.json")
                    self.buscador.gerar_html(f"{nome_arquivo}.html")

                    # Mostra melhor preço
                    melhor = resultados[0]
                    print(
                        f"💰 Melhor preço: {melhor['preco_formatado']} - {melhor['site']}"
                    )
                else:
                    print(f"⚠️  Nenhum resultado encontrado para '{produto}'")

                # Aguarda entre buscas
                time.sleep(3)

            except Exception as e:
                print(f"❌ Erro ao buscar '{produto}': {e}")

        print("\n" + "=" * 70)
        print(
            f"✅ AUTOMAÇÃO CONCLUÍDA - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        )
        print("=" * 70 + "\n")

    def iniciar_modo_continuo(self, intervalo_horas: int = 6):
        """
        Inicia modo de execução contínua

        Args:
            intervalo_horas: Intervalo entre execuções (padrão: 6 horas)
        """
        print("🚀 Iniciando modo contínuo...")
        print(f"⏱️  Intervalo: a cada {intervalo_horas} horas")
        print(f"📋 Produtos monitorados: {len(self.produtos_para_monitorar)}")
        print("\nPressione Ctrl+C para parar\n")

        # Executa imediatamente a primeira vez
        self.executar_busca()

        # Agenda execuções futuras
        schedule.every(intervalo_horas).hours.do(self.executar_busca)

        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Verifica a cada minuto
            except KeyboardInterrupt:
                print("\n\n⏹️  Automação interrompida pelo usuário")
                break

    def iniciar_horarios_fixos(self, horarios: list):
        """
        Inicia com horários fixos do dia

        Args:
            horarios: Lista de horários no formato "HH:MM" (ex: ["09:00", "15:00"])
        """
        print("🚀 Iniciando com horários fixos...")
        print(f"⏰ Horários programados: {', '.join(horarios)}")
        print(f"📋 Produtos monitorados: {len(self.produtos_para_monitorar)}")
        print("\nPressione Ctrl+C para parar\n")

        # Agenda para cada horário
        for horario in horarios:
            schedule.every().day.at(horario).do(self.executar_busca)

        while True:
            try:
                schedule.run_pending()
                time.sleep(60)
            except KeyboardInterrupt:
                print("\n\n⏹️  Automação interrompida pelo usuário")
                break


def exemplo_uso_basico():
    """Exemplo 1: Execução única"""
    automacao = AutomacaoBusca()

    # Adiciona produtos para monitorar
    automacao.adicionar_produto_monitoramento("notebook")
    automacao.adicionar_produto_monitoramento("smartphone samsung")

    # Executa busca única
    automacao.executar_busca()


def exemplo_modo_continuo():
    """Exemplo 2: Execução contínua a cada X horas"""
    automacao = AutomacaoBusca()

    # Configura produtos
    automacao.adicionar_produto_monitoramento("notebook")
    automacao.adicionar_produto_monitoramento("monitor")
    automacao.adicionar_produto_monitoramento("teclado mecanico")

    # Inicia execução a cada 4 horas
    automacao.iniciar_modo_continuo(intervalo_horas=4)


def exemplo_horarios_fixos():
    """Exemplo 3: Execução em horários específicos"""
    automacao = AutomacaoBusca()

    # Configura produtos
    automacao.adicionar_produto_monitoramento("notebook dell")
    automacao.adicionar_produto_monitoramento("iphone")

    # Executa 3x ao dia: 9h, 15h e 21h
    automacao.iniciar_horarios_fixos(["09:00", "15:00", "21:00"])


if __name__ == "__main__":
    print(
        """
╔════════════════════════════════════════════════════════════╗
║        🤖 AUTOMAÇÃO DE BUSCA DE PREÇOS                     ║
╚════════════════════════════════════════════════════════════╝

Escolha o modo de execução:

1 - Execução única (roda agora e para)
2 - Modo contínuo (roda a cada X horas)
3 - Horários fixos (roda em horários específicos)

Digite o número da opção: """,
        end="",
    )

    try:
        opcao = input().strip()

        if opcao == "1":
            exemplo_uso_basico()
        elif opcao == "2":
            print("\nQuantas horas entre cada execução? (padrão: 6): ", end="")
            horas = input().strip()
            horas = int(horas) if horas else 6

            automacao = AutomacaoBusca()
            # CONFIGURE AQUI SEUS PRODUTOS
            automacao.adicionar_produto_monitoramento("notebook")
            automacao.adicionar_produto_monitoramento("smartphone")

            automacao.iniciar_modo_continuo(intervalo_horas=horas)
        elif opcao == "3":
            print(
                "\nDigite os horários separados por vírgula (ex: 09:00,15:00,21:00): ",
                end="",
            )
            horarios_input = input().strip()
            horarios = [h.strip() for h in horarios_input.split(",")]

            automacao = AutomacaoBusca()
            # CONFIGURE AQUI SEUS PRODUTOS
            automacao.adicionar_produto_monitoramento("notebook")
            automacao.adicionar_produto_monitoramento("smartphone")

            automacao.iniciar_horarios_fixos(horarios)
        else:
            print("❌ Opção inválida!")

    except Exception as e:
        print(f"\n❌ Erro: {e}")
