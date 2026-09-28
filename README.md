# Estágio AI & Data Lab | Bari

Funil de crédito com garantia de imóvel: diagnóstico (Parte 1), automação do relatório semanal (Parte 2)
e extração estruturada de laudos (Parte 3). Todos os dados são os sintéticos fornecidos no desafio.

## Como rodar

Requisitos: Python 3.10+.

```bash
pip install -r requirements.txt

python rpa_bari.py --entrada propostas_credito.csv   # Parte 2: gera logs/ e saidas/relatorio_funil_AAAA-MM-DD.html
python extrator_laudos.py                            # Parte 3: gera saidas/laudos_extraidos.json e .csv
python avaliar_extracao.py                           # Parte 3: acurácia contra o gabarito manual
```

Opções do RPA: `--entrada` (CSV), `--pasta-logs` (padrão `logs`), `--pasta-saida` (padrão `saidas`).

## O que tem em cada arquivo

| Arquivo | Conteúdo |
|---|---|
| `rpa_bari.py` | Parte 2. Pipeline: ler → validar colunas → tratar → calcular métricas → exportar HTML (Jinja2) |
| `extrator_laudos.py` | Parte 3. Extrator por regras (regex) dos 17 laudos |
| `gabarito_laudos.py` | Parte 3. Verdade de referência escrita à mão |
| `avaliar_extracao.py` | Parte 3. Mede a acurácia do extrator |
| `PARTE3_METODOLOGIA.md` | Parte 3. Decisões, critério de acerto, resultado e limitações |
| `DIARIO.md` | Parte 4. Diário de bordo |
| `propostas_credito.csv`, `laudos_avaliacao/` | Dados fornecidos (sintéticos) |
| `saidas/` | Exemplos de saída: relatório HTML e laudos extraídos |
| `logs/` | Exemplo de log de uma execução |
| `requirements.txt` | Dependências (`pandas`, `jinja2`) |

## Parte 2 — como alguém que não sou eu roda toda segunda

O script roda, gera o relatório e termina; quem dispara é o sistema operacional.

- **Linux/Mac (cron)**: `0 7 * * 1 cd /caminho/do/projeto && python3 rpa_bari.py`
- **Windows**: Agendador de Tarefas, gatilho semanal (segunda), ação "iniciar programa" com
  `python.exe rpa_bari.py` e "iniciar em" apontando para a pasta do projeto.

O relatório do dia fica em `saidas/` e o log da execução em `logs/execucao_AAAAMMDD_HHMMSS.log`.
Em caso de falha fatal o script termina com **código de saída 1** (o agendador registra como erro) e
não gera relatório parcial.

### O que acontece se o arquivo vier diferente

| Situação | Comportamento |
|---|---|
| Falta coluna **obrigatória** | Para, log com o nome da coluna, sem relatório, exit 1 |
| Falta coluna **opcional** | Aviso no log e segue. Hoje nenhuma métrica usa colunas opcionais, então o relatório não muda |
| Coluna **nova** | Aviso no log; ignorada |
| Arquivo inexistente | Para, log claro, exit 1 |
| Separador diferente (`;`) ou codificação diferente (latin-1) | **Não adapta sozinho**: cai no erro de coluna ausente / de leitura, com mensagem clara, exit 1 |
| Uma métrica falha | Aviso no log; as demais métricas e o relatório continuam |

Limitação conhecida: não há detecção automática de separador nem de codificação.

### Tratamento de dados (cada item também aparece no log de execução)

1. `valor_imovel` com "R$" misturado a números puros → normalizado para número.
2. `canal_origem` com grafias duplicadas (`mídia paga` / `Mídia paga`) → padronizado.
3. `data_entrada` em dois formatos (`AAAA-MM-DD` e `DD/MM/AAAA`) → normalizado.
4. `idade_cliente` < 18 → **sinalizada** (`idade_suspeita`), não descartada.
5. `etapa_max_funil` fora de 1–6 → excluída só das métricas de funil, mantida no resto.
6. `ltv` está no dicionário mas não existe no CSV → calculado como `valor_solicitado / valor_imovel`.
7. `tipo_imovel == "Terreno"` → removido (instrução do desafio).

### Meses recentes (censura de dados)

Os 2 últimos meses da base têm poucas propostas e ainda estão em andamento, o que faz a conversão parecer
menor só por falta de tempo. Eles são excluídos da série mensal e listados nas observações do relatório.
O número de meses excluídos é a constante `MESES_EXCLUIDOS_POR_CENSURA` (é uma escolha, não um fato).

## Testes feitos

Cenários executados manualmente: CSV completo; sem coluna opcional; sem coluna obrigatória; com coluna nova;
arquivo inexistente; separador `;`; codificação latin-1. A versão refatorada foi comparada com a versão
anterior do script no mesmo CSV: perda por etapa, conversão por canal, conversão por mês, LTV e status
saíram idênticos. `flake8 --max-line-length=110` sem avisos nos scripts.

## Tempo gasto

No total foram 12 horas (de domingo 27/09 às 14:30 até segunda 28/09 às 2:30), contando pequenas
pausas para refeições. A distribuição foi aproximadamente esta:

| Etapa | Horas | % do total |
|---|---|---|
| Parte 1 — leitura do desafio, exploração e tratamento dos dados, análise | ~2h20 | 20% |
| Parte 2 — script do RPA (logging, validação de schema, relatório HTML) | ~2h20 | 20% |
| Parte 3 — extração dos laudos (regex, gabarito, avaliação) | ~2h25 | 19% |
| Estudo de conceitos novos (logging, regex, censura de dados) | ~1h00 | 8% |
| Revisão e refatoração (clean code) | ~1h15 | 10,4% |
| Parte 4 — diário de bordo | ~0h45 | 6,3% |
| README, zip e GitHub | ~1h | 10,4% |
| Pausas | ~0h45 | 6,3% |
| **Total** | **~12h00** | **~100%** |
