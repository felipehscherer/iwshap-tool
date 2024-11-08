#!/bin/bash

printline() {
	echo "==========================================================="
}

printline
echo -n "Verificando Python 3.12.3... "

VERSION=$(python3 -V | awk '{print $2}')
if [ "$VERSION" != "3.12.3" ]
then
	echo "ERRO."
	echo "    (1) Voce precisa do python 3.12.3 para rodar o IWSHAP!"
	echo "    (2) Por favor, instale Python 3.12.3 ou use a demo Docker(run_demo_docker.sh)."
	printline
	exit
fi

echo "done."
printline

printline
echo -n "Instalando as dependencias do Python.. "

pip install -r requirements.txt  > /dev/null 2>&1

echo "Pronto."
printline

echo ""

printline
echo "Executando o IWSHAP.py.. "
echo ""

python3 IWSHAP.py -s dataset/safe_dataset.csv -a dataset/attack_dataset_fabr.csv -x -n

echo ""
echo "Pronto."
printline