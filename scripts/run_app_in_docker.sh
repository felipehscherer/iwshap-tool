#!/bin/bash

echo "Executando o IWSHAP.."
echo ""

python3 IWSHAP.py -s your_dataset -a your_dataset -x -n

echo "Processo finalizado!"

echo "==========================================================="
ls graphics/
echo "==========================================================="
ls logs/
echo "==========================================================="
ls reduced_data/
echo "==========================================================="

bash 