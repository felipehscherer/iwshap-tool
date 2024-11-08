import time
import datetime
import pytz
import argparse
import numpy as np
import pandas as pd
import shap
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, recall_score, precision_score
from sklearn.preprocessing import LabelEncoder
from os import path, makedirs
import matplotlib.pyplot as plt


def create_log_directory(log_path):
    """
    Cria o diretório para armazenar os logs, se ele não existir.

    Args:
    log_path (str): Caminho onde o diretório de logs será criado.
    """
    print('Criando diretorio para os logs..')
    if not path.exists(log_path):
        makedirs(log_path)


def get_current_time_in_brazil():
    """
    Obtém a hora atual no fuso horário do Brasil.

    Returns:
    str: A hora atual formatada como "YYYY-MM-DD_HH-MM-SS".
    """
    brazil_tz = pytz.timezone('America/Sao_Paulo')
    brazil_time = datetime.datetime.now(brazil_tz)
    return brazil_time.strftime("%Y-%m-%d_%H-%M-%S")


def load_data(safe_path, attack_path):
    """
    Lê os datasets de caminhos fornecidos e os concatena.

    Args:
    safe_path (str): Caminho para o arquivo de dados seguro.
    attack_path (str): Caminho para o arquivo de dados de ataque.

    Returns:
    pd.DataFrame: DataFrame contendo os dados concatenados.
    """
    print('Lendo datasets..')
    file_extension = path.splitext(safe_path)[1].lower()
    
    if file_extension == '.csv':
        df_safe = pd.read_csv(safe_path)
        df_attack = pd.read_csv(attack_path)
    elif file_extension == '.parquet':
        df_safe = pd.read_parquet(safe_path)
        df_attack = pd.read_parquet(attack_path)
    
    return pd.concat([df_safe, df_attack], ignore_index=True)


def encode_categorical_features(df):
    """
    Codifica características categóricas no DataFrame em valores numéricos.

    Args:
    df (pd.DataFrame): DataFrame contendo os dados.

    Returns:
    pd.DataFrame: DataFrame com características categóricas codificadas.
    """
    print(f"Codificando tipos 'object' em tipos numericos..")
    for column in df.columns:
        if df[column].dtype == 'object':
            le = LabelEncoder()
            df[column] = le.fit_transform(df[column])
    return df


def split_data(df):
    """
    Separa os dados em conjuntos de treinamento e teste.

    Args:
    df (pd.DataFrame): DataFrame contendo os dados.

    Returns:
    tuple: Conjuntos de treinamento e teste para características (X) e rótulos (y).
    """
    X = df.drop("label", axis=1)
    y = df["label"]
    return train_test_split(X, y, test_size=0.2, random_state=42)


def train_and_evaluate_model(X_train, y_train, X_test, y_test):
    """
    Treina e avalia o modelo XGBoost.

    Args:
    X_train (pd.DataFrame): Conjunto de treinamento para características.
    y_train (pd.Series): Conjunto de treinamento para rótulos.
    X_test (pd.DataFrame): Conjunto de teste para características.
    y_test (pd.Series): Conjunto de teste para rótulos.

    Returns:
    tuple: O modelo treinado, F1 Score, Recall e Precision.
    """
    print('Treinando o modelo..')
    model = XGBClassifier(use_label_encoder=False, eval_metric="logloss")
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    
    f1 = f1_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    
    return model, f1, recall, precision


def calculate_feature_importance(model, X_train):
    """
    Calcula a importância das características usando SHAP.

    Args:
    model: Modelo treinado.
    X_train (pd.DataFrame): Conjunto de treinamento para características.

    Returns:
    pd.DataFrame: DataFrame contendo a importância das características.
    """
    print('Calculando a importancia das features..')
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_train)
    feature_importance = np.abs(shap_values).mean(axis=0)
    feature_importance_df = pd.DataFrame(
        {"feature": X_train.columns, "importance": feature_importance}
    ).sort_values(by="importance", ascending=False)
    
    return feature_importance_df


def evaluate_features(X_train, X_test, y_train, y_test, feature_importance_df, log):
    """
    Avalia as características usando o processo IWSHAP.

    Args:
    X_train (pd.DataFrame): Conjunto de treinamento para características.
    X_test (pd.DataFrame): Conjunto de teste para características.
    y_train (pd.Series): Conjunto de treinamento para rótulos.
    y_test (pd.Series): Conjunto de teste para rótulos.
    feature_importance_df (pd.DataFrame): DataFrame contendo a importância das características.
    log (file object): Arquivo de log para registrar o processo.

    Returns:
    tuple: Melhor conjunto de características, melhor F1 Score, melhor Recall, melhor Precision e melhor rodada.
    """
    print('Iniciando o processo IWSHAP..')
    best_features = []
    best_f1_score = 0
    best_recall = 0
    best_precision = 0
    best_round = 0

    for i in range(len(feature_importance_df)):
        log.write(f"Rodada: {i}\n")
        next_feature = feature_importance_df["feature"].iloc[i]
        current_features = best_features + [next_feature]
        log.write(f"Features atuais: \n {current_features}\n")

        X_train_selected = X_train[current_features]
        X_test_selected = X_test[current_features]

        before = time.time()

        model_selected = XGBClassifier(use_label_encoder=False, eval_metric="logloss")
        model_selected.fit(X_train_selected, y_train)
        y_pred_selected = model_selected.predict(X_test_selected)

        after = time.time()

        f1 = f1_score(y_test, y_pred_selected)
        recall = recall_score(y_test, y_pred_selected)
        precision = precision_score(y_test, y_pred_selected)

        log.write(
            f"F1 Score: {f1}, Recall: {recall}, Precision: {precision}, Tempo: {after - before} segundos\n"
        )

        if f1 > best_f1_score or f1 == 0.0:
            best_f1_score = f1
            best_precision = precision
            best_recall = recall
            best_round = i
            best_features = current_features
            log.write(f"Nova melhor F1 Score: {f1}\n com features:\n {best_features}\n")

    return best_features, best_f1_score, best_recall, best_precision, best_round

def save_best_features_dataset(df, best_features, formatted_time):
    """
    Salva o dataset apenas com as melhores características.

    Args:
    df (pd.DataFrame): DataFrame original.
    best_features (list): Lista das melhores características.
    output_path (str): Caminho onde o dataset será salvo.
    """

    data_path =  "reduced-datas"
    if not path.exists(data_path):
        print('Criando diretorio para os datasets reduzidos..')
        makedirs(data_path)
    print('Salvando o novo dataset reduzido..')
    data_file = path.join(data_path, f"dataset_reduced_{formatted_time}.csv")
    df_best_features = df[best_features]
    df_best_features.to_csv(data_file, index=False)



def plot_metrics(graphic_path, formatted_time, best_f1_score, best_recall, best_precision, best_round):
    """
    Gera e salva gráficos das métricas de desempenho.

    Args:
    graphic_path (str): Caminho onde os gráficos serão salvos.
    formatted_time (str): Tempo formatado para nomear o arquivo.
    best_f1_score (float): Melhor F1 Score.
    best_recall (float): Melhor Recall.
    best_precision (float): Melhor Precision.
    best_round (int): Melhor rodada.
    """
    print('Fazendo a plotagem dos graficos de metricas..')
    if not path.exists(graphic_path):
        makedirs(graphic_path)

    metrics = ['F1 Score', 'Recall', 'Precision']
    scores = [best_f1_score, best_recall, best_precision]  
    scores_percent = [score * 100 for score in scores]

    plt.figure(figsize=(10, 6))
    plt.bar(metrics, scores_percent, color=['purple', 'blue', 'red'])
    plt.xlabel('Metrics', fontsize=14)
    plt.ylabel('Scores (%)', fontsize=14)
    plt.title(f'Best F1 Score, Recall, and Precision in round: {best_round}', fontsize=16)
    plt.ylim(0, 100)  

    for index, value in enumerate(scores_percent):
        plt.text(index, value / 2, f'{value:.1f}%', ha='center', va='center', color='white', fontsize=12, fontweight='bold')

    plot_path = path.join(graphic_path, f"graphic_metrics_{formatted_time}.png")
    plt.savefig(plot_path)
    plt.close()


def plot_shap_summary(X_train, best_features, y_train, graphic_path, formatted_time):
    """
    Gera e salva o gráfico de resumo SHAP.

    Args:
    X_train (pd.DataFrame): Conjunto de treinamento para características.
    best_features (list): Melhor conjunto de características.
    y_train (pd.Series): Conjunto de treinamento para rótulos.
    graphic_path (str): Caminho onde o gráfico será salvo.
    formatted_time (str): Tempo formatado para nomear o arquivo.
    """
    X_train_selected = X_train[best_features]

    model_explanable = XGBClassifier(use_label_encoder=False, eval_metric="logloss")
    model_explanable.fit(X_train_selected, y_train)

    explainer = shap.TreeExplainer(model_explanable)
    shap_values = explainer.shap_values(X_train_selected)

    plt.figure()
    shap.summary_plot(shap_values, X_train_selected)
    plt.title(f"SHAP Summary plot of the best set")
    plot_path = path.join(graphic_path, f"graphic_summary_plot_{formatted_time}.png")
    plt.savefig(plot_path)
    plt.close()


def main(safe_path, attack_path, log_path, graphic_path, explanable, newdata_reduced):
    print('Iniciando a ferramenta IWSHAP')
    create_log_directory(log_path)
    formatted_time = get_current_time_in_brazil()
    log_file = path.join(log_path, f"Log_{formatted_time}.txt")
    
    with open(log_file, "w") as log:
        df = load_data(safe_path, attack_path)
        df = encode_categorical_features(df)
        X_train, X_test, y_train, y_test = split_data(df)
        
        model, f1, recall, precision = train_and_evaluate_model(X_train, y_train, X_test, y_test)
        log.write(f"Baseline: F1-Score={f1}, Recall={recall}, Precision={precision}\n")
        
        feature_importance_df = calculate_feature_importance(model, X_train)
        best_features, best_f1_score, best_recall, best_precision, best_round = evaluate_features(
            X_train, X_test, y_train, y_test, feature_importance_df, log
        )
        
        plot_metrics(graphic_path, formatted_time, best_f1_score, best_recall, best_precision, best_round)
        
        if explanable:
            plot_shap_summary(X_train, best_features, y_train, graphic_path, formatted_time)
        
        if newdata_reduced:
            save_best_features_dataset(df, best_features, formatted_time)
            
        log.write(f"Melhores features finais:\n {best_features}\n")
        log.write(f"Melhor F1 Score: {best_f1_score}\n")


    print('Processo finalizado!')
    print("Melhores features finais: ", best_features)
    print("Melhor F1 Score: ", best_f1_score)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ferramenta de seleção de features IWSHAP")
    parser.add_argument("--safe-path", "-s", required=True, type=str, help="Caminho para o arquivo de dados seguro")
    parser.add_argument("--attack-path", "-a", required=True, type=str, help="Caminho para o arquivo de dados de ataque")
    parser.add_argument("--log-path", "-l", type=str, help="Caminho para o arquivo de log", default="logs")
    parser.add_argument("--graphic-path", "-g", type=str, help="Caminho para os gráficos gerados", default="graphics")
    parser.add_argument("--explanable", "-x", action='store_true', help="Utilizada para definir a criação de um gráfico summary_plot com as características do melhor conjunto")
    parser.add_argument("--newdata-reduced", "-n", action='store_true', help="Utilizado para definir a criação de um novo dataset reduzido com as melhores características")
    
    args = parser.parse_args()
    main(args.safe_path, args.attack_path, args.log_path, args.graphic_path, args.explanable, args.newdata_reduced)
