class ConfiguracaoExecucao:
    MAX_CONSULTAS_POR_IP = 3
    THREADS_POR_LOJA_NORMAL = 3
    THREADS_POR_LOJA_ALTA_CARGA = 5
    INTERVALO_ENTRE_CONSULTAS = 0.02
    INTERVALO_VERIFICACAO_FILA = 2.0
    TIMEOUT_CONEXAO = 30
    TENTATIVAS_RECONEXAO = 3
    INTERVALO_RECONEXAO = 5
    
    @staticmethod
    def obter_configuracao_alta_carga():
        return {
            'threads_por_loja': ConfiguracaoExecucao.THREADS_POR_LOJA_ALTA_CARGA,
            'intervalo_consultas': 0.02,
            'intervalo_verificacao': 2.0
        }
    
    @staticmethod
    def obter_configuracao_normal():
        return {
            'threads_por_loja': ConfiguracaoExecucao.THREADS_POR_LOJA_NORMAL,
            'intervalo_consultas': ConfiguracaoExecucao.INTERVALO_ENTRE_CONSULTAS,
            'intervalo_verificacao': ConfiguracaoExecucao.INTERVALO_VERIFICACAO_FILA
        }