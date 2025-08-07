import threading
from Servicos.LeitorArquivoIni import LeitorArquivoIni
from Servicos.ExecutorConsultas import ExecutorConsultas

class GerenciadorCarga:
    def __init__(self, caminho_arquivo_ini):
        self.caminho_arquivo = caminho_arquivo_ini
        self.executores = []
        self.executando = False
    
    def iniciar_simulacao_carga(self):
        if self.executando:
            return
        
        leitor = LeitorArquivoIni(self.caminho_arquivo)
        configuracoes = leitor.carregar_configuracoes()
        
        self.executores = []
        for config in configuracoes:
            executor = ExecutorConsultas(config)
            self.executores.append(executor)
        
        for executor in self.executores:
            executor.iniciar_execucao()
        
        self.executando = True
    
    def parar_simulacao_carga(self):
        if not self.executando:
            return
        
        for executor in self.executores:
            executor.parar_execucao()
        
        self.executores = []
        self.executando = False
    
    def obter_status_execucao(self):
        return self.executando