import random
import argparse
# 24 48 72 96 
def generate_flow(i):
    num_workers = int(i)
    num_job = 1
    num_ps  = int(num_workers / 4)
    
    # num_ps = 1
    # num_job = 1
    # num_workers = int(num_ps*i)
    
    
    # flow_size = int(26500000 / num_ps)
    flow_size = 4000000
    fixed_data = f"3 100 {flow_size} 2"  
    dst_list = []
    src_list = []

    num_flows = num_ps * num_workers * num_job 
    nodes = num_ps + num_workers

    with open("/home/bo/High-Precision-Congestion-Control/simulation/mix/demo/demo_flow.txt", "w") as file:
        file.write(f"{num_flows}\n")
        random_numbers = random.sample(range(143), nodes)
        src_list = random_numbers[num_ps:]
        dst_list = random_numbers[:num_ps]

        print(dst_list)
        print(src_list)
        for src in src_list:
            for dst in dst_list:
                file.write(f"{src} {dst} {fixed_data}\n")


    print("workflow generates successfully: demo_flow.txt")
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate and plot throughput from log file.")
    parser.add_argument('-i', type=int, default=2, help="Node to calculate throughput for (default: 2)")
    args = parser.parse_args()
    generate_flow(args.i)