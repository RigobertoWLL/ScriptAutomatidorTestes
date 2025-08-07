import threading
import time
from Servicos.ConexaoFirebird import ConexaoFirebird
from Modelos.ConsultasSql import ConsultasSql

class ExecutorConsultas:
    def __init__(self, configuracao_banco):
        self.configuracao = configuracao_banco
        self.executando = False
        self.thread = None
    
    def iniciar_execucao(self):
        if not self.executando:
            self.executando = True
            self.thread = threading.Thread(target=self._executar_loop)
            self.thread.daemon = True
            self.thread.start()
    
    def parar_execucao(self):
        self.executando = False
        if self.thread:
            self.thread.join()
    
    def _executar_loop(self):
        conexao = ConexaoFirebird(self.configuracao)
        
        if not conexao.conectar():
            return
        
        consultas = ConsultasSql.obter_todas_consultas()
        
        while self.executando:
            for consulta in consultas:
                if not self.executando:
                    break
                conexao.executar_consulta(consulta)
                time.sleep(0.1)
        
        conexao.desconectar()