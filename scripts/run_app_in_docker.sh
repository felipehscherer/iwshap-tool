#!/bin/bash

echo "Executando o IWSHAP.."
echo ""

python3 IWSHAP.py -s dataset/safe_dataset.csv -a dataset/attack_dataset_fabr.csv -x -n

echo "Processo finalizado!"

echo "==========================================================="
ls graphics/
echo "==========================================================="
ls logs/
echo "==========================================================="
ls reduced_data/
echo "==========================================================="

bash 