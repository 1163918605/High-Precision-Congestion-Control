import random
import argparse

def generate_flow(num_workers, total_traffic=102230000, node_range=144, rack_size=16):
    num_job = 1
    num_ps = max(1, int(num_workers / 4))  # 至少1个PS
    
    # 检查PS数量是否超过机架总数
    max_racks = node_range // rack_size
    if num_ps > max_racks:
        raise ValueError(f"PS数量 {num_ps} 超过最大机架数 {max_racks}")

    # 动态流量分配
    flow_size = int(total_traffic / (num_ps))
    fixed_data = f"3 100 {flow_size} 2"

    # 为每个PS选择一个不同的机架
    rack_ids = random.sample(range(max_racks), num_ps)  # 随机选择不重复的机架ID
    ps_nodes = []
    for rack in rack_ids:
        # 从当前机架中随机选一个节点作为PS
        start = rack * rack_size
        end = start + rack_size - 1
        ps_nodes.append(random.randint(start, end))

    # 为Worker随机选择剩余节点（不能与PS同机架）
    worker_nodes = []
    available_racks = set(range(max_racks)) - set(rack_ids)  # 剩余机架
    for _ in range(num_workers):
        rack = random.choice(list(available_racks))
        start = rack * rack_size
        end = start + rack_size - 1
        worker_nodes.append(random.randint(start, end))

    # 写入文件
    with open("/home/bo/High-Precision-Congestion-Control/simulation/mix/demo/demo_flow.txt", "w") as file:
        file.write(f"{num_ps * num_workers * num_job}\n")
        for src in worker_nodes:
            for dst in ps_nodes:
                file.write(f"{src} {dst} {fixed_data}\n")

    print(ps_nodes)
    print(worker_nodes)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', type=int, required=True, help="Number of worker nodes")
    parser.add_argument('--traffic', type=int, default=26500000, help="Total traffic in bytes")
    args = parser.parse_args()
    generate_flow(args.i, args.traffic)