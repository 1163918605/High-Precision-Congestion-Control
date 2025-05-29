#!/bin/bash

# 定义路径变量和文件名
NAME="new-DCQCN"
ALL_PATH="/home/bo/High-Precision-Congestion-Control"

# 执行 waf 命令
./waf --run 'scratch/third mix/demo/DCQCN.txt'

python3 fct.py "/home/bo/High-Precision-Congestion-Control/simulation/mix/demo/fct.txt"

# echo " PFC DCQCN simulation finish"

# ./waf --run 'scratch/third mix/demo/HPCC.txt' > result/PFC/HPCC/output6.txt

# python3 fct.py "/home/bo/High-Precision-Congestion-Control/simulation/mix/demo/fct.txt" >> result/PFC/HPCC/result.txt

# echo " PFC HPCC simulation finish"

# ./waf --run 'scratch/third mix/demo/TIMELY.txt' > result/PFC/Timely/output6.txt

# python3 fct.py "/home/bo/High-Precision-Congestion-Control/simulation/mix/demo/fct.txt" >> result/PFC/Timely/result.txt

# echo " PFC Timely simulation finish"

# ./waf --run 'scratch/third mix/demo/LTFC/DCQCN.txt' > result/LTFC/DCQCN/output6.txt

# python3 fct.py "/home/bo/High-Precision-Congestion-Control/simulation/mix/demo/fct.txt" >> result/LTFC/DCQCN/result.txt

# echo " DCQCN simulation finish"

# ./waf --run 'scratch/third mix/demo/LTFC/HPCC.txt' > result/LTFC/HPCC/output6.txt

# python3 fct.py "/home/bo/High-Precision-Congestion-Control/simulation/mix/demo/fct.txt" >> result/LTFC/HPCC/result.txt

# echo " HPCC simulation finish"

# ./waf --run 'scratch/third mix/demo/LTFC/TIMELY.txt' > result/LTFC/Timely/output6.txt

# python3 fct.py "/home/bo/High-Precision-Congestion-Control/simulation/mix/demo/fct.txt" >> result/LTFC/Timely/result.txt

# echo " Timely simulation finish"

# 切换到分析目录
# cd "$ALL_PATH/analysis" || { echo "Failed to enter directory: $ALL_PATH/analysis"; exit 1; }

# # 执行 trace_reader 命令，将输出重定向到指定文件
# ./trace_reader $ALL_PATH/simulation/mix/demo/mix.tr > "demo/${NAME}.txt"

# echo "finshi0"

# # 切换到 throughput 目录
# cd throughput || { echo "Failed to enter directory: $ALL_PATH/analysis/throughput"; exit 1; }

# # 运行 Python 脚本处理数据
# python3 throughput.py "../demo/${NAME}.txt" "${NAME}.png" --node_id 2 --window_size_ns 1000

# echo "finshi1"

# cd "$ALL_PATH/analysis/queue" || { echo "Failed to enter directory: $ALL_PATH/analysis/queue"; exit 1; }

# # 运行 Python 脚本处理数据
# python3 queue.py "../demo/${NAME}.txt" "${NAME}.png" --node_id 16

# echo "finshi2"
