import threading
import logging
from Servicos.LeitorArquivoIni import LeitorArquivoIni
from Servicos.ExecutorLojaComFila import ExecutorLojaComFila
from Modelos.GerenciadorFilaLojas import GerenciadorFilaLojas
from Modelos.ConfiguracaoExecucao import ConfiguracaoExecucao


class GerenciadorCarga:
    def __init__(self, caminho_arquivo_ini):
        self.caminho_arquivo = caminho_arquivo_ini
        self.executores_ip = []
        self.gerenciador_fila = GerenciadorFilaLojas()
        self.executando = False
        self.modo_alta_carga = False
        self.ips_unicos = set()
        self.logger = logging.getLogger('SimuladorCarga.GerenciadorCarga')

    def iniciar_simulacao_carga(self, modo_alta_carga=False):
        if self.executando:
            self.logger.warning("Tentativa de iniciar simulação já em execução")
            return

        self.modo_alta_carga = modo_alta_carga
        modo_texto = "ALTA CARGA" if modo_alta_carga else "NORMAL"
        self.logger.info(f"Iniciando simulação de carga - Modo: {modo_texto}")

        leitor = LeitorArquivoIni(self.caminho_arquivo)
        configuracoes = leitor.carregar_configuracoes()

        if not configuracoes:
            self.logger.error("Nenhuma configuração válida encontrada")
            return

        self.gerenciador_fila.inicializar_filas(configuracoes)

        self.ips_unicos = set()
        for config in configuracoes:
            ip_porta = f"{config.ip}:{config.porta}"
            self.ips_unicos.add(ip_porta)

        self.executores_ip = []

        self.logger.info("=" * 80)
        self.logger.info("SISTEMA DE CONTROLE DE CARGA POR IP - MÁXIMO 8 CONSULTAS/IP")
        self.logger.info("=" * 80)

        total_lojas = len(configuracoes)
        threads_por_loja = ConfiguracaoExecucao.THREADS_POR_LOJA_ALTA_CARGA if modo_alta_carga else ConfiguracaoExecucao.THREADS_POR_LOJA_NORMAL

        for ip_porta in self.ips_unicos:
            executor_ip = ExecutorLojaComFila(ip_porta, self.gerenciador_fila, modo_alta_carga)
            self.executores_ip.append(executor_ip)
            executor_ip.iniciar_execucao()

        self.logger.info(f"Configuração da simulação:")
        self.logger.info(f"  IPs únicos: {len(self.ips_unicos)}")
        self.logger.info(f"  Total de lojas: {total_lojas}")
        self.logger.info(f"  Máximo consultas por IP: {ConfiguracaoExecucao.MAX_CONSULTAS_POR_IP}")
        self.logger.info(f"  Threads por loja: {threads_por_loja}")
        self.logger.info(f"  Modo: {modo_texto}")
        self.logger.info("=" * 80)

        self.executando = True
        self.logger.info("Simulação iniciada - Sistema de fila ativo para todas as lojas")

    def parar_simulacao_carga(self):
        if not self.executando:
            self.logger.warning("Tentativa de parar simulação que não está em execução")
            return

        self.logger.info("Parando simulação de carga")

        for executor_ip in self.executores_ip:
            executor_ip.parar_execucao()

        self.executores_ip = []
        self.executando = False
        self.logger.info("Simulação de carga parada com sucesso")

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
                    'limite_maximo': stats['limite_maximo'],
                    'percentual_uso': (stats['total_lojas_ativas'] / stats['limite_maximo'] * 100) if stats[
                                                                                                          'limite_maximo'] > 0 else 0
                })

        return sorted(resumo, key=lambda x: x['consultas'], reverse=True)