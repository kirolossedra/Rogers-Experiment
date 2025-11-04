import os
import re
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def parse_log_file(filepath):
    """Parse a log file and extract timestamp and number of clients."""
    data = []
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Split by the delimiter
    sections = content.split('/////')
    
    print(f"  Total sections found: {len(sections)}")
    
    # Process sections - look for time in current section and client count in next sections
    current_time = None
    current_time_str = None
    
    for i, section in enumerate(sections):
        # Look for LocalBeginTime
        time_match = re.search(r'LocalBeginTime:\s*(\d+)\s*\(([^)]+)\)', section)
        
        if time_match:
            time_str = time_match.group(2)
            try:
                # Parse the timestamp - Format: 2025-10-24T11:32:14.662-0400
                time_clean = time_str.split('.')[0]
                current_time = datetime.strptime(time_clean, '%Y-%m-%dT%H:%M:%S')
                current_time_str = time_str
            except Exception as e:
                print(f"  Warning: couldn't parse timestamp '{time_str}': {e}")
                current_time = None
        
        # Look for client count - can be in same section or following sections
        clients_match = re.search(r'(?:Number of Clients|Num of associated clients)\s*:\s*(\d+)', section)
        
        if clients_match and current_time:
            num_clients = int(clients_match.group(1))
            data.append((current_time, num_clients, filepath))  # Include filename
            # Keep the current time for potential multiple client counts
    
    print(f"  Successfully parsed {len(data)} data points")
    return data

def scan_and_plot():
    """Scan current directory for text files and plot client connections."""
    file_data = {}  # Dictionary to store data per file
    files_checked = []
    
    # Find all text files in current directory
    txt_files = [f for f in os.listdir('.') if f.endswith('.txt') or f.endswith('.log')]
    
    print(f"Found {len(txt_files)} log/txt files in current directory:")
    for filename in txt_files:
        print(f"  - {filename}")
    print()
    
    for filename in txt_files:
        files_checked.append(filename)
        print(f"Checking: {filename}")
        try:
            data = parse_log_file(filename)
            if data:
                file_data[filename] = data
            else:
                print(f"  ✗ No valid data found")
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    if not file_data:
        print("\n" + "="*50)
        print("NO DATA FOUND!")
        print(f"Checked {len(files_checked)} files, none had parseable data")
        print("="*50)
        return
    
    # Define time slices (time only, will match any date)
    time_slices = [
        ("14:42:58", "14:44:47"),
        ("14:50:01", "14:51:46"),
        ("14:54:28", "14:56:22")
    ]
    
    # Create 4 separate plots
    for slice_idx, (start_time_str, end_time_str) in enumerate(time_slices, 1):
        fig, ax = plt.subplots(figsize=(14, 6))
        
        # Colors for different files
        colors = ['blue', 'purple', 'green', 'red', 'orange', 'brown', 'pink', 'gray']
        
        slice_timestamps = []
        slice_client_counts = []
        has_data_in_slice = False
        
        # Parse time bounds (use a reference date, we'll only compare times)
        start_h, start_m, start_s = map(int, start_time_str.split(':'))
        end_h, end_m, end_s = map(int, end_time_str.split(':'))
        
        # Plot each file separately, filtering by time slice
        for idx, (filename, data) in enumerate(file_data.items()):
            # Sort by timestamp
            data.sort(key=lambda x: x[0])
            
            # Filter data for this time slice
            filtered_data = []
            for timestamp, client_count, fname in data:
                t_hour = timestamp.hour
                t_minute = timestamp.minute
                t_second = timestamp.second
                
                # Convert to total seconds for easier comparison
                t_total = t_hour * 3600 + t_minute * 60 + t_second
                start_total = start_h * 3600 + start_m * 60 + start_s
                end_total = end_h * 3600 + end_m * 60 + end_s
                
                if start_total <= t_total <= end_total:
                    filtered_data.append((timestamp, client_count))
            
            if not filtered_data:
                continue
            
            has_data_in_slice = True
            
            # Extract timestamps and client counts
            timestamps = [d[0] for d in filtered_data]
            client_counts = [d[1] for d in filtered_data]
            
            slice_timestamps.extend(timestamps)
            slice_client_counts.extend(client_counts)
            
            color = colors[idx % len(colors)]
            
            # Plot as step function
            ax.step(timestamps, client_counts, where='post', linewidth=2, 
                    color=color, label=filename, alpha=0.8)
            ax.scatter(timestamps, client_counts, color=color, s=30, alpha=0.6, zorder=5)
        
        if not has_data_in_slice:
            print(f"\nSlice {slice_idx} ({start_time_str} to {end_time_str}): No data found")
            plt.close(fig)
            continue
        
        # Formatting
        ax.set_xlabel('Time', fontsize=12, fontweight='bold')
        ax.set_ylabel('Number of Clients', fontsize=12, fontweight='bold')
        ax.set_title(f'Client Connection Timeline - Slice {slice_idx} ({start_time_str} to {end_time_str})', 
                     fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.legend(loc='upper left', fontsize=9)
        
        # Set y-axis limits with some padding
        if slice_client_counts:
            ax.set_ylim(-0.1, max(slice_client_counts) + 0.5)
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        plt.xticks(rotation=45, ha='right')
        
        plt.tight_layout()
        
        # Save the plot
        output_file = f'client_timeline_slice_{slice_idx}.png'
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        print(f"\nSlice {slice_idx} plot saved as: {output_file}")
        print(f"  Time range: {start_time_str} to {end_time_str}")
        print(f"  Data points: {len(slice_timestamps)}")
        if slice_client_counts:
            print(f"  Client count range: {min(slice_client_counts)} to {max(slice_client_counts)}")
    
    # Show summary
    print(f"\n{'='*50}")
    print(f"Summary:")
    print(f"  Files checked: {len(files_checked)}")
    print(f"  Files with data: {len(file_data)}")
    total_points = sum(len(data) for data in file_data.values())
    print(f"  Total data points: {total_points}")
    for filename, data in file_data.items():
        print(f"    {filename}: {len(data)} points")
    print(f"{'='*50}")
    
    plt.show()

if __name__ == "__main__":
    scan_and_plot()