# MobMetrics: A Tool for Processing and Analyzing Mobility Trace Metrics

**MobMetrics** é uma aplicação desenvolvida para analisar, de forma prática e eficiente, rastros de mobilidade de diferentes tipos — como pedestres, veículos, bicicletas, entre outros. A ferramenta calcula métricas nativas e oferece uma arquitetura modular, permitindo que o usuário adicione suas próprias métricas. Tudo isso é acessado por meio de uma interface intuitiva, facilitando o uso e a personalização das análises.

Com base no padrão adotado pelo *Salão de Ferramentas da SBRC 2025*, este projeto foi desenvolvido visando atender aos quatro selos de qualidade, descritos a seguir:

- **1. Artefatos Disponíveis (Selo D):** Garante que o código e/ou dados estejam acessíveis em um repositório público com documentação mínima, como o arquivo `README.md`.
- **2. Artefatos Funcionais (Selo F):** Certifica que a aplicação pode ser executada com sucesso, incluindo instruções claras de instalação, dependências e um exemplo funcional.
- **3. Artefatos Sustentáveis (Selo S):** Assegura que o código seja organizado, modular e compreensível, com documentação mínima que facilite o entendimento por terceiros.
- **4. Experimentos Reprodutíveis (Selo R):** Permite que os experimentos descritos no artigo sejam reproduzidos, com scripts e instruções que levem aos mesmos resultados apresentados.

Mais informações sobre os selos podem ser encontrados no [link](https://doc-artefatos.github.io/sbrc2025/).

---

# Estrutura Readme

- [MobMetrics](#mobmetrics-a-tool-for-processing-and-analyzing-mobility-trace-metrics)
- [Selos Considerados](#selos-considerados)
  - [1. Artefatos Disponíveis (Selo D)](#1-artefatos-disponíveis-selo-d)
  - [2. Artefatos Funcionais (Selo F)](#2-artefatos-funcionais-selo-f)
  - [3. Artefatos Sustentáveis (Selo S)](#3-artefatos-sustentáveis-selo-s)
  - [4. Experimentos Reprodutíveis (Selo R)](#4-experimentos-reprodutíveis-selo-r)
- [Instalação](#instalação)
  - [Dependências](#dependencias)
- [Executando](#executando)
  - [Ambiente de Execução](#ambiente-de-execução)
  - [Teste Mínimo](#teste-mínimo)
- [Requisitos Mínimos](#requisitos-mínimos)
- [LICENSE](#license)

---

# Instalação


1. Instale o [Python](https://www.python.org/downloads/).

2. Instale o [Miniconda](https://docs.conda.io/en/latest/miniconda.html) (ou Anaconda).

3. Instale o [Git](https://git-scm.com/downloads).

4. Clone o repositório

```bash
$ git clone {repository_url_here}.git
```

5. Abra o repositorio

```bash
$ cd /caminho_repositório/MOBMETRICS
```

6. Crie um novo ambiente

```bash
$ conda env create-f enviroment.yml
```
```bash
$ conda activate MobMetrics
```

7. Faça as migrations
```bash
$ python MobMetrics/manage.py makemigrations
```
```bash
$ python MobMetrics/manage.py migrate
```

## Dependências

As dependências estão todas listadas no arquivo [environment.yml](./environment.yml).

---

# Executando

Para executar o programa, primeiro é necessário iniciar o servidor Django. Isso pode ser feito com o seguinte comando:

```bash
python MobMetrics/manage.py runserver
```

Esse comando inicializa o servidor de desenvolvimento local. Após a execução, você pode acessar a aplicação diretamente pelo navegador no seguinte endereço:

[http://127.0.0.1:8000/](http://127.0.0.1:8000/)

> Obs.: Esse link pode variar de acordo com a máquina ou configurações locais. O terminal exibirá a URL exata com a seguinte mensagem:
>
> ```
> Starting development server at http://<endereço-local>/
> ```

---

## Ambiente de Execução

A aplicação é organizada em quatro abas principais: `Home`, `Upload & Process`, `Results` e `Manage Files`.

1. **Home**  
   Página inicial contendo uma introdução à aplicação e instruções básicas de uso.

2. **Upload & Process**  
   Nesta aba é realizado o upload do rastro e a configuração dos parâmetros para análise de métricas.  
   Cada campo possui um ícone de interrogação que, ao passar o mouse sobre ele, exibe uma descrição explicativa.

3. **Results**  
   Após o envio dos arquivos na aba anterior, os resultados das análises e comparações entre rastros, entidades e labels são exibidos aqui.  
   Assim como na aba anterior, é possível configurar parâmetros para os métodos PCA e t-SNE, com descrições disponíveis ao passar o mouse sobre os campos.

4. **Manage Files**  
   Esta aba permite visualizar, baixar e excluir arquivos já enviados.  
   Os arquivos são listados com botões individuais para:
   - Fazer o download em formato `.zip` contendo os arquivos `.csv` com os resultados das métricas.
   - Remover os arquivos da memória do sistema.

> Importante: Os arquivos permanecem salvos em memória mesmo após reiniciar a aplicação, a menos que sejam excluídos manualmente.


## Teste Mínimo

Para colocar em prática as funcionalidades do **MobMetrics**, utilizaremos os datasets disponíveis na pasta [experiments/Anglova](./experiments/Anglova/). Esses datasets foram coletados do site [Anglova](https://anglova.net/).

O dataset original é o arquivo [anglova.csv](./experiments/Anglova/anglova.csv), que foi particionado em 4 rastros diferentes. Cada um representa um tipo de entidade:

- **Tanks**
- **Staff and Mortar**
- **Mechanized Infantry**
- **Logistics**

Cada rastro está em um arquivo `.csv` separado.

### Passo a Passo

#### 1. Instalar e executar a aplicação

Certifique-se de que a aplicação está instalada e em execução. As instruções para isso foram fornecidas anteriormente.

#### 2. Upload e configuração dos arquivos

Acesse a aba `Upload & Process` e envie os arquivos `.csv` da pasta [experiments/Anglova](./experiments/Anglova/), **um por vez**.

Para cada arquivo, preencha os seguintes campos:

- **Trace File:** Selecione o arquivo correspondente.  
  > ⚠️ O arquivo `anglova.csv` **não será utilizado** nesta etapa (mas pode ser usado, se necessário).
- **Name:** Um nome descritivo para o arquivo (ex: `Anglova Tanks`)
- **Label:** O tipo da entidade (ex: `Tanks`)
- **Geographical Coordinates:** Marcar como **ativo**
- **Distance Threshold:** `60`
- **Time Threshold:** `20`
- **Radius Threshold:** `10`
- **Quadrant Divisions:** `10`

##### Tempo de execução estimado para cada arquivo:

- **Anglova Tanks:** ~[inserir tempo]
- **Anglova Mechanized Infantry:** ~[inserir tempo]
- **Anglova Logistics:** ~[inserir tempo]
- **Anglova Staff and Mortar:** ~[inserir tempo]

#### 3. Visualizar resultados

Após o envio e processamento dos quatro arquivos, vá para a aba `Results`. Nela, configure os seguintes parâmetros:

- **PCA N Components:** `[inserir valor]`
- **t-SNE N Components:** `[inserir valor]`
- **t-SNE Perplexity:** `[inserir valor]`

Depois disso, gere os gráficos para visualizar os resultados.

#### 4. Gerenciar arquivos

Na aba `Manage Files`, é possível:

- Excluir rastros enviados anteriormente
- Baixar os arquivos processados para análise individual



---

# Requisitos Mínimos

Liste as configurações mínimas exigidas para executar o sistema, como memória RAM, espaço em disco e versão do sistema operacional.

---


# LICENSE
