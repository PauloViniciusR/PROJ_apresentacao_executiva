# Notas do Projeto

## O que foi feito

- Reorganização do repositório para uma estrutura mais apresentável no GitHub.
- Separação entre dados brutos, notebook, figuras, código reutilizável e app.
- Criação de um pipeline simples em `src/data.py` e `src/features.py`.
- Criação de camada tratada em `data/processed/`, com dataset final e relatório de qualidade.
- Criação de script reproduzível em `scripts/build_processed_dataset.py`.
- Criação de dashboard Streamlit em `app/app.py`.
- Declaração de dependências em `requirements.txt`.

## Decisoes tecnicas

- O dataset bruto foi mantido em `data/raw/` para preservar a origem dos dados.
- O dataset tratado foi materializado em `data/processed/` para deixar o tratamento visível no case.
- As transformações principais ficaram fora do notebook para evitar duplicação no app.
- Datas são interpretadas no formato `dd/mm/yyyy`, conforme a base original.
- Registros sem data de pedido, sem valor de venda válido, com venda não positiva ou com envio anterior ao pedido são removidos no tratamento.
- CEPs foram mantidos como texto para preservar zeros à esquerda.
- Os 11 CEPs ausentes pertenciam a Burlington, Vermont, e foram preenchidos de forma explícita com `05401`.
- Uma duplicidade comercial foi removida porque repetia pedido, cliente, produto, datas, modo de envio e valor.

## Possíveis próximos passos

- Publicar o app no Streamlit Community Cloud usando este repositório.
- Adicionar testes unitários para as funções de tratamento e agregação.
