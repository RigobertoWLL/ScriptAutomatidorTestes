from Modelos.ConfiguracaoBanco import ConfiguracaoBanco

class LeitorArquivoIni:
    def __init__(self, caminho_arquivo):
        self.caminho_arquivo = caminho_arquivo
    
    def carregar_configuracoes(self):
        configuracoes = []
        with open(self.caminho_arquivo, 'r') as arquivo:
            for linha in arquivo:
                linha = linha.strip()
                if linha:
                    ip_porta, nome_banco = linha.split(':')
                    ip, porta = ip_porta.split(':') if ':' in ip_porta else (ip_porta, '3050')
                    configuracoes.append(ConfiguracaoBanco(ip, porta, nome_banco))
        return configuracoes