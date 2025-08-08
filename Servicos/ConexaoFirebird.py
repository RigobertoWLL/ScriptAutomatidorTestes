import fdb
import time
import logging
from Modelos.ConfiguracaoExecucao import ConfiguracaoExecucao

class ConexaoFirebird:
    def __init__(self, configuracao_banco, identificador_thread=""):
        self.configuracao = configuracao_banco
        self.identificador_thread = identificador_thread
        self.conexao = None
        self.logger = logging.getLogger(f'SimuladorCarga.ConexaoFirebird.{configuracao_banco.nome_banco}.{identificador_thread}')
        self.tentativas_reconexao = 0
    
    def conectar(self):
        try:
            self.logger.debug(f"Conectando ao banco: {self.configuracao} - Thread: {self.identificador_thread}")
            self.conexao = fdb.connect(
                host=self.configuracao.ip,
                port=int(self.configuracao.porta),
                database=self.configuracao.nome_banco,
                user='CCL',
                password='w_0rR-HbMomsH7vO917',
                role='R_CCL'
            )
            self.logger.debug(f"Conexão estabelecida - {self.identificador_thread}")
            self.tentativas_reconexao = 0
            return True
        except Exception as e:
            self.logger.error(f"Erro ao conectar - {self.identificador_thread}: {e}")
            return False
    
    def reconectar(self):
        if self.tentativas_reconexao >= ConfiguracaoExecucao.TENTATIVAS_RECONEXAO:
            self.logger.error(f"Máximo de tentativas de reconexão atingido - {self.identificador_thread}")
            return False
        
        self.desconectar()
        self.tentativas_reconexao += 1
        self.logger.warning(f"Tentativa de reconexão {self.tentativas_reconexao}/{ConfiguracaoExecucao.TENTATIVAS_RECONEXAO} - {self.identificador_thread}")
        time.sleep(ConfiguracaoExecucao.INTERVALO_RECONEXAO)
        return self.conectar()
    
    def executar_consulta(self, sql):
        if not self.conexao:
            if not self.reconectar():
                return False
        
        try:
            inicio = time.time()
            cursor = self.conexao.cursor()
            cursor.execute(sql)
            resultado = cursor.fetchall()
            cursor.close()
            tempo_execucao = time.time() - inicio
            
            self.logger.debug(f"Consulta executada - {self.identificador_thread} - Tempo: {tempo_execucao:.3f}s - Registros: {len(resultado)}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao executar consulta - {self.identificador_thread}: {e}")
            if not self.reconectar():
                return False
            return False
    
    def desconectar(self):
        if self.conexao:
            try:
                self.conexao.close()
                self.conexao = None
                self.logger.debug(f"Conexão fechada - {self.identificador_thread}")
            except Exception as e:
                self.logger.error(f"Erro ao fechar conexão - {self.identificador_thread}: {e}")