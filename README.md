<h1 align="center"> Ferramenta IWSHAP </h1>

<p align="center">
<img loading="lazy" src="https://img.shields.io/badge/release_date-07/2024-green"/>
<img loading="lazy" src="https://img.shields.io/badge/version-1.0-blue"/>
<img loading="lazy" src="https://img.shields.io/badge/python-V3.12.3-yellow"/>
</p>

IWSHAP é uma ferramenta de seleção de características que combina o algoritmo _Incremental Wrapper Subset Selection_ (IWSS) com valores SHAP (_SHapley Additive exPlanations_) com o objetivo de alcançar as melhores características para a detecção de ataques. A presente ferramenta permite identificar um conjunto de características reduzido ao mesmo tempo em que busca manter ou melhorar as métricas de desempenho do modelo. Ainda, a ferramenta dispõe de gráficos que visam a explicabilidade das características através dos valores SHAP. Dessa forma, busca-se alcançar um equilíbrio entre o desempenho do modelo de aprendizado de máquina e o tempo de otimização do conjunto de características analisados.

## Dependências do IWSHAP
Todas as dependências serão instaladas junto ao docker, sendo elas:
- pandas==2.2.2
- numpy==1.26.4
- shap==0.45.1
- xgboost==2.0.3
- scikit-learn==1.5.0
- matplotlib==3.9.0
- pyarrow==16.1.0

## 1. Pré-Configurações
Antes de tudo, é necessário clonar este repositório
```
  git clone https://github.com/sf24-iwshap/sf24-iwshap
```

Depois, entre no diretório clonado
```
cd sf24-IWSHAP
```

## 2. Escolha o ambiente
Você pode executar a ferramenta de algumas maneiras, sendo elas: **a)** Demonstração da ferramenta; **b)** Ambiente Docker; **c)** No seu computador (Linux)

<details>
  
  <summary>Demonstração</summary>

 # Executando script demo da ferramenta

  - ### Opção 1:
    - Esse script instalará os requisitos no seu sistema e executará a ferramenta IWSHAP
      Dentro do diretório do IWSHAP:
        ```
        ./run_demo_app.sh
        ```
  - ### Opção 2:
    - Esse script baixará e executará a imagem sf24/iwshap:latest disponivel em: [DockerHub](https://hub.docker.com/r/sf24/iwshap).
        ```
        ./run_demo_docker.sh
        ```
      Após isso é possivel executar a ferrameta diretamente utilizando o script da opção 1
        ```
        ./run_demo_app.sh
        ```
</details>

<details>

   <summary>Docker 🐳</summary>

   ## Execução em ambiente Docker
O IWSHAP disponibiliza um ambiente Docker com todas as configurações e dependências necessárias para a execução da ferramenta. Para isso, é necessário possuir uma instalação do Docker em execução no seu computador.

  - ### Ambiente Docker 
    - `Linux 38ad4d51e477 5.15.153.1-microsoft-standard-WSL2 #1 SMP Fri Mar 29 23:14:13 UTC 2024 x86_64 x86_64 x86_64 GNU/Linux`
    - `Python 3.12.3`

  - ### Instalação do Docker
    Linux: 
      ```
      apt install docker docker.io
      ```
    Windows:
      - Acesse o site oficial do Docker Desktop para Windows: [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/)

  - ### Construindo a imagem
    Dentro do diretório do IWSHAP:
      ```
      docker build . -t iwshap
      ```
  
  - ### Executando a imagem
      ```
      docker run -it iwshap
      ```
   
</details> 

<details>
  
  <summary>Linux :penguin:</summary>

  # Executando a ferramenta no Linux

## 1. Configurando o ambiente virtual

  ### Instalação do virtualenv para o python3
    sudo apt-get install python3-venv
    
  ### Criação do ambiente virtual
  Dentro do diretório da ferramenta, execute:
    
    python3 -m venv .venv 

  ### Ativando o ambiente virtual
  Dentro do diretório da ferramenta, execute:
  ```
  source .venv/bin/activate 
  ```

  ### Instalando dependências
  ```
  pip install -r requirements.txt
  ```
  
</details>

# ⚙️ Executando a ferramenta (Execução com os datasets reduzidos)
  Exemplo de execução simples:
  ```
  python3 IWSHAP.py -s dataset/safe_dataset.csv -a dataset/attack_dataset_fabr.csv
  ```

  Exemplo de execução gerando gráfico summary plot:
  ```
  python3 IWSHAP.py -s dataset/safe_dataset.csv -a dataset/attack_dataset_fabr.csv -x
  ```

  Exemplo de execução gerando gráfico summary plot e o dataset reduzido:
  ```
  python3 IWSHAP.py -s dataset/safe_dataset.csv -a dataset/attack_dataset_fabr.csv -x -n
  ```

# ⚙️ Executando a ferramenta(Execução com os datasets completos)
  Exemplo de execução simples:
  ```
  python3 IWSHAP.py -s dataset/safe_dataset_full.parquet -a dataset/attack_dataset_fabr_260h_full.parquet
  ```

  Exemplo de execução gerando gráfico summary plot:
  ```
  python3 IWSHAP.py -s dataset/safe_dataset_full.parquet -a dataset/attack_dataset_fabr_260h_full.parquet -x
  ```

  Exemplo de execução gerando gráfico summary plot e o dataset reduzido:
  ```
  python3 IWSHAP.py -s dataset/safe_dataset_full.parquet -a dataset/attack_dataset_fabr_260h_full.parquet -x -n
  ```

## Significado das flags
| Flag   | Parâmetro      | Descrição | Obrigatória |
| ------ | ------         | ------    | ------      |
| **-s**     | --safe-path     | Caminho para o dataset benigno | Sim |
| **-a**     | --attack-path   | Caminho para o dataset maligno | Sim |
| **-l**     | --log-path      | Caminho para armazenamento dos logs | Não |
| **-g**     | --graphics-path | Caminho para armazenamento dos gráficos | Não  |
| **-x**     | --explanable   | Define a criação de um gráfico Summary Plot das features mais importantes | Não |
| **-n**     | --newdata-reduced | Define a geração de um dataset reduzido com as melhores caracteristicas | Não |

### Exemplos de uso das flags:
```
python3 IWSHAP.py -s <safe_path> -a <attack_path>
python3 IWSHAP.py -s <safe_path> -a <attack_path> -l <log_path>
python3 IWSHAP.py -s <safe_path> -a <attack_path> -l <log_path> -g <graphics_path>
python3 IWSHAP.py -s <safe_path> -a <attack_path> -x
python3 IWSHAP.py -s <safe_path> -a <attack_path> -x -n
```

## Requisitos de hardware recomendados:

- Ambiente Docker com 32gb* de ram;
- Processador I5 (min 10º geração) ou equivalente.

*Considerando o conjunto de dados completo utilizado nos experimentos.
*Para conjuntos menores, como o dataset reduzido disponibilizado, 8gb de ram(ambiente docker) é o sufiente para a execução completa da ferramenta.

## Ambiente de teste
Para ambiente de teste fez-se o uso de um servidor com: 
- Ubuntu versão 22.04
- AMD Ryzen 7 5800x com 8 cores
- 64 GB de memória RAM

## Executando o dataset de demonstração
Se deseja apenas testar a ferramenta para familiarizar-se com o uso, não é necessário informar os caminhos para seus próprios datasets. É possível utilizar os datasets de demonstração incluídos, que possuem um tamanho reduzido e, consequentemente, exigem menos tempo e recursos para sua execução.
