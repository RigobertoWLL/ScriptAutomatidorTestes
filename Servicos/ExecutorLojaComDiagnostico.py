import threading
import time
import logging
from Servicos.ExecutorConsultasComDiagnostico import ExecutorConsultasComDiagnostico
from Servicos.DiagnosticoConexao import DiagnosticoConexao
from Modelos.ConfiguracaoExecucao import ConfiguracaoExecucao

class ExecutorLojaComDiagnostico:
    def __init__(self, ip_porta, gerenciador_fila, modo_alta_carga=False):
        self.ip_porta = ip_porta
        self.gerenciador_fila = gerenciador_fila
        self.modo_alta_carga = modo_alta_carga
        self.executores_ativos = {}
        self.executando = False
        self.thread_gerenciador = None
        self.config = ConfiguracaoExecucao.obter_configuracao_alta_carga() if modo_alta_carga else ConfiguracaoExecucao.obter_configuracao_normal()
        self.logger = logging.getLogger(f'SimuladorCarga.ExecutorComDiagnostico.{ip_porta}')
        self.diagnostico = DiagnosticoConexao()
    
    def iniciar_execucao(self):
        if not self.executando:
            self.executando = True
            self.executores_ativos = {}
            
            # Primeiro faz diagnóstico do IP
            self._diagnosticar_ip()
            
            self.thread_gerenciador = threading.Thread(target=self._gerenciar_fila_lojas, name=f"GerenciadorDiag-{self.ip_porta}")
            self.thread_gerenciador.daemon = True
            self.thread_gerenciador.start()
            self.logger.info(f"Gerenciador com diagnóstico iniciado para IP {self.ip_porta}")
    
    def _diagnosticar_ip(self):
        # Pega uma loja de exemplo para testar o IP
        loja_teste = self.gerenciador_fila.obter_proxima_loja(self.ip_porta)
        if loja_teste:
            ip, porta = self.ip_porta.split(':')
            sucesso, mensagem = self.diagnostico.testar_conexao_ip(ip, porta, loja_teste.nome_banco)
            
            if sucesso:
                self.logger.info(f"✅ Diagnóstico OK para IP {self.ip_porta}")
            else:
                self.logger.error(f"❌ Diagnóstico FALHOU para IP {self.ip_porta}: {mensagem}")
            
            # Retorna a loja para a fila
            self.gerenciador_fila.liberar_loja(self.ip_porta, loja_teste.nome_banco)
    
    def parar_execucao(self):
        if self.executando:
            self.executando = False
            
            for nome_loja, executor in self.executores_ativos.items():
                executor.parar_execucao()
                self.gerenciador_fila.liberar_loja(self.ip_porta, nome_loja)
            
            if self.thread_gerenciador:
                self.thread_gerenciador.join(timeout=10)
            
            self.executores_ativos.clear()
            self.logger.info(f"Gerenciador com diagnóstico parado para IP {self.ip_porta}")
    
    def _gerenciar_fila_lojas(self):
        self.logger.debug(f"Iniciando gerenciamento com diagnóstico para IP {self.ip_porta}")
        
        contador_ciclos = 0
        while self.executando:
            try:
                self._processar_fila()
                self._remover_executores_finalizados()
                
                contador_ciclos += 1
                if contador_ciclos % 30 == 0:  # Log a cada 30 ciclos
                    self.logger.debug(f"IP {self.ip_porta} - Ciclo {contador_ciclos} - Ativos: {len(self.executores_ativos)}")
                
                time.sleep(self.config['intervalo_verificacao'])
            except Exception as e:
                self.logger.error(f"Erro no gerenciamento da fila para IP {self.ip_porta}: {e}")
                time.sleep(5)
        
        self.logger.debug(f"Gerenciamento com diagnóstico finalizado para IP {self.ip_porta}")
    
    def _processar_fila(self):
        slots_disponiveis = ConfiguracaoExecucao.MAX_CONSULTAS_POR_IP - len(self.executores_ativos)
        
        for _ in range(slots_disponiveis):
            if not self.executando:
                break
            
            loja = self.gerenciador_fila.obter_proxima_loja(self.ip_porta)
            if loja:
                self._iniciar_executor_loja(loja)
            else:
                break
    
    def _iniciar_executor_loja(self, loja):
        if loja.nome_banco not in self.executores_ativos:
            executor = ExecutorConsultasComDiagnostico(loja, self.modo_alta_carga)
            self.executores_ativos[loja.nome_banco] = executor
            executor.iniciar_execucao()
            
            # Verifica se a execução foi bem-sucedida
            time.sleep(0.5)  # Aguarda um pouco para verificar o status
            stats = executor.obter_estatisticas()
            if stats and stats.get('conexao_ativa'):
                self.logger.debug(f"✅ Executor iniciado com sucesso para loja {loja.nome_banco} no IP {self.ip_porta}")
            else:
                self.logger.warning(f"⚠️ Executor iniciado mas sem conexão ativa para loja {loja.nome_banco}")
    
    def _remover_executores_finalizados(self):
        lojas_finalizadas = []
        
        for nome_loja, executor in self.executores_ativos.items():
            if not executor.executando:
                lojas_finalizadas.append(nome_loja)
        
        for nome_loja in lojas_finalizadas:
            if nome_loja in self.executores_ativos:
                self.executores_ativos[nome_loja].parar_execucao()
                del self.executores_ativos[nome_loja]
                self.gerenciador_fila.liberar_loja(self.ip_porta, nome_loja)
                self.logger.debug(f"Executor removido para loja {nome_loja} no IP {self.ip_porta}")
    
    def obter_estatisticas(self):
        if not self.executando:
            return None
        
        stats_lojas = {}
        total_consultas = 0
        total_erros = 0
        total_threads_ativas = 0
        total_threads = 0
        conexoes_ativas = 0
        
        for nome_loja, executor in self.executores_ativos.items():
            stats = executor.obter_estatisticas()
            if stats:
                stats_lojas[nome_loja] = stats
                total_consultas += stats['total_consultas']
                total_erros += stats['total_erros']
                total_threads_ativas += stats['threads_ativas']
                total_threads += stats['threads_total']
                
                if stats.get('conexao_ativa'):
                    conexoes_ativas += 1
        
        status_fila = self.gerenciador_fila.obter_status_filas().get(self.ip_porta, {})
        
        return {
            'ip_porta': self.ip_porta,
            'lojas_ativas': stats_lojas,
            'total_lojas_ativas': len(self.executores_ativos),
            'total_consultas': total_consultas,
            'total_erros': total_erros,
            'threads_ativas': total_threads_ativas,
            'threads_total': total_threads,
            'conexoes_ativas': conexoes_ativas,
            'fila_aguardando': status_fila.get('fila_aguardando', 0),
            'lojas_processadas': status_fila.get('processadas', 0),
            'limite_maximo': ConfiguracaoExecucao.MAX_CONSULTAS_POR_IP
        }