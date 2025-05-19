import argparse

def generate_topology():
    parser = argparse.ArgumentParser(description='Generate leaf-spine topology for NS3')
    parser.add_argument('--cores', type=int,  help='Number of core (spine) switches', default=4)
    parser.add_argument('--tors', type=int, help='Number of ToR (leaf) switches', default=9)
    parser.add_argument('--hosts_per_tor', type=int, help='Hosts per ToR switch', default=16)
    parser.add_argument('--links_per_tor_spine', type=int, default=1, help='Links per ToR-spine connection')
    parser.add_argument('--host_tor_rate', default='100Gbps', help='Host-ToR link rate')
    parser.add_argument('--host_tor_delay', default='1000ns', help='Host-ToR link delay')
    parser.add_argument('--tor_spine_rate', default='100Gbps', help='ToR-Spine link rate')
    parser.add_argument('--tor_spine_delay', default='1000ns', help='ToR-Spine link delay')
    parser.add_argument('--error_rate', type=float, default=0.000000, help='Link error rate')
    parser.add_argument('output_file', help='Output file path', default='topology.txt')

    args = parser.parse_args()

    # Calculate node parameters
    S, T, H, L = args.cores, args.tors, args.hosts_per_tor, args.links_per_tor_spine
    total_hosts = T * H
    total_switches = S + T
    total_nodes = total_hosts + T + S  # Hosts + ToRs + Spines
    total_links = T * H + T * S * L

    # New ID allocation order: Hosts -> ToRs -> Spines
    # Host IDs: 0 to (total_hosts - 1)
    # ToR IDs: total_hosts to (total_hosts + T - 1)
    # Spine IDs: (total_hosts + T) to (total_hosts + T + S - 1)
    tor_start_id = total_hosts
    spine_start_id = total_hosts + T

    # Generate switch IDs (ToRs first, then Spines)
    switch_ids = list(range(tor_start_id, spine_start_id)) + list(range(spine_start_id, spine_start_id + S))

    # Write topology file
    with open(args.output_file, 'w') as f:
        # Header line
        f.write(f"{total_nodes} {total_switches} {total_links}\n")
        
        # Switch IDs line (ToRs + Spines)
        f.write(' '.join(map(str, switch_ids)) + '\n')
        
        # Host-ToR connections (host_id tor_id ...)
        for tor_idx in range(T):
            tor_id = tor_start_id + tor_idx
            host_start = tor_idx * H  # Host IDs start from 0
            for h in range(H):
                host_id = host_start + h
                f.write(f"{host_id} {tor_id} {args.host_tor_rate} {args.host_tor_delay} {args.error_rate}\n")
        
        # ToR-Spine connections (tor_id spine_id ...)
        for tor_idx in range(T):
            tor_id = tor_start_id + tor_idx
            for spine_idx in range(S):
                spine_id = spine_start_id + spine_idx
                for _ in range(L):
                    f.write(f"{tor_id} {spine_id} {args.tor_spine_rate} {args.tor_spine_delay} {args.error_rate}\n")

if __name__ == '__main__':
    generate_topology()