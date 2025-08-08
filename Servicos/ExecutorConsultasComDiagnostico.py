import threading
import time
import logging
from Servicos.ConexaoFirebird import ConexaoFirebird
from Modelos.ConsultasSql import ConsultasSql
from Modelos.ConfiguracaoExecucao import ConfiguracaoExecucao

class ExecutorConsultasComDiagnostico:
    def __init__(self, configuracao_banco, modo_alta_carga=False):
        self.configuracao = configuracao_banco
        self.modo_alta_carga = modo_alta_carga
        self.executores_consultas = []
        self.executando = False
        self.conexao_ativa = False
        self.ultimo_erro = None
        self.logger = logging.getLogger(f'SimuladorCarga.ExecutorComDiagnostico.{configuracao_banco.nome_banco}')
        
        self.config = ConfiguracaoExecucao.obter_configuracao_alta_carga() if modo_alta_carga else ConfiguracaoExecucao.obter_configuracao_normal()
    
    def iniciar_execucao(self):
        if not self.executando:
            self.executando = True
            self.conexao_ativa = False
            self.ultimo_erro = None
            self.executores_consultas = []
            
            # Primeiro testa a conexão
            if self._testar_conexao_inicial():
                self._iniciar_threads_consultas()
            else:
                self.logger.error(f"Falha no teste inicial de conexão para {self.configuracao.nome_banco}")
                self.executando = False
    
    def _testar_conexao_inicial(self):
        try:
            self.logger.debug(f"Testando conexão inicial: {self.configuracao}")
            
            conexao_teste = ConexaoFirebird(self.configuracao, "TESTE")
            if conexao_teste.conectar():
                # Testa uma consulta simples
                sucesso = conexao_teste.executar_consulta("SELECT FIRST 1 * FROM RDB$DATABASE")
                conexao_teste.desconectar()
                
                if sucesso:
                    self.conexao_ativa = True
                    self.logger.info(f"✅ Teste de conexão OK: {self.configuracao.nome_banco}")
                    return True
                else:
                    self.ultimo_erro = "Falha ao executar consulta de teste"
                    return False
            else:
                self.ultimo_erro = "Falha ao conectar"
                return False
                
        except Exception as e:
            self.ultimo_erro = str(e)
            self.logger.error(f"Erro no teste de conexão: {e}")
            return False
    
    def _iniciar_threads_consultas(self):
        consultas_com_nome = ConsultasSql.obter_consultas_com_nome()
        threads_por_consulta = self.config['threads_por_loja'] // len(consultas_com_nome)
        threads_por_consulta = max(1, threads_por_consulta)  # Mínimo 1 thread por consulta
        
        self.logger.info(f"Iniciando {threads_por_consulta} threads por consulta para {self.configuracao.nome_banco}")
        
        for nome_consulta, sql_consulta in consultas_com_nome.items():
            for thread_id in range(threads_por_consulta):
                executor = ExecutorConsultaUnicaComDiagnostico(
                    self.configuracao,
                    nome_consulta,
                    sql_consulta,
                    thread_id,
                    self.config['intervalo_consultas']
                )
                self.executores_consultas.append(executor)
                executor.iniciar_execucao()
    
    def parar_execucao(self):
        if self.executando:
            self.executando = False
            self.logger.info(f"Parando {len(self.executores_consultas)} threads para {self.configuracao.nome_banco}")
            
            for executor in self.executores_consultas:
                executor.parar_execucao()
            
            self.executores_consultas = []
            self.conexao_ativa = False
    
    def obter_estatisticas(self):
        if not self.executando:
            return None
        
        stats_por_consulta = {}
        total_consultas = 0
        total_erros = 0
        threads_ativas = 0
        threads_total = len(self.executores_consultas)
        
        for executor in self.executores_consultas:
            nome_consulta = executor.nome_consulta
            if nome_consulta not in stats_por_consulta:
                stats_por_consulta[nome_consulta] = {'consultas': 0, 'erros': 0, 'threads_ativas': 0, 'threads_total': 0}
            
            stats = executor.obter_estatisticas()
            stats_por_consulta[nome_consulta]['consultas'] += stats['consultas_executadas']
            stats_por_consulta[nome_consulta]['erros'] += stats['erros']
            stats_por_consulta[nome_consulta]['threads_total'] += 1
            
            if stats['ativo']:
                stats_por_consulta[nome_consulta]['threads_ativas'] += 1
                threads_ativas += 1
            
            total_consultas += stats['consultas_executadas']
            total_erros += stats['erros']
        
        return {
            'consultas_por_tipo': stats_por_consulta,
            'total_consultas': total_consultas,
            'total_erros': total_erros,
            'threads_ativas': threads_ativas,
            'threads_total': threads_total,
            'conexao_ativa': self.conexao_ativa,
            'ultimo_erro': self.ultimo_erro
        }

class ExecutorConsultaUnicaComDiagnostico:
    def __init__(self, configuracao_banco, nome_consulta, sql_consulta, thread_id, intervalo_consultas=None):
        self.configuracao = configuracao_banco
        self.nome_consulta = nome_consulta
        self.sql_consulta = sql_consulta
        self.thread_id = thread_id
        self.executando = False
        self.thread = None
        self.contador_consultas = 0
        self.contador_erros = 0
        self.intervalo_consultas = intervalo_consultas or 0.02
        self.logger = logging.getLogger(f'SimuladorCarga.{configuracao_banco.nome_banco}.{nome_consulta}.Thread{thread_id}')
    
    def iniciar_execucao(self):
        if not self.executando:
            self.executando = True
            self.contador_consultas = 0
            self.contador_erros = 0
            self.thread = threading.Thread(
                target=self._executar_loop, 
                name=f"Executor-{self.configuracao.nome_banco}-{self.nome_consulta}-{self.thread_id}"
            )
            self.thread.daemon = True
            self.thread.start()
            self.logger.debug(f"Thread {self.thread_id} iniciada para {self.nome_consulta}")
    
    def parar_execucao(self):
        if self.executando:
            self.executando = False
            if self.thread:
                self.thread.join(timeout=5)
            self.logger.debug(f"Thread {self.thread_id} parada - {self.nome_consulta} - Consultas: {self.contador_consultas}")
    
    def _executar_loop(self):
        conexao = ConexaoFirebird(self.configuracao, f"{self.nome_consulta}-{self.thread_id}")
        
        if not conexao.conectar():
            self.logger.error(f"Thread {self.thread_id} - Falha ao conectar para {self.nome_consulta}")
            self.executando = False
            return
        
        self.logger.debug(f"Thread {self.thread_id} - Iniciando execução de {self.nome_consulta}")
        
        while self.executando:
            try:
                if conexao.executar_consulta(self.sql_consulta):
                    self.contador_consultas += 1
                    if self.contador_consultas % 100 == 0:
                        self.logger.info(f"Thread {self.thread_id} - {self.nome_consulta}: {self.contador_consultas} consultas")
                else:
                    self.contador_erros += 1
                
                if self.intervalo_consultas > 0:
                    time.sleep(self.intervalo_consultas)
                    
            except Exception as e:
                self.contador_erros += 1
                self.logger.error(f"Thread {self.thread_id} - Erro inesperado: {e}")
                time.sleep(1)
        
        conexao.desconectar()
        self.logger.debug(f"Thread {self.thread_id} - Loop finalizado para {self.nome_consulta}")
    
    def obter_estatisticas(self):
        return {
            'consultas_executadas': self.contador_consultas,
            'erros': self.contador_erros,
            'ativo': self.executando
        }