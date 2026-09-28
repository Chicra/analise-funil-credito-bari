
import json
import re
from pathlib import Path


MAPA_TIPO_IMOVEL = [
    (r"apartamento", "Apartamento"),
    (r"casa geminada", "Casa"),
    (r"casa t[ée]rrea", "Casa"),
    (r"casa residencial", "Casa"),
    (r"\bcasa\b", "Casa"),
    (r"sala comercial", "Sala comercial"),
    (r"loja t[ée]rrea", "Loja"),
    (r"unidade comercial", "Unidade comercial"),
    (r"gal[pã][ão]o industrial", "Galpão industrial"),
    (r"im[óo]vel rural", "Imóvel rural"),
    (r"s[íi]tio", "Imóvel rural"),
    (r"terreno urbano", "Terreno"),
    (r"terreno para incorpora[çc][ãa]o", "Terreno"),
    (r"\bterreno\b", "Terreno"),
]


def extrair_tipo_imovel(texto: str):
    texto_lower = texto.lower()
    for padrao, tipo_normalizado in MAPA_TIPO_IMOVEL:
        if re.search(padrao, texto_lower):
            return tipo_normalizado
    return None


PADROES_ENDERECO = [
    r"Endere[çc]o(?: do im[óo]vel)?:\s*(.+)",
    r"Localiza[çc][ãa]o do bem:\s*(.+)",
    r"Local:\s*(.+)",
    r"(?:situad[oa]|localizad[oa])\s+(?:n[oa]|à)\s*(.+?)\.(?!\d)",
]

UFS = ("AC|AL|AP|AM|BA|CE|DF|ES|GO|MA|MT|MS|MG|PA|PB|PR|PE|PI|RJ|RN|RS|"
       "RO|RR|SC|SP|SE|TO")

# fallback genérico: primeira sentença "de localização" que contenha um
# código de UF válido como palavra isolada — evita linhas de credencial
# (CREA/CAU) que também têm sigla de estado.
PADRAO_UF_NA_SENTENCA = re.compile(rf"\b(?:{UFS})\b")


def extrair_endereco(texto: str):
    for padrao in PADROES_ENDERECO:
        m = re.search(padrao, texto, re.IGNORECASE)
        if m:
            return m.group(1).strip().rstrip(".")

    padrao_split = r"(?<!\bap)(?<!\bAv)(?<!\bArq)(?<!\bEng)\.(?!\d)\s*"
    for sentenca in re.split(padrao_split, texto):
        sentenca_limpa = sentenca.strip()
        if not sentenca_limpa:
            continue
        if re.search(r"CREA|CAU|CNAI|respons[áa]vel", sentenca_limpa, re.IGNORECASE):
            continue  # linha de assinatura/credencial, não é endereço
        if PADRAO_UF_NA_SENTENCA.search(sentenca_limpa):

            linhas = sentenca_limpa.split("\n")
            if len(linhas) > 1 and linhas[0] == linhas[0].upper() and not re.search(r"[a-zà-ú]", linhas[0]):
                sentenca_limpa = "\n".join(linhas[1:]).strip()
            return sentenca_limpa.rstrip(".").strip()
    return None


PADRAO_AREA = re.compile(
    r"([ÁA]rea[\w\sá-ú]{0,25}?|Superf[íi]cie|lote(?:\s+de)?|terreno(?:\s+com)?"
    r"|benfeitorias[\w\sá-ú]{0,20}?)\s*[:\s]{1,3}"
    r"([\d\.]+(?:,\d+)?)\s*(m[²2]|ha)",
    re.IGNORECASE,
)


PADRAO_AREA_INVERSA = re.compile(
    r"([\d\.]+(?:,\d+)?)\s*(m[²2]|ha)\s+de\s+(área[\w\sá-ú]{0,20}?)(?=[,.;])",
    re.IGNORECASE,
)


PADRAO_AREA_TABELA = re.compile(
    r"tabela[^.]{0,20}?registra\s+([\d\.]+(?:,\d+)?)\s*(m[²2]|ha)", re.IGNORECASE
)


def extrair_areas(texto: str):
    achados = []
    for m in PADRAO_AREA.finditer(texto):
        rotulo = re.sub(r"\s+", " ", m.group(1)).strip().lower()
        valor = m.group(2)
        unidade = m.group(3).lower().replace("2", "²")
        achados.append({"rotulo": rotulo, "valor": valor, "unidade": unidade})

    for m in PADRAO_AREA_INVERSA.finditer(texto):
        achados.append({
            "rotulo": m.group(3).strip().lower(),
            "valor": m.group(1),
            "unidade": m.group(2).lower().replace("2", "²"),
        })


    m = PADRAO_AREA_TABELA.search(texto)
    if m:
        achados.append({
            "rotulo": "área total (tabela interna)",
            "valor": m.group(1),
            "unidade": m.group(2).lower().replace("2", "²"),
        })
    return achados


def detectar_conflito_area(texto: str, areas: list):

    totais = [a for a in areas if "total" in a["rotulo"]]
    valores_distintos = {a["valor"] for a in totais}
    if len(valores_distintos) > 1:
        return f"CONFLITO em 'área total': valores distintos encontrados {sorted(valores_distintos)}"
    return None


PADROES_ANO_EXPLICITO = [
    r"[Aa]no de constru[çc][ãa]o(?: informado[a]? pel[oa] propriet[áa]rio)?:\s*(\d{4})",
    r"[Cc]onstru[íi]da em (\d{4})",
    r"[Cc]onstru[íi]do em (\d{4})",
    r"[Cc]onstru[çc][ãa]o:\s*(\d{4})",
    r"[Aa]no das edifica[çc][õo]es:\s*(\d{4})",
    r"[Aa]no de conclus[ãa]o\s*(\d{4})",
    r"[Aa]no informado:\s*(\d{4})",
    r"com (\d{4}) de constru[çc][ãa]o",
    r"\bAno:?\s+(\d{4})\b",  
]

PADRAO_ANO_NAO_APLICA = r"[Aa]no[:\s]*n[ãa]o se aplica|[Aa]no de constru[çc][ãa]o:\s*inexistente"

PADRAO_IDADE_APARENTE = r"[Ii]dade aparente:\s*(\d+)\s*anos|[Ii]dade:\s*aproximadamente\s*(\d+)\s*anos"


def extrair_ano_construcao(texto: str):
    if re.search(PADRAO_ANO_NAO_APLICA, texto):
        return {"valor": None, "observacao": "Não se aplica (terreno sem edificação)"}
    for padrao in PADROES_ANO_EXPLICITO:
        m = re.search(padrao, texto)
        if m:
            return {"valor": int(m.group(1)), "observacao": None}
    m = re.search(PADRAO_IDADE_APARENTE, texto)
    if m:
        idade = m.group(1) or m.group(2)
        return {
            "valor": None,
            "observacao": (f"Ano não declarado explicitamente; documento menciona "
                           f"apenas idade aparente de {idade} anos"),
        }
    return {"valor": None, "observacao": "Campo não encontrado no documento"}



PADRAO_VALOR = re.compile(r"R\$\s*([\d\.]+(?:,\d{2})?)")


def extrair_valor_avaliacao(texto: str):
    valores = PADRAO_VALOR.findall(texto)
    if not valores:
        return {"valor": None, "observacao": "Nenhum valor em R$ encontrado no documento"}
    valores_unicos = set(valores)
    if len(valores_unicos) > 1:
        return {
            "valor": "CONFLITO",
            "observacao": f"Mais de um valor em R$ encontrado no texto: {sorted(valores_unicos)}",
        }
    valor_str = valores[0].replace(".", "").replace(",", ".")
    return {"valor": float(valor_str), "observacao": None}



PADROES_MATRICULA = [
    r"[Mm]atr[íi]cula\s*n?[ºo°]?\s*[:\s]*(\d+(?:\.\d+)*)",
    r"[Rr]egistro imobili[áa]rio\s*n?[ºo°]?\s*(\d+(?:\.\d+)*)",
    r"[Rr]egistro:\s*matr[íi]cula\s*(\d+(?:\.\d+)*)",
]

PADRAO_MATRICULA_AUSENTE = r"[Mm]atr[íi]cula n[ãa]o apresentada"


def extrair_matricula(texto: str):
    if re.search(PADRAO_MATRICULA_AUSENTE, texto):
        return {"valor": None,
                "observacao": "Documento declara explicitamente que a matrícula não foi apresentada"}
    for padrao in PADROES_MATRICULA:
        m = re.search(padrao, texto)
        if m:
            return {"valor": m.group(1), "observacao": None}
    return {"valor": None, "observacao": "Campo não encontrado no documento"}



PALAVRAS_ONUS_PRESENTE = [
    ("alienação fiduciária", r"aliena[çc][ãa]o fiduci[áa]ria"),
    ("penhora", r"penhora(?!\s+cancelada)"),
    ("penhora cancelada", r"penhora cancelada"),
    ("hipoteca", r"hipoteca(?!\s*(?:não|nao))"),
    ("servidão de passagem", r"servid[ãa]o de passagem"),
    ("reserva legal", r"reserva legal"),
]

PALAVRAS_ONUS_AUSENTE = [
    r"n[ãa]o foram identificados [oô]nus",
    r"sem gravames conhecidos",
    r"n[ãa]o consta informa[çc][ãa]o sobre [oô]nus",
    r"inexist[êe]ncia de [oô]nus",
    r"n[ãa]o h[áa] men[çc][ãa]o a [oô]nus",
    r"n[ãa]o h[áa] [oô]nus, segundo declara[çc][ãa]o",
]

PALAVRAS_ONUS_NAO_VERIFICAVEL = [
    r"n[ãa]o foi poss[íi]vel verificar",
    r"nada informado",
    r"[oô]nus reais n[ãa]o informados",
    r"sem informa[çc][ãa]o",
]


def extrair_onus(texto: str):
    for nome, padrao in PALAVRAS_ONUS_PRESENTE:
        m = re.search(padrao, texto, re.IGNORECASE)
        if m:
            # pega a frase inteira que contém o termo, para dar contexto
            inicio = texto.rfind(".", 0, m.start()) + 1
            fim = texto.find(".", m.end())
            fim = fim if fim != -1 else len(texto)
            frase = texto[inicio:fim].strip()
            return {"status": "ÔNUS IDENTIFICADO", "tipo": nome, "texto": frase}

    for padrao in PALAVRAS_ONUS_AUSENTE:
        if re.search(padrao, texto, re.IGNORECASE):
            return {"status": "NENHUM IDENTIFICADO", "tipo": None, "texto": None}

    for padrao in PALAVRAS_ONUS_NAO_VERIFICAVEL:
        if re.search(padrao, texto, re.IGNORECASE):
            return {"status": "NÃO INFORMADO / NÃO VERIFICÁVEL", "tipo": None, "texto": None}

    return {"status": "NÃO INFORMADO / NÃO VERIFICÁVEL", "tipo": None,
            "texto": "Nenhum padrão conhecido de ônus encontrado no texto — revisão manual recomendada"}



MESES = {
    "janeiro": "01", "fevereiro": "02", "março": "03", "marco": "03", "abril": "04",
    "maio": "05", "junho": "06", "julho": "07", "agosto": "08", "setembro": "09",
    "outubro": "10", "novembro": "11", "dezembro": "12",
}

PADROES_DATA_VISTORIA = [
    r"[Vv]istoria (?:realizada |efetuada )?em\s*(\d{2}[/-]\d{2}[/-]\d{4})",
    r"[Dd]ata da (?:vistoria|inspe[çc][ãa]o|visita t[ée]cnica)\s*:?\s*(\d{2}[/-]\d{2}[/-]\d{4})",
    r"[Ii]nspe[çc][ãa]o(?: presencial)?\s*(?:em|:)\s*(\d{2}[/-]\d{2}[/-]\d{4})",
    r"[Vv]istoria:?\s*(\d{2}[/-]\d{2}[/-]\d{4})",
    r"[Dd]ata do levantamento:\s*(\d{2}[/-]\d{2}[/-]\d{4})",
]

PADRAO_DATA_EXTENSO = r"[Ee]m (\d{1,2}) de (\w+) de (\d{4})"


def extrair_data_vistoria(texto: str):
    for padrao in PADROES_DATA_VISTORIA:
        m = re.search(padrao, texto)
        if m:
            return m.group(1).replace("-", "/")
    m = re.search(PADRAO_DATA_EXTENSO, texto)
    if m:
        dia, mes_nome, ano = m.groups()
        mes = MESES.get(mes_nome.lower())
        if mes:
            return f"{int(dia):02d}/{mes}/{ano}"
    return None


PADROES_RESPONSAVEL = [
    r"Respons[áa]vel t[ée]cnico:\s*(.+)",
    r"Respons[áa]vel pelo trabalho:\s*(.+)",
    r"Respons[áa]vel:\s*(.+)",
    r"Avaliadora respons[áa]vel:\s*(.+)",
    r"Avaliador:\s*(.+)",
    r"Avaliadora:\s*(.+)",
    r"Perito avaliador:\s*(.+)",
    r"Perita:\s*(.+)",
    r"Elaborado por:\s*(.+)",
    r"RT:\s*(.+)",
]


def extrair_responsavel_tecnico(texto: str):
    for padrao in PADROES_RESPONSAVEL:
        m = re.search(padrao, texto)
        if m:
            return m.group(1).strip().rstrip(".")
    return None



def extrair_laudo(caminho: Path) -> dict:
    texto = caminho.read_text(encoding="utf-8")
    alertas = []

    tipo_imovel = extrair_tipo_imovel(texto)
    if tipo_imovel is None:
        alertas.append("tipo_imovel não identificado por nenhum padrão conhecido")

    endereco = extrair_endereco(texto)
    if endereco is None:
        alertas.append("endereco não identificado por nenhum padrão conhecido")

    areas = extrair_areas(texto)
    conflito_area = detectar_conflito_area(texto, areas)
    if conflito_area:
        alertas.append(conflito_area)

    ano = extrair_ano_construcao(texto)
    if ano["observacao"]:
        alertas.append(f"ano_construcao: {ano['observacao']}")

    valor = extrair_valor_avaliacao(texto)
    if valor["observacao"]:
        alertas.append(f"valor_avaliacao: {valor['observacao']}")

    matricula = extrair_matricula(texto)
    if matricula["observacao"]:
        alertas.append(f"matricula: {matricula['observacao']}")

    onus = extrair_onus(texto)

    data_vistoria = extrair_data_vistoria(texto)
    if data_vistoria is None:
        alertas.append("data_vistoria não identificada por nenhum padrão conhecido")

    responsavel = extrair_responsavel_tecnico(texto)
    if responsavel is None:
        alertas.append("responsavel_tecnico não identificado por nenhum padrão conhecido")

    return {
        "arquivo": caminho.name,
        "tipo_imovel": tipo_imovel,
        "endereco": endereco,
        "areas": areas,
        "ano_construcao": ano["valor"],
        "valor_avaliacao": valor["valor"],
        "matricula": matricula["valor"],
        "onus_status": onus["status"],
        "onus_tipo": onus["tipo"],
        "onus_texto": onus["texto"],
        "data_vistoria": data_vistoria,
        "responsavel_tecnico": responsavel,
        "alertas": alertas,
    }


def main():
    pasta_laudos = Path("laudos_avaliacao")
    saida = []
    for caminho in sorted(pasta_laudos.glob("*.txt")):
        saida.append(extrair_laudo(caminho))

    Path("saidas").mkdir(exist_ok=True)
    with open("saidas/laudos_extraidos.json", "w", encoding="utf-8") as f:
        json.dump(saida, f, ensure_ascii=False, indent=2)

    print(f"Extraídos {len(saida)} laudos -> saidas/laudos_extraidos.json")
    total_alertas = sum(len(laudo["alertas"]) for laudo in saida)
    print(f"Total de alertas/campos não resolvidos automaticamente: {total_alertas}")


if __name__ == "__main__":
    main()
