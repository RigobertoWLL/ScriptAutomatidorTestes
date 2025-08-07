import logging
import os
from datetime import datetime


class ConfiguradorLog:
    @staticmethod
    def configurar_log():
        if not os.path.exists('Logs'):
            os.makedirs('Logs')

        data_atual = datetime.now().strftime('%Y-%m-%d')
        nome_arquivo_log = f'Logs/simulador_carga_{data_atual}.log'

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(nome_arquivo_log, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )

        return logging.getLogger('SimuladorCarga')