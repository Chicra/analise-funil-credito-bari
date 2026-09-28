# Parte 3 — Extração estruturada dos laudos

## Arquivos

| Arquivo | Função |
|---|---|
| `extrator_laudos.py` | Lê `laudos_avaliacao/*.txt` e gera `saidas/laudos_extraidos.json` e `.csv` |
| `gabarito_laudos.py` | Verdade de referência, montada à mão lendo os 17 laudos |
| `avaliar_extracao.py` | Compara extração x gabarito e imprime a acurácia por campo |

```bash
python extrator_laudos.py
python avaliar_extracao.py
```

## Por que regras (regex) e não um LLM generativo

O enunciado diz que um extrator que "chuta um valor plausível é pior do que um que assume que não sabe".
Regex é **determinístico e auditável**: para cada valor da saída dá para apontar o trecho do texto e o
padrão que o produziu, e rodar duas vezes dá o mesmo resultado. Também deixa explícito o "não sei".

## Formato de saída

Todo laudo produz um objeto com as mesmas chaves, sempre na mesma ordem: `arquivo, tipo_imovel, endereco,
areas, ano_construcao, valor_avaliacao, matricula, onus_status, onus_tipo, onus_texto, data_vistoria,
responsavel_tecnico, alertas`. Campo ausente vira `null`, nunca uma chave faltando.

## Campo ausente e documento contraditório

- **Ausente**: valor `null` + explicação em `alertas` (ex.: laudo_08 declara "matrícula não apresentada").
- **Só idade, sem ano** (laudos 03 e 14): `ano_construcao = null`. Calcular o ano a partir da idade seria
  inferência, não extração.
- **Contradição** (laudo_17: área total 95 m² no cabeçalho x 92 m² na tabela): os dois valores ficam na
  lista de áreas e um alerta `CONFLITO` é gerado. O extrator não escolhe um deles.
- **Ônus**: quatro estados — `ÔNUS IDENTIFICADO`, `NENHUM IDENTIFICADO`, `NÃO INFORMADO / NÃO VERIFICÁVEL`.
  "Sem informação" no laudo nunca é convertido em "sem ônus".

## Critério de acerto

Gabarito manual, campo a campo. Um campo só conta como acerto se:

| Campo | Regra |
|---|---|
| tipo, ano, valor, matrícula, ônus (status), data | igualdade exata; se o correto é "não existe" (`None`), o extrator precisa devolver `None` |
| áreas | conjunto de `valor + unidade` **igual** ao esperado (nem falta, nem sobra), sem olhar o rótulo |
| endereço | a extração contém o logradouro + número (ou o município, quando o laudo não traz rua) |
| responsável técnico | texto igual à linha do laudo (nome + registro profissional) |
| conflito | detectado exatamente nos laudos que se contradizem, e em nenhum outro |

## Resultado

```
tipo_imovel / ano_construcao / valor_avaliacao / matricula /
onus_status / data_vistoria / areas / endereco /
responsavel_tecnico / conflito_area      -> 17/17 em cada  (170/170 = 100%)
```

**Como ler esse 100%:** o extrator foi ajustado por tentativa e erro **nestes mesmos 17 laudos**, então
a medida é *in-sample*: prova que ele cobre os formatos vistos, não que generaliza. Um laudo com redação
nova provavelmente devolveria `null` em alguns campos, que é o comportamento desejado, mas não está medido.
Além disso, o gabarito foi escrito pela mesma pessoa/ferramenta que calibrou o extrator (viés de
confirmação); o ideal seria um segundo revisor.

Durante a revisão final encontrei e corrigi uma falha que a primeira versão da métrica escondia: 3 laudos
perdiam uma área (146,00 m² no laudo_02, 310 m² no laudo_05 e o terreno de 600 m² no laudo_12) porque a
métrica original não cobria áreas.

## Limitações conhecidas

- `endereco` é a sentença inteira com a localização; não separa rua, número, bairro, cidade e UF.
- Regex depende das palavras-chave dos 17 formatos; texto totalmente diferente cai em `null`.
- Fora do escopo medido: `onus_tipo` e `onus_texto` (descritivos) não entram na acurácia.
