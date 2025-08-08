import time
import logging
from Controladores.GerenciadorCargaComDiagnostico import GerenciadorCargaComDiagnostico

class MenuConsoleComDiagnostico:
    def __init__(self):
        self.gerenciador = GerenciadorCargaComDiagnostico('ListaBanco.ini')
        self.logger = logging.getLogger('SimuladorCarga.MenuConsoleComDiagnostico')
    
    def exibir_menu_principal(self):
        self.logger.info("Aplicação com diagnóstico iniciada")
        
        while True:
            print("\n" + "=" * 75)
            print("🔥 SIMULADOR DE CARGA FIREBIRD - COM DIAGNÓSTICO 🔥")
            print("🔍 SISTEMA COM DETECÇÃO DE PROBLEMAS DE CONECTIVIDADE")
            print("📊 MÁXIMO 8 CONSULTAS SIMULTÂNEAS POR IP")
            print("=" * 75)
            print("1 - Iniciar simulação (Modo Normal)")
            print("2 - Iniciar simulação (Modo Alta Carga)")
            print("3 - Parar simulação")
            print("4 - Status da simulação")
            print("5 - Estatísticas com diagnóstico")
            print("6 - Resumo de IPs e conexões")
            print("7 - Monitor em tempo real")
            print("8 - Sair")
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
    
    def _iniciar_simulacao(self, modo_alta_carga):
        modo_texto = "Alta Carga" if modo_alta_carga else "Normal"
        
        print(f"\n🔍 Iniciando simulação com diagnóstico - Modo: {modo_texto}")
        print("🔬 Executando testes de conectividade...")
        print("⏳ Aguarde o diagnóstico inicial...")
        
        self.gerenciador.iniciar_simulacao_carga(modo_alta_carga)
        print("\n✅ Simulação com diagnóstico iniciada!")
        print("🔍 Problemas de conectividade serão detectados automaticamente")
    
    def _parar_simulacao(self):
        print("🛑 Parando simulação...")
        self.gerenciador.parar_simulacao_carga()
        print("✅ Simulação parada!")
    
    def _exibir_status(self):
        status = "🟢 EXECUTANDO" if self.gerenciador.obter_status_execucao() else "🔴 PARADO"
        print(f"Status: {status}")
    
    def _exibir_estatisticas(self):
        estatisticas = self.gerenciador.obter_estatisticas_completas()
        if estatisticas:
            print("\n" + "=" * 90)
            print("🔍 ESTATÍSTICAS COM DIAGNÓSTICO")
            print("=" * 90)
            
            totais = estatisticas.get('TOTAIS_GERAIS', {})
            if totais:
                print(f"🔗 THREADS ATIVAS: {totais.get('threads_ativas', 0)}/{totais.get('threads_total', 0)}")
                print(f"🔌 CONEXÕES ATIVAS: {totais.get('conexoes_ativas_total', 0)}")
                print(f"📈 CONSULTAS: {totais.get('total_consultas', 0):,}")
                print(f"❌ ERROS: {totais.get('total_erros', 0)}")
                print(f"🖥️  IPs ATIVOS: {totais.get('ips_ativos', 0)}/{totais.get('ips_únicos', 0)}")
                print("=" * 90)
            
            for ip_porta, stats in estatisticas.items():
                if ip_porta != 'TOTAIS_GERAIS':
                    conexoes = stats.get('conexoes_ativas', 0)
                    status_conexao = "🟢" if conexoes > 0 else "🔴"
                    
                    print(f"\n{status_conexao} IP: {ip_porta}")
                    print(f"   🔌 Conexões: {conexoes}/{stats.get('total_lojas_ativas', 0)}")
                    print(f"   🔗 Threads: {stats.get('threads_ativas', 0)}/{stats.get('threads_total', 0)}")
                    print(f"   📈 Consultas: {stats.get('total_consultas', 0):,}")
                    print(f"   ❌ Erros: {stats.get('total_erros', 0)}")
                    print("   " + "-" * 50)
        else:
            print("❌ Simulação não está em execução")
    
    def _exibir_resumo_ips(self):
        resumo = self.gerenciador.obter_resumo_ips()
        if resumo:
            print("\n" + "=" * 90)
            print("🔍 RESUMO COM DIAGNÓSTICO DE CONECTIVIDADE")
            print("=" * 90)
            print(f"{'IP:PORTA':<20} {'ATIVAS':<8} {'FILA':<8} {'CONSULTAS':<12} {'THREADS':<10} {'CONEXÕES':<10}")
            print("-" * 90)
            
            for ip_info in resumo:
                ip_porta = ip_info['ip_porta']
                ativas = f"{ip_info['lojas_ativas']}/8"
                fila = ip_info['lojas_fila']
                consultas = ip_info['consultas']
                threads = ip_info['threads_ativas']
                conexoes = ip_info['conexoes_ativas']
                
                status = "🟢" if conexoes > 0 else "🔴"
                
                print(f"{status} {ip_porta:<18} {ativas:<8} {fila:<8} {consultas:<12,} {threads:<10} {conexoes:<10}")
            
            print("=" * 90)
        else:
            print("❌ Simulação não está em execução")
    
    def _monitor_tempo_real(self):
        if not self.gerenciador.obter_status_execucao():
            print("❌ Simulação não está em execução")
            return
        
        print("\n" + "=" * 80)
        print("📡 MONITOR COM DIAGNÓSTICO EM TEMPO REAL")
        print("=" * 80)
        print("Pressione Ctrl+C para voltar ao menu")
        print("-" * 80)
        
        try:
            while self.gerenciador.obter_status_execucao():
                estatisticas = self.gerenciador.obter_estatisticas_completas()
                if estatisticas and 'TOTAIS_GERAIS' in estatisticas:
                    totais = estatisticas['TOTAIS_GERAIS']
                    consultas = totais.get('total_consultas', 0)
                    erros = totais.get('total_erros', 0)
                    threads = totais.get('threads_ativas', 0)
                    conexoes = totais.get('conexoes_ativas_total', 0)
                    ips_ativos = totais.get('ips_ativos', 0)
                    ips_total = totais.get('ips_únicos', 0)
                    
                    print(f"\r🔥 {consultas:,} consultas | ❌ {erros} erros | 🔗 {threads} threads | 🔌 {conexoes} conexões | 🖥️  {ips_ativos}/{ips_total} IPs", 
                          end='', flush=True)
                
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n🔙 Voltando ao menu...")
    
    def _sair_aplicacao(self):
        if self.gerenciador.obter_status_execucao():
            self.gerenciador.parar_simulacao_carga()
        print("👋 Encerrando...")