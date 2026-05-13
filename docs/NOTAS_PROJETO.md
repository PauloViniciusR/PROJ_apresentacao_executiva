# Notas do Projeto

## O que foi feito

- Reorganizacao do repositorio para uma estrutura mais apresentavel no GitHub.
- Separacao entre dados brutos, notebook, figuras, codigo reutilizavel e app.
- Criacao de um pipeline simples em `src/data.py` e `src/features.py`.
- Criacao de camada tratada em `data/processed/`, com dataset final e relatorio de qualidade.
- Criacao de script reproduzivel em `scripts/build_processed_dataset.py`.
- Criacao de dashboard Streamlit em `app/app.py`.
- Declaracao de dependencias em `requirements.txt`.

## Decisoes tecnicas

- O dataset bruto foi mantido em `data/raw/` para preservar a origem dos dados.
- O dataset tratado foi materializado em `data/processed/` para deixar o tratamento visivel no case.
- As transformacoes principais ficaram fora do notebook para evitar duplicacao no app.
- Datas sao interpretadas no formato `dd/mm/yyyy`, conforme a base original.
- Registros sem data de pedido, sem valor de venda valido, com venda nao positiva ou com envio anterior ao pedido sao removidos no tratamento.
- CEPs foram mantidos como texto para preservar zeros a esquerda.
- Os 11 CEPs ausentes pertenciam a Burlington, Vermont, e foram preenchidos de forma explicita com `05401`.
- Uma duplicidade comercial foi removida porque repetia pedido, cliente, produto, datas, modo de envio e valor.

## Possiveis proximos passos

- Publicar o app no Streamlit Community Cloud usando este repositorio.
- Adicionar testes unitarios para as funcoes de tratamento e agregacao.
