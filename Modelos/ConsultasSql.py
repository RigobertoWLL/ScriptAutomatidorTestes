class ConsultasSql:
    CONSULTA_SP_GERENCIAL = "SELECT * FROM sp_gerencial_pg1 ('2025-07-01','2025-07-31',0)"
    CONSULTA_SP_DRE = "SELECT * FROM sp_dre (3, '2025-07-01', '2025-07-31', 0)"
    
    @staticmethod
    def obter_todas_consultas():
        return [
            ConsultasSql.CONSULTA_SP_GERENCIAL,
            ConsultasSql.CONSULTA_SP_DRE
        ]