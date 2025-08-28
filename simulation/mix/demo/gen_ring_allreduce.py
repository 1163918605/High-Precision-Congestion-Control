import random
import argparse

def generate_multi_job_ring_flows(num_jobs, nodes_per_job, flow_size=1000000, node_range=144):
    """
    num_jobs: 任务数（每个任务一个 Ring All-Reduce）
    nodes_per_job: 每个任务包含的节点数量
    flow_size: 每条流大小（字节）
    node_range: 可选节点编号范围（默认 0~143）
    """

    total_required_nodes = num_jobs * nodes_per_job
    if total_required_nodes > node_range:
        raise ValueError(f"需要节点总数 {total_required_nodes} 超出可用范围 {node_range}")

    # 全部随机选取，确保节点不重复
    all_selected_nodes = random.sample(range(node_range), total_required_nodes)

    fixed_data = f"3 100 {flow_size} 2"
    flows = []

    for job_id in range(num_jobs):
        start_idx = job_id * nodes_per_job
        end_idx = start_idx + nodes_per_job
        job_nodes = all_selected_nodes[start_idx:end_idx]

        print(f"[INFO] Job {job_id}: 节点列表 = {job_nodes}")

        for i in range(nodes_per_job):
            src = job_nodes[i]
            dst = job_nodes[(i + 1) % nodes_per_job]
            flows.append(f"{src} {dst} {fixed_data}")

    # 写入文件
    out_path = "/home/bo/High-Precision-Congestion-Control/simulation/mix/demo/demo_flow.txt"
    with open(out_path, "w") as file:
        file.write(f"{len(flows)}\n")
        for line in flows:
            file.write(line + "\n")

    print(f"[INFO] 成功为 {num_jobs} 个任务生成 {len(flows)} 条 Ring All-Reduce 流。")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-j', type=int, required=True, help="任务数量（jobs）")
    parser.add_argument('-n', type=int, required=True, help="每个任务的节点数量")
    parser.add_argument('--flow_size', type=int, default=1000000, help="每流大小（默认1MB）")
    parser.add_argument('--range', type=int, default=144, help="节点编号范围（默认0~143）")
    args = parser.parse_args()

    generate_multi_job_ring_flows(args.j, args.n, args.flow_size, args.range)
