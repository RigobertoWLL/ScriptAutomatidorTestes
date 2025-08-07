import time
import logging
from Controladores.GerenciadorCarga import GerenciadorCarga


class MenuConsole:
    def __init__(self):
        self.gerenciador = GerenciadorCarga('ListaBanco.ini')
        self.logger = logging.getLogger('SimuladorCarga.MenuConsole')

    def exibir_menu_principal(self):
        self.logger.info("Aplicação iniciada - Menu principal exibido")

        while True:
            print("\n" + "=" * 75)
            print("🔥 SIMULADOR DE CARGA FIREBIRD - CONTROLE POR IP 🔥")
            print("📊 MÁXIMO 8 CONSULTAS SIMULTÂNEAS POR IP")
            print("🔄 SISTEMA DE FILA PARA TODAS AS LOJAS")
            print("=" * 75)
            print("1 - Iniciar simulação (Modo Normal - 5 threads/loja)")
            print("2 - Iniciar simulação (Modo Alta Carga - 10 threads/loja)")
            print("3 - Parar simulação")
            print("4 - Status da simulação")
            print("5 - Estatísticas por IP")
            print("6 - Resumo de IPs e filas")
            print("7 - Monitor em tempo real")
            print("8 - Sair")
            print("=" * 75)
            print("CONSULTAS: SP_GERENCIAL • SP_DRE • EMPRESA • PRODUTOS • CLIENTES")
            print("GARANTIA: Todas as lojas serão processadas (sistema de fila)")
            print("=" * 75)

            opcao = input("Escolha uma opção: ")
            self.logger.info(f"Opção selecionada: {opcao}")

            if opcao == '1':
                self._iniciar_simulacao(False)
            elif opcao == '2':
                self._iniciar_simulacao(True)
            elif opcao == '3':
                self._parar_simulacao()
            elif opcao == '4':
                self._exibir_status()
            elif opcao == '5':
                self._exibir_estatisticas()
            elif opcao == '6':
                self._exibir_resumo_ips()
            elif opcao == '7':
                self._monitor_tempo_real()
            elif opcao == '8':
                self._sair_aplicacao()
                break
            else:
                print("❌ Opção inválida!")
                self.logger.warning(f"Opção inválida selecionada: {opcao}")

    def _iniciar_simulacao(self, modo_alta_carga):
        threads_por_loja = 10 if modo_alta_carga else 5
        modo_texto = f"Alta Carga ({threads_por_loja} threads/loja)" if modo_alta_carga else f"Normal ({threads_por_loja} threads/loja)"

        print(f"\n🚀 Iniciando simulação - Modo: {modo_texto}")
        print("📊 Máximo de 8 consultas simultâneas por IP")
        print("🔄 Sistema de fila ativo para processar todas as lojas")
        print("⏳ Aguarde enquanto o sistema organiza as filas...")

        self.gerenciador.iniciar_simulacao_carga(modo_alta_carga)
        print("\n✅ Simulação iniciada com sucesso!")
        print("🎯 TODAS AS LOJAS SERÃO PROCESSADAS RESPEITANDO O LIMITE POR IP!")

    def _parar_simulacao(self):
        print("🛑 Parando simulação de carga...")
        self.gerenciador.parar_simulacao_carga()
        print("✅ Simulação parada com sucesso!")

    def _exibir_status(self):
        status = "🟢 EXECUTANDO" if self.gerenciador.obter_status_execucao() else "🔴 PARADO"
        print(f"Status da simulação: {status}")
        self.logger.info(f"Status consultado: {status}")

    def _exibir_estatisticas(self):
        estatisticas = self.gerenciador.obter_estatisticas_completas()
        if estatisticas:
            print("\n" + "=" * 90)
            print("📊 ESTATÍSTICAS DETALHADAS POR IP")
            print("=" * 90)

            totais = estatisticas.get('TOTAIS_GERAIS', {})
            if totais:
                modo = "ALTA CARGA" if totais.get('modo_alta_carga') else "NORMAL"
                print(f"🔥 MODO: {modo}")
                print(f"🖥️  IPs ÚNICOS: {totais.get('ips_únicos', 0)}")
                print(f"✅ IPs ATIVOS: {totais.get('ips_ativos', 0)}")
                print(f"🏪 LOJAS ATIVAS: {totais.get('lojas_ativas_total', 0)}")
                print(f"⏳ LOJAS NA FILA: {totais.get('lojas_na_fila', 0)}")
                print(f"🔗 THREADS: {totais.get('threads_ativas', 0)}/{totais.get('threads_total', 0)}")
                print(f"📈 CONSULTAS: {totais.get('total_consultas', 0):,}")
                print(f"❌ ERROS: {totais.get('total_erros', 0)}")
                print(f"🎯 LIMITE POR IP: {totais.get('limite_por_ip', 0)}")
                print("=" * 90)

            for ip_porta, stats in estatisticas.items():
                if ip_porta != 'TOTAIS_GERAIS':
                    print(f"\n🖥️  IP: {ip_porta}")
                    print(f"   🏪 Lojas Ativas: {stats.get('total_lojas_ativas', 0)}/{stats.get('limite_maximo', 8)}")
                    print(f"   ⏳ Fila de Espera: {stats.get('fila_aguardando', 0)} lojas")
                    print(f"   🔗 Threads: {stats.get('threads_ativas', 0)}/{stats.get('threads_total', 0)}")
                    print(f"   📈 Consultas: {stats.get('total_consultas', 0):,}")
                    print(f"   ❌ Erros: {stats.get('total_erros', 0)}")

                    lojas_ativas = stats.get('lojas_ativas', {})
                    if lojas_ativas:
                        print(f"   📋 Lojas em execução:")
                        for nome_loja, dados_loja in list(lojas_ativas.items())[:3]:
                            print(f"      • {nome_loja}: {dados_loja.get('total_consultas', 0)} consultas")
                        if len(lojas_ativas) > 3:
                            print(f"      ... e mais {len(lojas_ativas) - 3} lojas")

                    print("   " + "-" * 60)
        else:
            print("❌ Simulação não está em execução")

    def _exibir_resumo_ips(self):
        resumo = self.gerenciador.obter_resumo_ips()
        if resumo:
            print("\n" + "=" * 85)
            print("🖥️  RESUMO DE CONTROLE POR IP")
            print("=" * 85)
            print(f"{'IP:PORTA':<20} {'ATIVAS':<8} {'FILA':<8} {'CONSULTAS':<12} {'THREADS':<10} {'USO%':<8}")
            print("-" * 85)

            for ip_info in resumo:
                ip_porta = ip_info['ip_porta']
                ativas = f"{ip_info['lojas_ativas']}/8"
                fila = ip_info['lojas_fila']
                consultas = ip_info['consultas']
                threads = ip_info['threads_ativas']
                uso = f"{ip_info['percentual_uso']:.1f}%"

                print(f"{ip_porta:<20} {ativas:<8} {fila:<8} {consultas:<12,} {threads:<10} {uso:<8}")

            print("=" * 85)
            print(f"✅ TOTAL DE IPs ÚNICOS: {len(resumo)}")
            print("🎯 CADA IP LIMITADO A MÁXIMO 8 CONSULTAS SIMULTÂNEAS")
            print("🔄 SISTEMA DE FILA GARANTE QUE TODAS AS LOJAS SEJAM PROCESSADAS")
        else:
            print("❌ Simulação não está em execução")

    def _monitor_tempo_real(self):
        if not self.gerenciador.obter_status_execucao():
            print("❌ Simulação não está em execução")
            return

        print("\n" + "=" * 70)
        print("📡 MONITOR EM TEMPO REAL - CONTROLE POR IP")
        print("=" * 70)
        print("Pressione Ctrl+C para voltar ao menu")
        print("-" * 70)

        try:
            contador = 0
            while self.gerenciador.obter_status_execucao():
                estatisticas = self.gerenciador.obter_estatisticas_completas()
                if estatisticas and 'TOTAIS_GERAIS' in estatisticas:
                    totais = estatisticas['TOTAIS_GERAIS']
                    consultas = totais.get('total_consultas', 0)
                    erros = totais.get('total_erros', 0)
                    threads = totais.get('threads_ativas', 0)
                    lojas_ativas = totais.get('lojas_ativas_total', 0)
                    lojas_fila = totais.get('lojas_na_fila', 0)
                    ips_ativos = totais.get('ips_ativos', 0)
                    ips_total = totais.get('ips_únicos', 0)

                    print(
                        f"\r🔥 {consultas:,} consultas | ❌ {erros} erros | 🔗 {threads} threads | 🏪 {lojas_ativas} ativas | ⏳ {lojas_fila} fila | 🖥️  {ips_ativos}/{ips_total} IPs",
                        end='', flush=True)

                    contador += 1
                    if contador % 30 == 0:
                        print()
                        print("📊 Top 5 IPs por consultas:")
                        resumo = self.gerenciador.obter_resumo_ips()
                        if resumo:
                            for i, ip_info in enumerate(resumo[:5], 1):
                                print(
                                    f"   {i}. {ip_info['ip_porta']}: {ip_info['consultas']:,} consultas, {ip_info['lojas_ativas']}/8 ativas")
                        print("-" * 70)

                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n🔙 Voltando ao menu...")

    def _sair_aplicacao(self):
        self.logger.info("Encerrando aplicação")
        if self.gerenciador.obter_status_execucao():
            print("🛑 Parando simulação antes de sair...")
            self.gerenciador.parar_simulacao_carga()
        print("👋 Encerrando aplicação...")