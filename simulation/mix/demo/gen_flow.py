import random

# 24 48 72 96 
num_ps = 4
num_job = 1

flow_size = int(26500000 / num_ps)
# flow_size = 26500000
fixed_data = f"3 100 {flow_size} 2"  
dst_list = []
src_list = []

num_workers  = num_ps * 4
num_flows = num_ps * num_workers * num_job 
nodes = num_ps + num_workers

with open("demo_flow.txt", "w") as file:
    file.write(f"{num_flows}\n")
    random_numbers = random.sample(range(144), nodes)
    src_list = random_numbers[num_ps:]
    dst_list = random_numbers[:num_ps]

    print(dst_list)
    print(src_list)
    for src in src_list:
        for dst in dst_list:
            file.write(f"{src} {dst} {fixed_data}\n")


print("workflow generates successfully: demo_flow.txt")
