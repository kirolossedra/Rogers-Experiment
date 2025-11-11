
---

# QConnectManager Modem Interface for Linux

This repository provides instructions and guidance for interfacing Quectel 4G/5G modems on Linux using **QConnectManager**. It covers setup, building the driver, connecting to the modem, testing connectivity, and using AT commands.

---

## Table of Contents

* [Prerequisites](#prerequisites)
* [Stopping ModemManager](#stopping-modemmanager)
* [Cloning the Repository](#cloning-the-repository)
* [Building QConnectManager](#building-qconnectmanager)
* [Running QConnectManager](#running-qconnectmanager)
* [Testing Network Connectivity](#testing-network-connectivity)
* [Using AT Commands](#using-at-commands)
* [Understanding AT Command Output](#understanding-at-command-output)

---

## Prerequisites

* Linux system (tested on Ubuntu)
* USB-C connected Quectel modem (ensure connected to USB 3.0 port, **not the USB-to-UART port**)
* `sudo` privileges

Optional utilities:

```bash
sudo apt install minicom iperf3
```

---

## Stopping ModemManager

The default Linux `ModemManager` may interfere with direct modem communication. Temporarily stop it:

```bash
sudo systemctl stop ModemManager      # stops ModemManager for current session
systemctl status ModemManager         # verify it is stopped
```

> **Note:** ModemManager will restart on the next system reboot.

---

## Cloning the Repository

Clone the driver repository (requires UWaterloo credentials):

```bash
git clone https://git.uwaterloo.ca/robohub/connected_robotics/qconnectmanager.git
cd qconnectmanager
```

---

## Building QConnectManager

Build the driver:

```bash
cd ~/Research/Rogers/5G/qconnectmanager
make
```

> **Tip:** If you encounter compilation errors, modify the `Makefile` to **change `-Werror` to warnings** in the `CFLAGS` section. This allows compilation to continue despite non-critical warnings.

---

## Running QConnectManager

Run as root due to permissions:

```bash
sudo ./quectel-CM -4 -6
```

Sample output log:

```
[11-10_13:49:29:039] QConnectManager_Linux_V1.6.5
[11-10_13:49:29:040] Auto find qmichannel = /dev/cdc-wdm3
[11-10_13:49:29:040] Auto find usbnet_adapter = wwan0
[11-10_13:49:29:040] netcard driver = qmi_wwan, driver version = 6.14.0-34-generic
[11-10_13:49:29:040] Modem works in QMI mode
[11-10_13:49:31:846] requestRegistrationState2 MCC: 302, MNC: 720, PS: Attached, DataCap: 5G_NSA
[11-10_13:49:31:910] ip addr flush dev wwan0
...
```

> `wwan0` is the network interface for your modem.

---

## Testing Network Connectivity

### Using Ping

```bash
ping -I wwan0 8.8.8.8
ping -I wwan0 google.com
```

### Using iperf3

```bash
iperf3 -c robohub.eng.uwaterloo.ca -6 --time 30 --bind-dev $(cat /run/quectel_dev)
```

> This tests the throughput of your modem interface.

---

## Using AT Commands

1. Identify modem serial devices:

```bash
ls /dev/ttyUSB*
# example output: /dev/ttyUSB2
```

2. Start `minicom`:

```bash
sudo minicom -D /dev/ttyUSB2 -b 115200
```

3. Basic AT commands:

```
AT
# should return: OK

AT+QENG="servingcell"
# returns serving cell information
```

---

## Understanding AT Command Output

### Example Output:

```
+QENG: "servingcell","NOCONN"
+QENG: "LTE","FDD",302,720,9D8148,95,3050,7,5,5,73A0,-110,-16,-74,-2,4,140,-
+QENG: "NR5G-NSA",302,720,479,-100,3,-15,638016,77,8,1
```

### LTE Line Breakdown:

| Field     | Value  | Meaning                                   |
| --------- | ------ | ----------------------------------------- |
| Mode      | LTE    | LTE network info                          |
| Duplex    | FDD    | Frequency Division Duplex                 |
| MCC       | 302    | Mobile Country Code (Canada)              |
| MNC       | 720    | Mobile Network Code (Rogers)              |
| CellID    | 9D8148 | Unique cell identifier                    |
| PCID      | 95     | Physical Cell ID                          |
| EARFCN    | 3050   | LTE channel number                        |
| Freq Band | 7      | LTE Band 7                                |
| UL BW     | 5      | Uplink bandwidth (MHz)                    |
| DL BW     | 5      | Downlink bandwidth (MHz)                  |
| TAC       | 73A0   | Tracking Area Code                        |
| RSRP      | -110   | Reference Signal Received Power (dBm)     |
| RSRQ      | -16    | Reference Signal Received Quality (dB)    |
| RSSI      | -74    | Received Signal Strength Indicator (dBm)  |
| SINR      | -2     | Signal to Interference + Noise Ratio (dB) |
| CQI       | 4      | Channel Quality Indicator                 |
| TX Power  | 140    | Modem transmit power                      |
| SRxLev    | -      | Not used / empty                          |

### NR5G-NSA Line Breakdown:

| Field | Value    | Meaning                                     |
| ----- | -------- | ------------------------------------------- |
| Mode  | NR5G-NSA | 5G in Non-Standalone mode (uses LTE anchor) |
| MCC   | 302      | Country code (Canada)                       |
| MNC   | 720      | Mobile Network Code (Rogers)                |
| PCID  | 479      | Physical Cell ID                            |
| RSRP  | -100     | 5G Reference Signal Received Power          |
| SINR  | 3        | 5G Signal to Interference + Noise Ratio     |
| RSRQ  | -15      | Reference Signal Received Quality           |
| ARFCN | 638016   | NR frequency channel number                 |
| Band  | 77       | NR Band n78 (3.5 GHz)                       |
| DL BW | 8        | Downlink bandwidth (units vary, often MHz)  |
| SCS   | 1        | Subcarrier spacing (kHz)                    |

---

## Notes and Tips

* Ensure the modem is **connected to USB 3.0**, not USB-to-UART.
* Run `QConnectManager` as root due to network device permissions.
* Temporarily stopping `ModemManager` avoids conflicts.
* The `-4 -6` flags in `./quectel-CM` enable IPv4 and IPv6 connectivity.
* If `udhcpc` fails to obtain an IP, the manager will automatically retry in raw IP mode.

---


the use of cloning this and making it, then using it using the script is adding more DL bandwidth

fix issue, the files are not generated...
