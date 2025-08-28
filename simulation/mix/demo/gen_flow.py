import argparse
import random

def generate_flow(num_workers, total_traffic=25600000, node_range=144, rack_size=9):
    max_racks = node_range // rack_size
    total_flows = 0
    all_lines = []
    num_job= 2500
    
    for job_id in range(num_job):
        num_ps = max(1, int(num_workers / 4))  # 每个任务至少1个PS

        # 为当前任务选择PS的机架
        rack_ids_ps = random.sample(range(max_racks), num_ps)
        ps_nodes = []
        for rack in rack_ids_ps:
            start = rack * rack_size
            end = start + rack_size - 1
            ps_nodes.append(random.randint(start, end))

        # 为当前任务选择Worker（不能与PS同机架）
        available_racks = set(range(max_racks)) - set(rack_ids_ps)
        if len(available_racks) == 0:
            raise ValueError("没有足够的可用机架分配给Worker")

        worker_nodes = []
        for _ in range(num_workers):
            rack = random.choice(list(available_racks))
            start = rack * rack_size
            end = start + rack_size - 1
            worker_nodes.append(random.randint(start, end))

        # 流量均分给每个PS流
        flow_size = int(total_traffic / (num_job * num_ps))
        fixed_data = f"3 100 {flow_size} 2"

        # 构建当前任务的所有流
        for src in worker_nodes:
            for dst in ps_nodes:
                all_lines.append(f"{src} {dst} {fixed_data}")
                total_flows += 1

        print(f"Job {job_id}:")
        print(f"  PS: {ps_nodes}")
        print(f"  Worker: {worker_nodes}")

    # 写入文件
    with open("/home/bo/High-Precision-Congestion-Control/simulation/mix/demo/demo_flow.txt", "w") as file:
        file.write(f"{total_flows}\n")
        for line in all_lines:
            file.write(f"{line}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', type=int, required=True, help="Number of worker nodes per job")
    parser.add_argument('--traffic', type=int, default=26500000, help="Total traffic in bytes")
    # parser.add_argument('--job', type=int, default=1, help="Number of jobs to simulate")
    args = parser.parse_args()
    generate_flow(num_workers=args.i, total_traffic=args.traffic)
