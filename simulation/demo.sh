#!/bin/bash

# ========== 配置区 ==========
BASE_DIR="/home/bo/High-Precision-Congestion-Control"
SIM_DIR="$BASE_DIR/simulation/mix/demo"
RESULT_DIR="$BASE_DIR/result/Vary_CC/HPCC"
ALL_DEGREES=(8 12 16 20 24)

# ========== 参数解析 ==========
usage() {
    echo "用法: $0 [选项]"
    echo "选项:"
    echo "  -a, --all        运行所有算法（默认）"
    echo "  -d, --dcqcn      只运行DCQCN"
    echo "  -l, --ltfc       只运行LTFC"
    echo "  -i, --irn        只运行IRN"
    # echo "  -n, --nonpfc     只运行Non-PFC"
    echo "  -g, --degree N   只运行特定degree值(8/12/16/20/24)"
    echo "  -h, --help       显示帮助信息"
    exit 1
}

# 默认设置
RUN_DCQCN=true
RUN_LTFC=true
RUN_IRN=true
# RUN_NONPFC=true
SPECIFIC_DEGREE=false
SELECTED_DEGREE=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        -a|--all)
            RUN_DCQCN=true
            RUN_LTFC=true
            RUN_IRN=true
            # RUN_NONPFC=true
            shift
            ;;
        -d|--dcqcn)
            RUN_DCQCN=true
            RUN_LTFC=false
            RUN_IRN=false
            # RUN_NONPFC=false
            shift
            ;;
        -l|--ltfc)
            RUN_DCQCN=false
            RUN_LTFC=true
            RUN_IRN=false
            # RUN_NONPFC=false
            shift
            ;;
        -i|--irn)
            RUN_DCQCN=false
            RUN_LTFC=false
            RUN_IRN=true
            # RUN_NONPFC=false
            shift
            ;;
        # -n|--nonpfc)
        #     RUN_DCQCN=false
        #     RUN_LTFC=false
        #     RUN_IRN=false
        #     RUN_NONPFC=true
        #     shift
        #     ;;
        -g|--degree)
            if [[ -z "$2" ]]; then
                echo "错误: --degree 需要参数值" >&2
                usage
            fi
            if [[ " ${ALL_DEGREES[@]} " =~ " $2 " ]]; then
                SPECIFIC_DEGREE=true
                SELECTED_DEGREE=$2
                shift 2
            else
                echo "错误: 无效的degree值 '$2'，可选值为: ${ALL_DEGREES[*]}" >&2
                exit 1
            fi
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo "未知选项: $1"
            usage
            ;;
    esac
done

# ========== 初始化 ==========
mkdir -p "$RESULT_DIR"
> "$RESULT_DIR/dcqcn.log"  # 清理旧数据
> "$RESULT_DIR/ltfc.log"
> "$RESULT_DIR/irn.log"
# > "$RESULT_DIR/nonpfc.log"

# ========== 确定要运行的degree值 ==========
if $SPECIFIC_DEGREE; then
    degrees=($SELECTED_DEGREE)
else
    degrees=("${ALL_DEGREES[@]}")
fi

# ========== 流程控制 ==========
for DEGREE in "${degrees[@]}"; do
    echo "========================================"
    echo "正在处理 degree=${DEGREE} ..."
    
    echo "【1/5】生成流量模式..."
    if ! python3 "$SIM_DIR/gen_flow.py" -i $DEGREE; then
        echo "错误：流量模式生成失败" >&2
        exit 1
    fi

    # DCQCN测试
    if $RUN_DCQCN; then
        echo "【2/5】运行DCQCN测试..."
        nohup stdbuf -oL ./waf --run "scratch/third $SIM_DIR/DCQCN.txt" > "$RESULT_DIR/dcqcn.log" 2>&1 &
        wait $! || { echo "DCQCN测试失败"; exit 1; }
        python3 "$SIM_DIR/fct.py" "$SIM_DIR/fct.txt" -i $DEGREE -o "$RESULT_DIR/DCQCN_fct.txt" -s "$RESULT_DIR/dcqcn.log"
        python3 "$SIM_DIR/pfc.py" "$RESULT_DIR/dcqcn.log"

        echo "【2/5】跳过DCQCN测试..."
    fi

    # LTFC测试
    if $RUN_LTFC; then
        echo "【3/5】运行LTFC测试..."
        > "$BASE_DIR/result/Basic/ratio.txt"
        nohup stdbuf -oL ./waf --run "scratch/third $SIM_DIR/LTFC/DCQCN.txt" > "$RESULT_DIR/ltfc.log" 2>&1 &
        wait $! || { echo "LTFC测试失败"; exit 1; }
        python3 "$SIM_DIR/fct.py" "$SIM_DIR/fct.txt" -i $DEGREE -o "$RESULT_DIR/LTFC_fct.txt" -s "$RESULT_DIR/ltfc.log"
        python3 "$SIM_DIR/ratio.py" 
        python3 "$SIM_DIR/pfc.py" "$RESULT_DIR/ltfc.log"
    else
        echo "【3/5】跳过LTFC测试..."
    fi

    # IRN测试
    if $RUN_IRN; then
        echo "【4/5】运行IRN测试..."
        cd /home/bo/srnic-simulation-public/simulation
        nohup stdbuf -oL ./waf --run 'scratch/third mix/config.txt' > "$RESULT_DIR/irn.log" 2>&1 &
        wait $! || { echo "IRN测试失败"; exit 1; }
        cd -
        python3 "$SIM_DIR/fct.py" "$SIM_DIR/fct.txt" -i $DEGREE -o "$RESULT_DIR/IRN_fct.txt" -s "$RESULT_DIR/irn.log"
    else
        echo "【4/5】跳过IRN测试..."
    fi

    # Non-PFC测试
    # if $RUN_NONPFC; then
    #     echo "【5/5】运行non-PFC测试..."
    #     nohup stdbuf -oL ./waf --run "scratch/third $SIM_DIR/motivation/config_drop.txt" > "$RESULT_DIR/nonpfc.log" 2>&1 &
    #     wait $! || { echo "Non-PFC测试失败"; exit 1; }
    #     python3 "$SIM_DIR/fct.py" "$SIM_DIR/fct.txt" -i $DEGREE -o "$RESULT_DIR/NonPFC_fct.txt" -s "$RESULT_DIR/nonpfc.log"
    # else
    #     echo "【5/5】跳过non-PFC测试..."
    # fi

    echo "degree=${DEGREE} 测试完成！结果保存在 $RESULT_DIR"
    echo "========================================"
    echo
done

echo "所有测试完成！"