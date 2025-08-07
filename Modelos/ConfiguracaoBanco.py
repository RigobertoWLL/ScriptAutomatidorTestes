class ConfiguracaoBanco:
    def __init__(self, ip, porta, nome_banco):
        self.ip = ip
        self.porta = porta
        self.nome_banco = nome_banco

    def obter_string_conexao(self):
        return f"{self.ip}:{self.porta}/{self.nome_banco}"

    def __str__(self):
        return f"{self.ip}:{self.porta}:{self.nome_banco}"