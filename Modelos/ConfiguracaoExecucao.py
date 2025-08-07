class ConfiguracaoExecucao:
    MAX_CONSULTAS_POR_IP = 8
    THREADS_POR_LOJA_NORMAL = 5
    THREADS_POR_LOJA_ALTA_CARGA = 10
    INTERVALO_ENTRE_CONSULTAS = 0.02
    INTERVALO_VERIFICACAO_FILA = 2.0
    TIMEOUT_CONEXAO = 30
    TENTATIVAS_RECONEXAO = 3
    INTERVALO_RECONEXAO = 5

    @staticmethod
    def obter_configuracao_alta_carga():
        return {
            'threads_por_loja': ConfiguracaoExecucao.THREADS_POR_LOJA_ALTA_CARGA,
            'intervalo_consultas': 0.005,
            'intervalo_verificacao': 1.0
        }

    @staticmethod
    def obter_configuracao_normal():
        return {
            'threads_por_loja': ConfiguracaoExecucao.THREADS_POR_LOJA_NORMAL,
            'intervalo_consultas': ConfiguracaoExecucao.INTERVALO_ENTRE_CONSULTAS,
            'intervalo_verificacao': ConfiguracaoExecucao.INTERVALO_VERIFICACAO_FILA
        }