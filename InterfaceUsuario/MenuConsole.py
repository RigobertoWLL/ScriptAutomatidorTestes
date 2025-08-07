import time
from Controladores.GerenciadorCarga import GerenciadorCarga

class MenuConsole:
    def __init__(self):
        self.gerenciador = GerenciadorCarga('ListaBanco.ini')
    
    def exibir_menu_principal(self):
        while True:
            print("\n=== SIMULADOR DE CARGA FIREBIRD ===")
            print("1 - Iniciar simulação")
            print("2 - Parar simulação")
            print("3 - Status da simulação")
            print("4 - Sair")
            print("=" * 35)
            
            opcao = input("Escolha uma opção: ")
            
            if opcao == '1':
                self._iniciar_simulacao()
            elif opcao == '2':
                self._parar_simulacao()
            elif opcao == '3':
                self._exibir_status()
            elif opcao == '4':
                self._sair_aplicacao()
                break
            else:
                print("Opção inválida!")
    
    def _iniciar_simulacao(self):
        print("Iniciando simulação de carga...")
        self.gerenciador.iniciar_simulacao_carga()
        print("Simulação iniciada com sucesso!")
    
    def _parar_simulacao(self):
        print("Parando simulação de carga...")
        self.gerenciador.parar_simulacao_carga()
        print("Simulação parada com sucesso!")
    
    def _exibir_status(self):
        status = "EXECUTANDO" if self.gerenciador.obter_status_execucao() else "PARADO"
        print(f"Status da simulação: {status}")
    
    def _sair_aplicacao(self):
        if self.gerenciador.obter_status_execucao():
            self.gerenciador.parar_simulacao_carga()
        print("Encerrando aplicação...")