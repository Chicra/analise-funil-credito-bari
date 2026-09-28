"""RPA - relatório semanal do funil de crédito (Bari).

Fluxo: ler CSV -> validar colunas -> tratar dados -> calcular métricas -> exportar HTML.
Uso:   python rpa_bari.py --entrada propostas_credito.csv
"""
import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
from jinja2 import Environment

COLUNAS_OBRIGATORIAS = {
    "id_proposta", "data_entrada", "canal_origem", "tipo_imovel",
    "valor_imovel", "valor_solicitado", "status_final", "etapa_max_funil",
}
COLUNAS_OPCIONAIS = {
    "cidade", "uf", "prazo_meses", "score_credito", "idade_cliente",
    "renda_mensal_declarada", "flag_cliente_recorrente", "consultor_id",
    "tempo_analise_dias", "data_assinatura_contrato", "taxa_juros_aa",
}
COLUNAS_NUMERICAS = [
    "prazo_meses", "score_credito", "idade_cliente",
    "renda_mensal_declarada", "etapa_max_funil", "tempo_analise_dias",
]
MAPA_CANAL = {
    "mídia paga": "Mídia paga", "organico": "Organico", "indicação": "Indicação",
    "correspondente": "Correspondente", "parceria": "Parceria",
}
LTV_MAXIMO_POLITICA = 0.60
IDADE_MINIMA = 18
ETAPA_MIN, ETAPA_MAX = 1, 6
MESES_EXCLUIDOS_POR_CENSURA = 2  # meses recentes ainda "em andamento"


# ---------------------------------------------------------------- log
def configurar_logger(pasta_logs: Path) -> logging.Logger:
    """Cria um logger que escreve no console e em um arquivo por execução."""
    pasta_logs.mkdir(parents=True, exist_ok=True)
    arquivo_log = pasta_logs / f"execucao_{datetime.now():%Y%m%d_%H%M%S}.log"

    logger = logging.getLogger("rpa_bari")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    formato = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    for handler in (logging.FileHandler(arquivo_log, encoding="utf-8"),
                    logging.StreamHandler(sys.stdout)):
        handler.setFormatter(formato)
        logger.addHandler(handler)
    return logger


# ---------------------------------------------------------------- leitura e schema
def ler_dados(caminho: Path, logger: logging.Logger) -> pd.DataFrame:
    """Lê o CSV tudo como texto, para não deixar o pandas converter tipos em silêncio."""
    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo de entrada não encontrado: {caminho}")
    df = pd.read_csv(caminho, dtype=str)
    logger.info(f"Leitura ok: {len(df)} linhas, {len(df.columns)} colunas de '{caminho.name}'")
    return df


def validar_schema(df: pd.DataFrame, logger: logging.Logger) -> None:
    """Para se faltar coluna obrigatória; apenas avisa sobre opcionais ausentes e colunas novas."""
    presentes = set(df.columns)

    obrigatorias_ausentes = COLUNAS_OBRIGATORIAS - presentes
    if obrigatorias_ausentes:
        raise ValueError(f"Colunas obrigatórias ausentes: {sorted(obrigatorias_ausentes)}")

    opcionais_ausentes = COLUNAS_OPCIONAIS - presentes
    if opcionais_ausentes:
        logger.warning(f"Colunas opcionais ausentes: {sorted(opcionais_ausentes)}")

    desconhecidas = presentes - COLUNAS_OBRIGATORIAS - COLUNAS_OPCIONAIS
    if desconhecidas:
        logger.warning(f"Colunas novas, ignoradas no cálculo: {sorted(desconhecidas)}")


# ---------------------------------------------------------------- tratamento
def _normalizar_valores_monetarios(df: pd.DataFrame, logger: logging.Logger) -> pd.DataFrame:
    com_simbolo = df["valor_imovel"].str.contains("R$", regex=False, na=False).sum()
    df["valor_imovel"] = pd.to_numeric(
        df["valor_imovel"].str.replace("R$", "", regex=False).str.strip(), errors="coerce")
    df["valor_solicitado"] = pd.to_numeric(df["valor_solicitado"], errors="coerce")

    logger.info(f"[tratamento] valor_imovel: removido 'R$' em {com_simbolo} linha(s)")
    invalidos = df[["valor_imovel", "valor_solicitado"]].isna().sum().sum()
    if invalidos:
        logger.warning(f"[tratamento] {invalidos} valor(es) monetário(s) não numérico(s) viraram NaN")
    return df


def _padronizar_canal(df: pd.DataFrame, logger: logging.Logger) -> pd.DataFrame:
    canal_limpo = df["canal_origem"].str.strip()
    canal_padrao = canal_limpo.str.lower().map(MAPA_CANAL).fillna(canal_limpo)
    corrigidas = ((canal_padrao != canal_limpo) & canal_limpo.notna()).sum()

    df["canal_origem"] = canal_padrao
    logger.info(f"[tratamento] canal_origem: {corrigidas} grafia(s) divergente(s) corrigida(s)")
    return df


def _normalizar_datas(df: pd.DataFrame, logger: logging.Logger) -> pd.DataFrame:
    df["data_entrada"] = pd.to_datetime(df["data_entrada"], format="mixed", errors="coerce")
    invalidas = df["data_entrada"].isna().sum()
    if invalidas:
        logger.warning(f"[tratamento] data_entrada: {invalidas} data(s) não reconhecida(s)")
    else:
        logger.info("[tratamento] data_entrada: formatos mistos normalizados")
    return df


def _converter_colunas_numericas(df: pd.DataFrame) -> pd.DataFrame:
    for coluna in COLUNAS_NUMERICAS:
        if coluna in df.columns:
            df[coluna] = pd.to_numeric(df[coluna], errors="coerce")
    return df


def _sinalizar_idade_suspeita(df: pd.DataFrame, logger: logging.Logger) -> pd.DataFrame:
    if "idade_cliente" not in df.columns:
        return df
    df["idade_suspeita"] = df["idade_cliente"] < IDADE_MINIMA
    suspeitas = int(df["idade_suspeita"].sum())
    if suspeitas:
        logger.warning(f"[tratamento] idade_cliente: {suspeitas} linha(s) < {IDADE_MINIMA} anos "
                       "sinalizada(s) e mantida(s) (decisão de negócio a revisar)")
    return df


def _sinalizar_etapa_invalida(df: pd.DataFrame, logger: logging.Logger) -> pd.DataFrame:
    etapa = df["etapa_max_funil"]
    df["etapa_invalida"] = (etapa < ETAPA_MIN) | (etapa > ETAPA_MAX)
    invalidas = int(df["etapa_invalida"].sum())
    if invalidas:
        logger.warning(f"[tratamento] etapa_max_funil: {invalidas} linha(s) fora de "
                       f"{ETAPA_MIN}-{ETAPA_MAX}, excluída(s) só das métricas de funil")
    return df


def _calcular_ltv(df: pd.DataFrame, logger: logging.Logger) -> pd.DataFrame:
    df["ltv"] = df["valor_solicitado"] / df["valor_imovel"]
    logger.info("[tratamento] ltv: coluna citada no dicionário mas ausente no CSV; "
                "calculada como valor_solicitado / valor_imovel")
    return df


def _remover_terrenos(df: pd.DataFrame, logger: logging.Logger) -> pd.DataFrame:
    sem_terreno = df[df["tipo_imovel"] != "Terreno"]
    logger.info(f"[tratamento] tipo_imovel='Terreno': {len(df) - len(sem_terreno)} linha(s) "
                "removida(s) (regra do desafio)")
    return sem_terreno


def tratar_dados(df: pd.DataFrame, logger: logging.Logger) -> pd.DataFrame:
    """Aplica cada correção de qualidade em sequência; cada uma registra o que fez no log."""
    df = df.copy()
    df = _normalizar_valores_monetarios(df, logger)
    df = _padronizar_canal(df, logger)
    df = _normalizar_datas(df, logger)
    df = _converter_colunas_numericas(df)
    df = _sinalizar_idade_suspeita(df, logger)
    df = _sinalizar_etapa_invalida(df, logger)
    df = _calcular_ltv(df, logger)
    df = _remover_terrenos(df, logger)
    logger.info(f"[tratamento] Base final: {len(df)} linhas")
    return df


# ---------------------------------------------------------------- métricas
def _taxa_conversao(df: pd.DataFrame) -> float:
    return (df["status_final"] == "Contratada").mean()


def _perda_valor_por_etapa(df: pd.DataFrame) -> pd.Series:
    perdidas = df[~df["etapa_invalida"] & (df["status_final"] != "Contratada")]
    return perdidas.groupby("etapa_max_funil")["valor_solicitado"].sum().sort_index()


def _conversao_por_canal(df: pd.DataFrame) -> pd.Series:
    contratada = df["status_final"] == "Contratada"
    return contratada.groupby(df["canal_origem"]).mean().sort_values(ascending=False)


def _volume_por_canal(df: pd.DataFrame) -> pd.Series:
    return df["canal_origem"].value_counts()


def _separar_meses(df: pd.DataFrame) -> tuple[list, list]:
    """Divide os meses em completos e excluídos por censura (os mais recentes)."""
    meses = sorted(df["data_entrada"].dt.to_period("M").dropna().unique())
    if len(meses) <= MESES_EXCLUIDOS_POR_CENSURA:
        return meses, []
    return meses[:-MESES_EXCLUIDOS_POR_CENSURA], meses[-MESES_EXCLUIDOS_POR_CENSURA:]


def _conversao_por_mes(df: pd.DataFrame) -> pd.Series:
    meses_completos, _ = _separar_meses(df)
    df = df.assign(mes=df["data_entrada"].dt.to_period("M"))
    df = df[df["mes"].isin(meses_completos)]
    return (df["status_final"] == "Contratada").groupby(df["mes"]).mean()


def _meses_excluidos_por_censura(df: pd.DataFrame) -> list[str]:
    return [str(mes) for mes in _separar_meses(df)[1]]


def _conversao_por_politica_ltv(df: pd.DataFrame) -> dict:
    acima = df["ltv"] > LTV_MAXIMO_POLITICA
    return {
        "qtd_acima": int(acima.sum()),
        "conversao_dentro": _taxa_conversao(df[~acima]),
        "conversao_acima": _taxa_conversao(df[acima]),
    }


def _distribuicao_status(df: pd.DataFrame) -> pd.Series:
    return df["status_final"].value_counts()


METRICAS = {
    "perda_valor_por_etapa": _perda_valor_por_etapa,
    "conversao_por_canal": _conversao_por_canal,
    "volume_por_canal": _volume_por_canal,
    "conversao_por_mes": _conversao_por_mes,
    "meses_excluidos_por_censura": _meses_excluidos_por_censura,
    "ltv_politica": _conversao_por_politica_ltv,
    "distribuicao_status": _distribuicao_status,
}


def calcular_metricas(df: pd.DataFrame, logger: logging.Logger) -> dict:
    """Calcula cada métrica isoladamente: se uma falhar, as outras continuam."""
    metricas = {}
    for nome, funcao in METRICAS.items():
        try:
            metricas[nome] = funcao(df)
        except Exception as erro:
            logger.warning(f"[métrica] '{nome}' não calculada: {erro}")
    logger.info(f"[métrica] {len(metricas)} de {len(METRICAS)} métricas calculadas")
    return metricas


# ---------------------------------------------------------------- relatório
def _fmt_pct(valor) -> str:
    return "—" if pd.isna(valor) else f"{valor * 100:.1f}%"


def _fmt_moeda(valor) -> str:
    inteiro, centavos = f"{valor:,.2f}".split(".")
    return f"R$ {inteiro.replace(',', '.')},{centavos}"


def _fmt_int(valor) -> str:
    return f"{int(valor):,}".replace(",", ".")


FORMATADORES = {"pct": _fmt_pct, "moeda": _fmt_moeda, "int": _fmt_int}

# (chave da métrica, título da seção, cabeçalho do rótulo, cabeçalho do valor, formato)
SECOES = [
    ("perda_valor_por_etapa", "Valor solicitado perdido por etapa do funil", "Etapa", "Valor (R$)", "moeda"),
    ("conversao_por_canal", "Taxa de conversão por canal", "Canal", "Conversão", "pct"),
    ("volume_por_canal", "Volume de propostas por canal", "Canal", "Quantidade", "int"),
    ("conversao_por_mes", "Conversão por mês (meses recentes excluídos)", "Mês", "Conversão", "pct"),
    ("distribuicao_status", "Distribuição de status final", "Status", "Quantidade", "int"),
]

TEMPLATE_HTML = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<title>{{ titulo }}</title>
<style>
  :root { --fundo: #0A3D4C; --escuro: #072F3A; --claro: #fff; }
  body { margin: 0; padding: 32px 20px; background: var(--fundo); color: var(--claro);
         font-family: "Segoe UI", Arial, sans-serif; }
  .pagina { max-width: 900px; margin: 0 auto; }
  header, .destaque, .observacao { background: var(--escuro); border: 1px solid var(--claro);
         padding: 16px 24px; margin-bottom: 16px; }
  .logo { border: 2px solid var(--claro); padding: 4px 14px; letter-spacing: .3em; font-weight: 700; }
  h1 { margin: 16px 0 4px; font-size: 26px; }
  h2 { margin: 0 0 12px; font-size: 16px; }
  .meta, .rotulo { margin: 0; font-size: 13px; opacity: .85; }
  .destaques { display: flex; flex-wrap: wrap; gap: 12px; }
  .destaque { flex: 1; min-width: 180px; }
  .valor { margin: 4px 0 0; font-size: 24px; font-weight: 700; }
  .secao { background: var(--claro); color: var(--fundo); padding: 20px 24px; margin-bottom: 16px; }
  table { width: 100%; border-collapse: collapse; }
  th, td { padding: 8px 12px; border-bottom: 1px solid var(--fundo); text-align: left; }
  th { background: var(--fundo); color: var(--claro); }
  .num { text-align: right; }
</style>
</head>
<body><div class="pagina">
  <header>
    <span class="logo">BARI</span>
    <h1>{{ titulo }}</h1>
    <p class="meta">Gerado em {{ gerado_em }}</p>
  </header>

  <div class="destaques">
    {% for d in destaques %}
    <div class="destaque"><p class="rotulo">{{ d.rotulo }}</p><p class="valor">{{ d.valor }}</p></div>
    {% endfor %}
  </div>

  {% for s in secoes %}
  <section class="secao">
    <h2>{{ s.titulo }}</h2>
    <table>
      <tr><th>{{ s.cab_rotulo }}</th><th class="num">{{ s.cab_valor }}</th></tr>
      {% for l in s.linhas %}<tr><td>{{ l.rotulo }}</td><td class="num">{{ l.valor }}</td></tr>{% endfor %}
    </table>
  </section>
  {% endfor %}

  {% if observacao %}<section class="observacao"><h2>Observações</h2>{{ observacao }}</section>{% endif %}
</div></body>
</html>
"""


def _montar_destaques(metricas: dict) -> list[dict]:
    ltv = metricas.get("ltv_politica")
    if not ltv:
        return []
    limite = f"{LTV_MAXIMO_POLITICA:.0%}"
    return [
        {"rotulo": f"Propostas com LTV > {limite}", "valor": _fmt_int(ltv["qtd_acima"])},
        {"rotulo": "Conversão dentro da política", "valor": _fmt_pct(ltv["conversao_dentro"])},
        {"rotulo": "Conversão acima da política", "valor": _fmt_pct(ltv["conversao_acima"])},
    ]


def _montar_secoes(metricas: dict) -> list[dict]:
    return [
        {
            "titulo": titulo, "cab_rotulo": cab_rotulo, "cab_valor": cab_valor,
            "linhas": [{"rotulo": str(r), "valor": FORMATADORES[formato](v)}
                       for r, v in metricas[chave].items()],
        }
        for chave, titulo, cab_rotulo, cab_valor, formato in SECOES if chave in metricas
    ]


def exportar_relatorio(metricas: dict, pasta_saida: Path, logger: logging.Logger) -> Path:
    """Renderiza o template HTML com as métricas e salva o arquivo do dia."""
    pasta_saida.mkdir(parents=True, exist_ok=True)
    caminho = pasta_saida / f"relatorio_funil_{datetime.now():%Y-%m-%d}.html"

    meses_excluidos = metricas.get("meses_excluidos_por_censura")
    observacao = (f"Meses excluídos da série de conversão por estarem incompletos "
                  f"(censura de dados): {', '.join(meses_excluidos)}") if meses_excluidos else None

    template = Environment(autoescape=True).from_string(TEMPLATE_HTML)
    html = template.render(
        titulo="Relatório Semanal do Funil de Crédito",
        gerado_em=f"{datetime.now():%d/%m/%Y %H:%M}",
        destaques=_montar_destaques(metricas),
        secoes=_montar_secoes(metricas),
        observacao=observacao,
    )
    caminho.write_text(html, encoding="utf-8")
    logger.info(f"Relatório HTML gerado em '{caminho}'")
    return caminho


# ---------------------------------------------------------------- orquestração
def _executar_etapa(logger: logging.Logger, nome: str, funcao, *args, fatal: bool = True):
    """Roda uma etapa do pipeline; em caso de erro registra no log e (se fatal) encerra."""
    try:
        return funcao(*args, logger)
    except Exception as erro:
        logger.error(f"FALHA na etapa '{nome}': {erro}")
        if fatal:
            logger.error("Execução interrompida - nenhum relatório foi gerado.")
            sys.exit(1)
        return None


def main() -> None:
    parser = argparse.ArgumentParser(description="RPA - relatório semanal do funil Bari")
    parser.add_argument("--entrada", default="propostas_credito.csv", help="CSV de entrada")
    parser.add_argument("--pasta-logs", default="logs", help="Pasta dos logs")
    parser.add_argument("--pasta-saida", default="saidas", help="Pasta do relatório")
    args = parser.parse_args()

    logger = configurar_logger(Path(args.pasta_logs))
    logger.info("=" * 60)
    logger.info("Início da execução do RPA - Relatório Semanal do Funil")

    df_bruto = _executar_etapa(logger, "leitura", ler_dados, Path(args.entrada))
    _executar_etapa(logger, "validação de schema", validar_schema, df_bruto)
    df_limpo = _executar_etapa(logger, "tratamento", tratar_dados, df_bruto)
    metricas = _executar_etapa(logger, "métricas", calcular_metricas, df_limpo, fatal=False) or {}
    caminho = _executar_etapa(logger, "exportação", exportar_relatorio, metricas, Path(args.pasta_saida))

    logger.info(f"Execução concluída com sucesso. Relatório em: {caminho}")


if __name__ == "__main__":
    main()
