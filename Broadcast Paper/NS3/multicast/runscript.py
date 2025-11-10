import subprocess
import re
import matplotlib.pyplot as plt

# List of station counts from 1 to 64.
stations_list = list(range(1, 65,5))
throughputs = []

for num in stations_list:
    # Construct the command line. Adjust the simulation name if necessary.
    cmd = f"./ns3 run \"scratch/unicastperuserthroughput --numStations={num}\""
    print(f"Running simulation with numStations = {num}")
    
    # Run the simulation.
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    output = stdout.decode("utf-8")
    
    # Optionally print the simulation output for debugging.
    print(output)
    
    # Parse the average throughput per user from the output.
    # Expected output line: "Average UDP unicast throughput per user: X Mbps"
    match = re.search(r"Average UDP unicast throughput per user:\s*([0-9.]+)\s*Mbps", output)
    if match:
        avg_throughput = float(match.group(1))
    else:
        avg_throughput = 0.0
        print("Warning: Could not parse throughput for numStations =", num)
    
    throughputs.append(avg_throughput)
    print(f"numStations: {num} -> Average throughput per user: {avg_throughput} Mbps\n")

# Plot the results.
plt.figure(figsize=(10, 6))
plt.plot(stations_list, throughputs, marker='o', linestyle='-', color='b')
plt.xlabel('Number of Stations')
plt.ylabel('Average Throughput per User (Mbps)')
plt.title('Average Throughput per User vs. Number of Stations')
plt.grid(True)
plt.show()
