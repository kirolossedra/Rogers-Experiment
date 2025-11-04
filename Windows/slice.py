import os
import re
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# ----------------------------------------------------------------------
# 1. PARSE LOG → (timestamp, state, filename)
# ----------------------------------------------------------------------
def parse_log_file(filepath):
    data = []
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    sections = content.split('/////')
    print(f"  Sections: {len(sections)}")

    current_time = None
    for section in sections:
        # Timestamp
        m = re.search(r'LocalBeginTime:\s*\d+\s*\(([^)]+)\)', section)
        if m:
            ts_str = m.group(1).split('.')[0]
            try:
                current_time = datetime.strptime(ts_str, '%Y-%m-%dT%H:%M:%S')
            except:
                current_time = None

        # Client present?
        state = 1 if '192.168.0.220' in section else 0

        if current_time:
            data.append((current_time, state, filepath))

    print(f"  Raw points: {len(data)}")
    return data


# ----------------------------------------------------------------------
# 2. DEDUPLICATE: one row per second per file → OR rule (any 1 → 1)
# ----------------------------------------------------------------------
def dedup_per_file(raw_data):
    groups = {}
    for dt, state, fname in raw_data:
        key = (fname, dt.replace(microsecond=0))  # truncate to second
        groups.setdefault(key, []).append(state)

    cleaned = []
    for (fname, dt_sec), states in groups.items():
        final_state = 1 if any(s == 1 for s in states) else 0
        cleaned.append((dt_sec, final_state, fname))
    return cleaned


# ----------------------------------------------------------------------
# 3. SCAN + DEDUP + PLOT (NO CSV)
# ----------------------------------------------------------------------
def scan_and_plot():
    raw_data = {}
    files_checked = []

    # Find files
    txt_files = [f for f in os.listdir('.') if f.lower().endswith(('.txt', '.log'))]
    print(f"Found {len(txt_files)} files:")
    for f in txt_files: print(f"  - {f}")
    print()

    # Parse
    for f in txt_files:
        files_checked.append(f)
        print(f"Parsing: {f}")
        try:
            pts = parse_log_file(f)
            if pts:
                raw_data[f] = pts
        except Exception as e:
            print(f"  Error: {e}")

    if not raw_data:
        print("\nNO DATA FOUND")
        return

    # Deduplicate per file
    file_data = {}
    for fname, pts in raw_data.items():
        cleaned = dedup_per_file(pts)
        file_data[fname] = cleaned
        print(f"  {fname}: {len(pts)} → {len(cleaned)} unique seconds")

    # Time slices
    time_slices = [
        ("14:42:58", "14:44:47"),
        ("14:50:01", "14:51:46"),
        ("14:54:28", "14:56:22")
    ]

    # Plot each slice
    for slice_idx, (s_str, e_str) in enumerate(time_slices, 1):
        fig, ax = plt.subplots(figsize=(14, 6))
        colors = ['blue', 'purple', 'green', 'red', 'orange', 'brown', 'pink', 'gray']

        sh, sm, ss = map(int, s_str.split(':'))
        eh, em, es = map(int, e_str.split(':'))
        start_sec = sh*3600 + sm*60 + ss
        end_sec   = eh*3600 + em*60 + es

        has_data = False
        all_ts, all_st = [], []
        ref_date = None

        for idx, (fname, pts) in enumerate(file_data.items()):
            pts = sorted(pts, key=lambda x: x[0])
            if not ref_date and pts:
                ref_date = pts[0][0].date()

            # Filter slice
            filtered = [(dt, st) for dt, st, _ in pts
                        if start_sec <= (dt.hour*3600 + dt.minute*60 + dt.second) <= end_sec]

            if not filtered:
                continue

            has_data = True
            ts_list = [t for t, s in filtered]
            st_list = [s for t, s in filtered]
            all_ts.extend(ts_list)
            all_st.extend(st_list)

            color = colors[idx % len(colors)]

            # Build step: hold → jump
            step_x, step_y = [], []
            if ts_list:
                step_x.append(ts_list[0])
                step_y.append(st_list[0])

                for i in range(1, len(ts_list)):
                    prev_t, prev_s = ts_list[i-1], st_list[i-1]
                    curr_t, curr_s = ts_list[i],   st_list[i]
                    step_x.extend([curr_t, curr_t])
                    step_y.extend([prev_s, curr_s])

                # Extend to end
                if ref_date:
                    end_dt = datetime.combine(ref_date, datetime.min.time())
                    end_dt = end_dt.replace(hour=eh, minute=em, second=es)
                    if ts_list[-1] < end_dt:
                        step_x.append(end_dt)
                        step_y.append(st_list[-1])

            ax.plot(step_x, step_y, drawstyle='steps-post', linewidth=2.5,
                    color=color, label=fname, alpha=0.9)
            ax.scatter(ts_list, st_list, color=color, s=45, zorder=5,
                       edgecolors='black', linewidth=0.6)

        if not has_data:
            print(f"\nSlice {slice_idx} ({s_str}–{e_str}): no data")
            plt.close(fig)
            continue

        # Format
        ax.set_xlabel('Time', fontsize=12, fontweight='bold')
        ax.set_ylabel('Client 192.168.0.220', fontsize=12, fontweight='bold')
        ax.set_title(f'Connection Status – Slice {slice_idx} ({s_str}–{e_str})',
                     fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.legend(loc='upper left', fontsize=9)
        ax.set_ylim(-0.1, 1.1)
        ax.set_yticks([0, 1])
        ax.set_yticklabels(['Disconnected', 'Connected'])
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        # Save
        png = f'client_timeline_slice_{slice_idx}.png'
        plt.savefig(png, dpi=150, bbox_inches='tight')
        print(f"\nSlice {slice_idx} → {png}")
        print(f"  Points: {len(all_ts)} | Connected: {sum(all_st)}/{len(all_st)}")

    # Summary
    print("\n" + "="*50)
    print("SUMMARY")
    print(f"Files checked: {len(files_checked)}")
    print(f"Files w/ data: {len(file_data)}")
    total_clean = sum(len(d) for d in file_data.values())
    print(f"Total unique seconds: {total_clean}")
    for f in file_data:
        print(f"  {f}: {len(file_data[f])}")
    print("="*50)

    plt.show()


if __name__ == "__main__":
    scan_and_plot()