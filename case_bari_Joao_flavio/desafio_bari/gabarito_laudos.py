
GABARITO = {
    "laudo_01.txt": {
        "tipo_imovel": "Apartamento", "ano_construcao": 2014,
        "valor_avaliacao": 642000.00, "matricula": "184.772",
        "onus_status": "NENHUM IDENTIFICADO", "data_vistoria": "12/03/2025",
    },
    "laudo_02.txt": {
        "tipo_imovel": "Casa", "ano_construcao": 2008,
        "valor_avaliacao": 680000.00, "matricula": "45.981",
        "onus_status": "NENHUM IDENTIFICADO", "data_vistoria": "18/03/2025",
    },
    "laudo_03.txt": {
        "tipo_imovel": "Sala comercial", "ano_construcao": None,  # só idade aparente (11 anos)
        "valor_avaliacao": 395500.00, "matricula": "77.201",
        "onus_status": "ÔNUS IDENTIFICADO", "data_vistoria": "22/03/2025",
    },
    "laudo_04.txt": {
        "tipo_imovel": "Terreno", "ano_construcao": None,  # não se aplica
        "valor_avaliacao": 218000.00, "matricula": "102.334",
        "onus_status": "NÃO INFORMADO / NÃO VERIFICÁVEL", "data_vistoria": "02/04/2025",
    },
    "laudo_05.txt": {
        "tipo_imovel": "Imóvel rural", "ano_construcao": 1999,
        "valor_avaliacao": 1275000.00, "matricula": "32.110",
        "onus_status": "ÔNUS IDENTIFICADO", "data_vistoria": "07/04/2025",  # reserva legal
    },
    "laudo_06.txt": {
        "tipo_imovel": "Apartamento", "ano_construcao": 2018,
        "valor_avaliacao": 455000.00, "matricula": "9.876",
        "onus_status": "NENHUM IDENTIFICADO", "data_vistoria": "15/04/2025",
    },
    "laudo_07.txt": {
        "tipo_imovel": "Casa", "ano_construcao": 2011,
        "valor_avaliacao": 372000.00, "matricula": "66.504",
        "onus_status": "ÔNUS IDENTIFICADO", "data_vistoria": "20/04/2025",  # penhora
    },
    "laudo_08.txt": {
        "tipo_imovel": "Loja", "ano_construcao": None,  # só "ano de referência" (ambíguo)
        "valor_avaliacao": 910000.00, "matricula": None,  # não apresentada
        "onus_status": "NÃO INFORMADO / NÃO VERIFICÁVEL", "data_vistoria": "29/04/2025",
    },
    "laudo_09.txt": {
        "tipo_imovel": "Casa", "ano_construcao": 2020,
        "valor_avaliacao": 1080000.00, "matricula": "12.909",
        "onus_status": "NENHUM IDENTIFICADO", "data_vistoria": "03/05/2025",
    },
    "laudo_10.txt": {
        "tipo_imovel": "Apartamento", "ano_construcao": 2016,
        "valor_avaliacao": 735000.00, "matricula": "201.443",
        "onus_status": "ÔNUS IDENTIFICADO", "data_vistoria": "09/05/2025",  # alienação fiduciária
    },
    "laudo_11.txt": {
        "tipo_imovel": "Terreno", "ano_construcao": None,  # inexistente
        "valor_avaliacao": 2450000.00, "matricula": "88.710",
        "onus_status": "NÃO INFORMADO / NÃO VERIFICÁVEL", "data_vistoria": "16/05/2025",
    },
    "laudo_12.txt": {
        "tipo_imovel": "Casa", "ano_construcao": 2012,
        "valor_avaliacao": 2180000.00, "matricula": "54.122",
        "onus_status": "ÔNUS IDENTIFICADO", "data_vistoria": "23/05/2025",  # servidão
    },
    "laudo_13.txt": {
        "tipo_imovel": "Apartamento", "ano_construcao": 1987,
        "valor_avaliacao": 1320000.00, "matricula": "145.230",
        "onus_status": "ÔNUS IDENTIFICADO", "data_vistoria": "30/05/2025",  # penhora cancelada, sem data
    },
    "laudo_14.txt": {
        "tipo_imovel": "Galpão industrial", "ano_construcao": None,  # só idade aproximada (18 anos)
        "valor_avaliacao": 3900000.00, "matricula": "70.008",
        "onus_status": "NENHUM IDENTIFICADO", "data_vistoria": "05/06/2025",
    },
    "laudo_15.txt": {
        "tipo_imovel": "Casa", "ano_construcao": 2003,
        "valor_avaliacao": 590000.00, "matricula": "39.240",
        "onus_status": "ÔNUS IDENTIFICADO", "data_vistoria": "12/06/2025",  # hipoteca ativa
    },
    "laudo_16.txt": {
        "tipo_imovel": "Unidade comercial", "ano_construcao": 2010,
        "valor_avaliacao": 288000.00, "matricula": "101.010",
        "onus_status": "NÃO INFORMADO / NÃO VERIFICÁVEL", "data_vistoria": "19/06/2025",
    },
    "laudo_17.txt": {
        "tipo_imovel": "Apartamento", "ano_construcao": 2015,
        "valor_avaliacao": 610000.00, "matricula": "176.543",
        "onus_status": "NENHUM IDENTIFICADO",  # segundo o proprietário, sem certidão anexada
        "data_vistoria": "25/06/2025",
    },
}

GABARITO_EXTRA = {
    "laudo_01.txt": {"areas": {"78,40 m²", "102,10 m²"}, "endereco_contem": "Rua das Acácias, 145",
                     "responsavel_tecnico": "Eng. Marina Albuquerque - CREA-SP 5061234567"},
    "laudo_02.txt": {"areas": {"146,00 m²", "250 m²"}, "endereco_contem": "Av. Central, 900",
                     "responsavel_tecnico": "Carlos Henrique Moura, CAU A123456-7"},
    "laudo_03.txt": {"areas": {"54,8 m²", "18,2 m²"}, "endereco_contem": "Rua do Comércio, 77",
                     "responsavel_tecnico": "Arq. Beatriz Nunes (CAU A987654-3)"},
    "laudo_04.txt": {"areas": {"360 m²"}, "endereco_contem": "Rua Ipê Amarelo",
                     "responsavel_tecnico": "Paulo Sérgio Reis, CREA 12345/D-GO"},
    "laudo_05.txt": {"areas": {"4,8 ha", "310 m²"}, "endereco_contem": "Campinas",
                     "responsavel_tecnico": "João A. Farias, CREA-SP 5076543210"},
    "laudo_06.txt": {"areas": {"61 m²", "84 m²"}, "endereco_contem": "Rua das Palmeiras, 1.210",
                     "responsavel_tecnico": "Fernanda Lins, CREA 18001/PE"},
    "laudo_07.txt": {"areas": {"125,00 m²", "92,50 m²"}, "endereco_contem": "Rua Azul, 33",
                     "responsavel_tecnico": "Eng. Rafael Costa, CREA-RS 222333"},
    "laudo_08.txt": {"areas": {"118 m²"}, "endereco_contem": "Rua Sete de Setembro, 410",
                     "responsavel_tecnico": "Luciana Prado - CNAI 12345"},
    "laudo_09.txt": {"areas": {"420,00 m²", "198,00 m²"}, "endereco_contem": "Alameda das Flores 88",
                     "responsavel_tecnico": "Eng. Thiago Martins, CREA-SC 7654321"},
    "laudo_10.txt": {"areas": {"96,3 m²", "127,6 m²"}, "endereco_contem": "SQN 214",
                     "responsavel_tecnico": "Denise Carvalho, CREA-DF 112233"},
    "laudo_11.txt": {"areas": {"1.020 m²"}, "endereco_contem": "Rua Projetada 4",
                     "responsavel_tecnico": "Marcos Vieira, Eng. Civil, CREA-SP 5099988776"},
    "laudo_12.txt": {"areas": {"285 m²", "600 m²"}, "endereco_contem": "Rua das Bromélias, 500",
                     "responsavel_tecnico": "Arq. Andréa Melo, CAU A445566-1"},
    "laudo_13.txt": {"areas": {"112,00 m²", "155,00 m²"}, "endereco_contem": "Av. Brasil 1770",
                     "responsavel_tecnico": "Eduardo Sampaio, CNAI 67890"},
    "laudo_14.txt": {"areas": {"1.450 m²", "3.000 m²"}, "endereco_contem": "BR-116, km 12",
                     "responsavel_tecnico": "Sérgio Tavares, CREA-MG 998877"},
    "laudo_15.txt": {"areas": {"200 m²", "135 m²"}, "endereco_contem": "Rua Monte Verde, 19",
                     "responsavel_tecnico": "Patrícia Gomes, Eng. Civil, CREA-PR 123123"},
    "laudo_16.txt": {"areas": {"42,00 m²", "67,00 m²"}, "endereco_contem": "Rua do Sol, 250",
                     "responsavel_tecnico": "Guilherme Rocha, CREA-SP 501010"},
    "laudo_17.txt": {"areas": {"70 m²", "95 m²", "92 m²"}, "endereco_contem": "Rua Harmonia, 44",
                     "responsavel_tecnico": "Marina Albuquerque, CREA-SP 5061234567"},
}

LAUDOS_COM_CONFLITO_DE_AREA = {"laudo_17.txt"}
