import threading
import logging
from Servicos.LeitorArquivoIni import LeitorArquivoIni
from Servicos.ExecutorLojaComDiagnostico import ExecutorLojaComDiagnostico
from Servicos.DiagnosticoConexao import DiagnosticoConexao
from Modelos.GerenciadorFilaLojas import GerenciadorFilaLojas
from Modelos.ConfiguracaoExecucao import ConfiguracaoExecucao

class GerenciadorCargaComDiagnostico:
    def __init__(self, caminho_arquivo_ini):
        self.caminho_arquivo = caminho_arquivo_ini
        self.executores_ip = []
        self.gerenciador_fila = GerenciadorFilaLojas()
        self.diagnostico = DiagnosticoConexao()
        self.executando = False
        self.modo_alta_carga = False
        self.ips_unicos = set()
        self.logger = logging.getLogger('SimuladorCarga.GerenciadorCargaComDiagnostico')
    
    def iniciar_simulacao_carga(self, modo_alta_carga=False):
        if self.executando:
            self.logger.warning("Tentativa de iniciar simulação já em execução")
            return
        
        self.modo_alta_carga = modo_alta_carga
        modo_texto = "ALTA CARGA" if modo_alta_carga else "NORMAL"
        self.logger.info(f"Iniciando simulação com diagnóstico - Modo: {modo_texto}")
        
        leitor = LeitorArquivoIni(self.caminho_arquivo)
        configuracoes = leitor.carregar_configuracoes()
        
        if not configuracoes:
            self.logger.error("Nenhuma configuração válida encontrada")
            return
        
        # Diagnóstico inicial
        self.logger.info("Executando diagnóstico inicial de conectividade...")
        resultados_diagnostico = self.diagnostico.diagnosticar_ips_problematicos(configuracoes, 10)
        
        self.logger.info("=" * 80)
        self.logger.info("RESULTADO DO DIAGNÓSTICO:")
        for ip_porta, resultado in resultados_diagnostico.items():
            status = "✅ OK" if resultado['sucesso'] else "❌ FALHA"
            self.logger.info(f"  {ip_porta}: {status} - {resultado['mensagem']}")
        self.logger.info("=" * 80)
        
        self.gerenciador_fila.inicializar_filas(configuracoes)
        
        self.ips_unicos = set()
        for config in configuracoes:
            ip_porta = f"{config.ip}:{config.porta}"
            self.ips_unicos.add(ip_porta)
        
        self.executores_ip = []
        
        for ip_porta in self.ips_unicos:
            executor_ip = ExecutorLojaComDiagnostico(ip_porta, self.gerenciador_fila, modo_alta_carga)
            self.executores_ip.append(executor_ip)
            executor_ip.iniciar_execucao()
        
        self.executando = True
        self.logger.info("Simulação com diagnóstico iniciada")
    
    def parar_simulacao_carga(self):
        if not self.executando:
            self.logger.warning("Tentativa de parar simulação que não está em execução")
            return
        
        self.logger.info("Parando simulação com diagnóstico")
        
        for executor_ip in self.executores_ip:
            executor_ip.parar_execucao()
        
        self.executores_ip = []
        self.executando = False
        self.logger.info("Simulação com diagnóstico parada")
    
    def obter_status_execucao(self):
        return self.executando
    
    def obter_estatisticas_completas(self):
        if not self.executando:
            return None
        
        estatisticas_por_ip = {}
        total_geral_consultas = 0
        total_geral_erros = 0
        total_geral_threads_ativas = 0
        total_geral_threads = 0
        total_lojas_ativas = 0
        total_fila_aguardando = 0
        total_conexoes_ativas = 0
        ips_ativos = 0
        
        for executor_ip in self.executores_ip:
            stats = executor_ip.obter_estatisticas()
            if stats:
                ip_porta = stats['ip_porta']
                estatisticas_por_ip[ip_porta] = stats
                total_geral_consultas += stats['total_consultas']
                total_geral_erros += stats['total_erros']
                total_geral_threads_ativas += stats['threads_ativas']
                total_geral_threads += stats['threads_total']
                total_lojas_ativas += stats['total_lojas_ativas']
                total_fila_aguardando += stats['fila_aguardando']
                total_conexoes_ativas += stats['conexoes_ativas']
                
                if stats['total_lojas_ativas'] > 0:
                    ips_ativos += 1
        
        estatisticas_por_ip['TOTAIS_GERAIS'] = {
            'total_consultas': total_geral_consultas,
            'total_erros': total_geral_erros,
            'threads_ativas': total_geral_threads_ativas,
            'threads_total': total_geral_threads,
            'ips_únicos': len(self.ips_unicos),
            'ips_ativos': ips_ativos,
            'lojas_ativas_total': total_lojas_ativas,
            'lojas_na_fila': total_fila_aguardando,
            'conexoes_ativas_total': total_conexoes_ativas,
            'limite_por_ip': ConfiguracaoExecucao.MAX_CONSULTAS_POR_IP,
            'modo_alta_carga': self.modo_alta_carga
        }
        
        return estatisticas_por_ip
    
    def obter_resumo_ips(self):
        if not self.executando:
            return None
        
        resumo = []
        for executor_ip in self.executores_ip:
            stats = executor_ip.obter_estatisticas()
            if stats:
                resumo.append({
                    'ip_porta': stats['ip_porta'],
                    'lojas_ativas': stats['total_lojas_ativas'],
                    'lojas_fila': stats['fila_aguardando'],
                    'consultas': stats['total_consultas'],
                    'threads_ativas': stats['threads_ativas'],
                    'conexoes_ativas': stats['conexoes_ativas'],
                    'limite_maximo': stats['limite_maximo'],
                    'percentual_uso': (stats['total_lojas_ativas'] / stats['limite_maximo'] * 100) if stats['limite_maximo'] > 0 else 0
                })
        
        return sorted(resumo, key=lambda x: x['consultas'], reverse=True)