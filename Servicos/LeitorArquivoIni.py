import logging
from Modelos.ConfiguracaoBanco import ConfiguracaoBanco

class LeitorArquivoIni:
    def __init__(self, caminho_arquivo):
        self.caminho_arquivo = caminho_arquivo
        self.logger = logging.getLogger('SimuladorCarga.LeitorArquivoIni')
    
    def carregar_configuracoes(self):
        configuracoes = []
        try:
            self.logger.info(f"Iniciando leitura do arquivo: {self.caminho_arquivo}")
            with open(self.caminho_arquivo, 'r') as arquivo:
                for linha_numero, linha in enumerate(arquivo, 1):
                    linha = linha.strip()
                    if linha and not linha.startswith('#'):
                        try:
                            if ':' in linha:
                                partes = linha.split(':')
                                if len(partes) >= 2:
                                    if len(partes) == 2:
                                        ip, nome_banco = partes[0], partes[1]
                                        porta = '3050'
                                    else:
                                        ip, porta, nome_banco = partes[0], partes[1], partes[2]
                                    
                                    config = ConfiguracaoBanco(ip, porta, nome_banco)
                                    configuracoes.append(config)
                                    self.logger.debug(f"Configuração carregada linha {linha_numero}: {config}")
                                else:
                                    self.logger.warning(f"Formato inválido na linha {linha_numero}: {linha}")
                            else:
                                self.logger.warning(f"Formato inválido na linha {linha_numero}: {linha}")
                        except Exception as e:
                            self.logger.error(f"Erro ao processar linha {linha_numero}: {linha} - {e}")
            
            self.logger.info(f"Total de configurações carregadas: {len(configuracoes)}")
            return configuracoes
            
        except FileNotFoundError:
            self.logger.error(f"Arquivo não encontrado: {self.caminho_arquivo}")
            return []
        except Exception as e:
            self.logger.error(f"Erro ao carregar configurações: {e}")
            return []