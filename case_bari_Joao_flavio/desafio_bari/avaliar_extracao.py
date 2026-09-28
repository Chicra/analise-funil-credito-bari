"""Mede a acurácia do extrator contra o gabarito manual (gabarito_laudos.py).

Critérios de acerto de cada campo: ver comentários em gabarito_laudos.py.
Uso: python avaliar_extracao.py   (rode antes o extrator_laudos.py)
"""
import json

from gabarito_laudos import GABARITO, GABARITO_EXTRA, LAUDOS_COM_CONFLITO_DE_AREA

CAMPOS_EXATOS = [
    "tipo_imovel", "ano_construcao", "valor_avaliacao",
    "matricula", "onus_status", "data_vistoria",
]


def _conjunto_de_areas(extraido: dict) -> set:
    return {f"{a['valor']} {a['unidade']}" for a in extraido["areas"]}


def _avaliar_documento(arquivo: str, extraido: dict) -> dict:
    """Devolve {campo: (acertou, esperado, obtido)} para um laudo."""
    esperado = GABARITO[arquivo]
    extra = GABARITO_EXTRA[arquivo]
    resultado = {c: (extraido[c] == esperado[c], esperado[c], extraido[c]) for c in CAMPOS_EXATOS}

    areas = _conjunto_de_areas(extraido)
    resultado["areas"] = (areas == extra["areas"], extra["areas"], areas)

    endereco = extraido["endereco"] or ""
    resultado["endereco"] = (extra["endereco_contem"] in endereco, extra["endereco_contem"], endereco)

    resultado["responsavel_tecnico"] = (
        extraido["responsavel_tecnico"] == extra["responsavel_tecnico"],
        extra["responsavel_tecnico"], extraido["responsavel_tecnico"])

    detectou = any("CONFLITO" in alerta for alerta in extraido["alertas"])
    deveria = arquivo in LAUDOS_COM_CONFLITO_DE_AREA
    resultado["conflito_area"] = (detectou == deveria, deveria, detectou)
    return resultado


def avaliar() -> float:
    with open("saidas/laudos_extraidos.json", encoding="utf-8") as arquivo_json:
        extraidos = {d["arquivo"]: d for d in json.load(arquivo_json)}

    acertos, totais, divergencias = {}, {}, []
    for arquivo in GABARITO:
        for campo, (acertou, esperado, obtido) in _avaliar_documento(arquivo, extraidos[arquivo]).items():
            totais[campo] = totais.get(campo, 0) + 1
            acertos[campo] = acertos.get(campo, 0) + acertou
            if not acertou:
                divergencias.append((arquivo, campo, esperado, obtido))

    print("=" * 66)
    print("ACURÁCIA POR CAMPO")
    print("=" * 66)
    for campo, total in totais.items():
        print(f"  {campo:22s}: {acertos[campo]:2d}/{total:2d}  ({acertos[campo] / total:.0%})")
    soma_acertos, soma_total = sum(acertos.values()), sum(totais.values())
    print("-" * 66)
    print(f"  {'TOTAL':22s}: {soma_acertos:3d}/{soma_total:3d}  ({soma_acertos / soma_total:.0%})")

    for arquivo, campo, esperado, obtido in divergencias:
        print(f"  DIVERGÊNCIA [{arquivo}] {campo}: esperado={esperado!r} | obtido={obtido!r}")
    return soma_acertos / soma_total


if __name__ == "__main__":
    avaliar()
