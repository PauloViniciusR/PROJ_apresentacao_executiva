# Notas do Projeto

## O que foi feito

- Reorganizacao do repositorio para uma estrutura mais apresentavel no GitHub.
- Separacao entre dados brutos, notebook, figuras, codigo reutilizavel e app.
- Criacao de um pipeline simples em `src/data.py` e `src/features.py`.
- Criacao de dashboard Streamlit em `app/app.py`.
- Declaracao de dependencias em `requirements.txt`.

## Decisoes tecnicas

- O dataset bruto foi mantido em `data/raw/` para preservar a origem dos dados.
- As transformacoes principais ficaram fora do notebook para evitar duplicacao no app.
- Datas sao interpretadas no formato `dd/mm/yyyy`, conforme a base original.
- Registros sem data de pedido ou valor de venda valido sao removidos no tratamento.

## Possiveis proximos passos

- Adicionar testes unitarios para as funcoes de tratamento e agregacao.
- Publicar o app no Streamlit Community Cloud usando este repositorio.
- Criar uma camada `data/processed/` caso novas transformacoes persistidas sejam necessarias.
