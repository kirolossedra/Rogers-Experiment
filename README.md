
# Rogers Experiment

### Husky Setup
- Set your Ethernet IP to the same subnet as the Husky (e.g., **192.168.131.x**).
- Then, try pinging the Husky’s IP to verify connectivity:
  ```bash
  ping 192.168.131.1
  ```

* SSH into the Husky:

  ```bash
  ssh administrator@192.168.131.1
  ```
* Turn on the Joystick controller and it will connect to the robot

### Rogers Experiment To-Do

* [ ] Try out the mid-range 5G modem to do a sanity check for the AT commands and scripts.
  → Afterward, list here a set of useful AT commands.
* [ ] Redo the **2 AP** setup with uplink, downlink, and noise floor measurement script.
* [ ] Redo the **single AP** setup with uplink, downlink, and noise floor measurement script.
* [ ] Perform the **5G test twice**: once for uplink and once for downlink.

---


### Improvements

* [x] Use unified timestamps in all files, logs, latency, iperf
* [x] Only generating the logs one time per experiment instead of generating multiple files for each AP
* [x] RF Improvement placing on plastic shelf instead of placing directly on concrete
* [x] Decreasing Tx power to allow for roaming to happen in 2AP experiment
* [x] Prepare downlink and uplink scripts both with showing retr(retr is already there)
* [x] Update the commant list to include noise floor logging


### Reminder Tasks 
* [x] Getting started with 5G Mid-band modem
* [ ] Test the script and modify it according to the experiment
* [ ] Change the Tx power back to 5dbm to run the 2AP experiment





### Broadcast Paper To-Do

* [ ] Re-run **NS-3 simulations** for the broadcast project, this time including **impairments**.
