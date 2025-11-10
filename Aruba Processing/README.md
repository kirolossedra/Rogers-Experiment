
# Aruba Log Analysis System

Each one of these HTML files is specialized to work with certain files related to **Aruba logs**.

The **main Aruba logs** are collected from **two Access Points (APs)**.
The **slicing of the large Aruba log** is done using either **iPerf logs** or **latency logs**, based on their **timestamps** as seen below.

These slicing scripts are located in the following directory:

```
/Linux
```

From the **root directory**, the folder hierarchy looks like this:

```
/
├── Linux/
│   ├── iperf.py
│   ├── ping.py
│   └── ...
├── Aruba Processing/
│   ├── iperf.html
│   ├── latency.html
│   └── ...
└── README.md
```

---

## 📈 Sample from iPerf3 Logs

These logs show throughput (bandwidth) over time in megabytes and megabits per second.

```
Mon Oct 27 14:43:07 2025 [  6]   8.02-9.01   sec  62.9 MBytes   531 Mbits/sec
Mon Oct 27 14:43:08 2025 [  6]   9.01-10.01  sec  43.5 MBytes   363 Mbits/sec
Mon Oct 27 14:43:09 2025 [  6]  10.01-11.00  sec  51.4 MBytes   436 Mbits/sec
Mon Oct 27 14:43:10 2025 [  6]  11.00-12.01  sec  47.2 MBytes   394 Mbits/sec
Mon Oct 27 14:43:11 2025 [  6]  12.01-13.01  sec  44.9 MBytes   375 Mbits/sec
Mon Oct 27 14:43:12 2025 [  6]  13.01-14.02  sec  39.4 MBytes   329 Mbits/sec
Mon Oct 27 14:43:13 2025 [  6]  14.02-15.01  sec  20.6 MBytes   175 Mbits/sec
Mon Oct 27 14:43:14 2025 [  6]  15.01-16.01  sec  26.6 MBytes   222 Mbits/sec
Mon Oct 27 14:43:15 2025 [  6]  16.01-17.02  sec  25.5 MBytes   213 Mbits/sec
Mon Oct 27 14:43:16 2025 [  6]  17.02-18.01  sec  24.1 MBytes   204 Mbits/sec
Mon Oct 27 14:43:17 2025 [  6]  18.01-19.01  sec  20.4 MBytes   170 Mbits/sec
Mon Oct 27 14:43:18 2025 [  6]  19.01-20.00  sec  19.5 MBytes   165 Mbits/sec
```

---

## 🕒 Sample from Latency Logs

These logs show ICMP (ping) response times for a specific IP, along with timestamp, round-trip time, and TTL.

```
2025-10-27 14:43:05 Reply from 192.168.0.227: bytes=32 time=37ms TTL=128
2025-10-27 14:43:06 Reply from 192.168.0.227: bytes=32 time=34ms TTL=128
2025-10-27 14:43:07 Reply from 192.168.0.227: bytes=32 time=15ms TTL=128
2025-10-27 14:43:08 Reply from 192.168.0.227: bytes=32 time=55ms TTL=128
2025-10-27 14:43:09 Reply from 192.168.0.227: bytes=32 time=57ms TTL=128
2025-10-27 14:43:10 Reply from 192.168.0.227: bytes=32 time=15ms TTL=128
2025-10-27 14:43:11 Reply from 192.168.0.227: bytes=32 time=33ms TTL=128
2025-10-27 14:43:12 Reply from 192.168.0.227: bytes=32 time=183ms TTL=128
2025-10-27 14:43:13 Reply from 192.168.0.227: bytes=32 time=32ms TTL=128
2025-10-27 14:43:14 Reply from 192.168.0.227: bytes=32 time=115ms TTL=128
2025-10-27 14:43:15 Reply from 192.168.0.227: bytes=32 time=83ms TTL=128
2025-10-27 14:43:16 Reply from 192.168.0.227: bytes=32 time=61ms TTL=128
2025-10-27 14:43:17 Reply from 192.168.0.227: bytes=32 time=184ms TTL=128
2025-10-27 14:43:18 Reply from 192.168.0.227: bytes=32 time=129ms TTL=128
2025-10-27 14:43:19 Reply from 192.168.0.227: bytes=32 time=103ms TTL=128
```

---

## 🧠 Summary

* Each HTML file corresponds to a specific analysis mode (e.g., iPerf-based or latency-based slicing).
* Slicing is synchronized using **timestamps** extracted from iPerf or latency logs.
* The sliced Aruba logs are then used for visual analysis and correlation across both APs.

---

