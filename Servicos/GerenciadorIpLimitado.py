import threading
import logging
from Servicos.ExecutorConsultaRotativa import ExecutorConsultaRotativa
from Modelos.ConsultasSql import ConsultasSql
from Modelos.ConfiguracaoExecucao import ConfiguracaoExecucao


class GerenciadorIpLimitado:
    def __init__(self, ip_porta, gerenciador_rotacao, modo_alta_carga=False):
        self.ip_porta = ip_porta
        self.gerenciador_rotacao = gerenciador_rotacao
        self.modo_alta_carga = modo_alta_carga
        self.executores_consultas = []
        self.executando = False
        self.logger = logging.getLogger(f'SimuladorCarga.GerenciadorIpLimitado.{ip_porta}')

        self.config = ConfiguracaoExecucao.obter_configuracao_alta_carga() if modo_alta_carga else ConfiguracaoExecucao.obter_configuracao_normal()
        self.max_consultas = self.config['max_consultas_por_ip']

    def iniciar_execucao(self):
        if not self.executando:
            self.executando = True
            self.executores_consultas = []

            consultas_com_nome = ConsultasSql.obter_consultas_com_nome()

            contador_thread = 0
            for nome_consulta, sql_consulta in consultas_com_nome.items():
                if contador_thread >= self.max_consultas:
                    break

                executor = ExecutorConsultaRotativa(
                    self.ip_porta,
                    self.gerenciador_rotacao,
                    nome_consulta,
                    sql_consulta,
                    contador_thread,
                    self.config['intervalo_consultas']
                )
                self.executores_consultas.append(executor)
                executor.iniciar_execucao()
                contador_thread += 1

            self.logger.info(
                f"IP {self.ip_porta} iniciado com {len(self.executores_consultas)}/{self.max_consultas} consultas simultâneas")
            self.logger.info(f"  Consultas ativas: {[exec.nome_consulta for exec in self.executores_consultas]}")

    def parar_execucao(self):
        if self.executando:
            self.executando = False
            self.logger.info(f"Parando IP {self.ip_porta}")

            for executor in self.executores_consultas:
                executor.parar_execucao()

            self._log_estatisticas_finais()
            self.executores_consultas = []

    def _log_estatisticas_finais(self):
        total_consultas = 0
        total_erros = 0
        total_rotacoes = 0

        for executor in self.executores_consultas:
            stats = executor.obter_estatisticas()
            total_consultas += stats['consultas_executadas']
            total_erros += stats['erros']
            total_rotacoes += stats['rotacoes']

        self.logger.info(f"Estatísticas finais IP {self.ip_porta}:")
        self.logger.info(f"  Total consultas: {total_consultas}")
        self.logger.info(f"  Total erros: {total_erros}")
        self.logger.info(f"  Total rotações: {total_rotacoes}")

    def obter_estatisticas(self):
        if not self.executando:
            return None

        stats_por_consulta = {}
        total_consultas = 0
        total_erros = 0
        total_rotacoes = 0
        executores_ativos = 0

        for executor in self.executores_consultas:
            stats = executor.obter_estatisticas()
            nome_consulta = executor.nome_consulta

            if nome_consulta not in stats_por_consulta:
                stats_por_consulta[nome_consulta] = {
                    'consultas': 0,
                    'erros': 0,
                    'rotacoes': 0,
                    'lojas_atuais': [],
                    'executores_ativos': 0
                }

            stats_por_consulta[nome_consulta]['consultas'] += stats['consultas_executadas']
            stats_por_consulta[nome_consulta]['erros'] += stats['erros']
            stats_por_consulta[nome_consulta]['rotacoes'] += stats['rotacoes']

            if stats['loja_atual']:
                stats_por_consulta[nome_consulta]['lojas_atuais'].append(stats['loja_atual'])

            if stats['ativo']:
                stats_por_consulta[nome_consulta]['executores_ativos'] += 1
                executores_ativos += 1

            total_consultas += stats['consultas_executadas']
            total_erros += stats['erros']
            total_rotacoes += stats['rotacoes']

        return {
            'ip_porta': self.ip_porta,
            'consultas_por_tipo': stats_por_consulta,
            'total_consultas': total_consultas,
            'total_erros': total_erros,
            'total_rotacoes': total_rotacoes,
            'executores_ativos': executores_ativos,
            'executores_total': len(self.executores_consultas),
            'limite_consultas': self.max_consultas
        }