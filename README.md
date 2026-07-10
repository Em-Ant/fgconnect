# FGconnect (Unified Patched Edition) 🚀

This branch (`combined-fixes`) serves as a consolidated reference environment for `fgconnect`. It resolves upstream merge conflicts and unites three critical tracking and telemetry fixes into a single, functional runtime. 

If you are looking for isolated implementations to review or merge individually, please refer to the standalone feature branches (`status-fix`, `plane-icao`, and `fuel`).

---

### 🛠️ Summary of Combined Fixes & Cross-Repo Collaboration

Achieving full telemetry tracking in Little Navmap (LNM) requires tight coordination between this Python connector framework and the XML network protocol emitter inside [flightgear-addon-littlenavmap](https://github.com/jimishol/flightgear-addon-littlenavmap/tree/combined-fixes). This branch unifies the following enhancements:

1. **Ground Status Fix**
   * *The Problem:* Flight telemetry consistently locked the aircraft state to "on the ground," failing to trigger active flight log profiling in LNM.
   * *The Fix:* Corrected the status evaluation logic inside the connector loop to properly track live airborne transitions.

2. **ICAO Aircraft Model Alignment**
   * *The Problem:* Mismatched or missing aircraft type designators caused LNM to render generic fallback models.
   * *The Fix:* Synchronized string parsing between the XML payload and the Python connector to ensure proper ICAO companion mapping.

3. **Universal Fuel & Performance Telemetry (FDM-Independent)**
   * *The Problem:* Legacy fuel mapping relied heavily on FDM-specific property trees (like `/fdm/jsbsim/...`), completely breaking fuel flow and tank telemetry for non-JSBSim aircraft.
   * *The Fix:* Shifted fuel analytics to a dynamic calculation layer. By collaborating with an updated array structure in the XML protocol, the Python script now dynamically iterates through up to 4 engines and 4 fuel tanks. It checks active engine `running` states, tracks selected tanks, and aggregates total Fuel Flow (GPH/PPH) using live fuel density (`density-ppg`) telemetry.

4. **Multiplayer Aircraft Traffic Support**
   * *The Problem:* fgconnect only detected AI aircraft because the property‑tree filter in lib/fg.py excluded the /ai/models/multiplayer branch. As a result, human‑controlled aircraft never appeared in Little Navmap, and missing fields in multiplayer nodes caused occasional crashes.
   * *The Fix:* The connector now recognizes multiplayer aircraft by expanding the path filter to include the multiplayer branch. The translation layer in lib/helper.py was updated to safely handle missing identifiers using .get(), ensuring stable processing even when pilots have no flight plan. This enables full multiplayer visibility in Little Navmap without breaking the binary protocol.

---
# About

This small program is used to connect the FlightGear flight simulator to the LittleNavMap.
To make this application run, please install the FlightGear Addon from the following link:

- https://github.com/slawekmikula/flightgear-addon-littlenavmap

This program replaces the official application "littlefgconnect" which needs to be built
from source on linux. Also, the official application does not connect directly
between FlightGear and LittleNavMap, but requires LittleNavConnect in between.

Except for the add-on, this program does not require anything else to be running on the
machine. To use it, just provide the IP address/server name and port number of the
machine running FlightGear + Addon, and also provide the IP address/server name and port
number of the machine running LittleNavMap. Click start (on both Start buttons for
FlightGear, and LittleNavMap) and enjoy!

## Usage

You can run `fgconnect.py` either via GUI (default) or via command-line arguments for headless or scripted operation.

### Command-Line Arguments

```bash
python fgconnect.py [OPTIONS]
```

#### Options:

| Argument       | Default     | Description                                        |
| -------------- | ----------- | -------------------------------------------------- |
| `-h`, `--help` | —           | Show this help message and exit                    |
| `-s`           | —           | Run in Stand-Alone Mode (no GUI)                   |
| `--lnmip`      | `127.0.0.1` | IP Address or Host Name of LittleNavMap            |
| `--lnmpt`      | `51968`     | UDP Port of LittleNavMap                           |
| `--fgip`       | `127.0.0.1` | IP Address or Host Name of FlightGear              |
| `--fglnmpt`    | `7755`      | UDP Port of FlightGear’s LittleNavMap Plugin       |
| `--fghttppt`   | `5400`      | HTTP Port of FlightGear (for property tree access) |

#### Example:

To connect to FlightGear running on a remote machine `192.168.1.10` and LittleNavMap on `192.168.1.20`:

```bash
python fgconnect.py --fgip 192.168.1.10 --lnmip 192.168.1.20 -s
```

> **Note**: Use `-s` (stand-alone mode) to run without the GUI — useful for automation or servers.

### GUI Mode (Default)

If no command-line arguments are provided (or `-s` is omitted), a Tkinter-based GUI will launch. Use the interface to:

1. Enter the IP and port for **FlightGear** (with addon running).
2. Enter the IP and port for **LittleNavMap**.
3. Click **Start** for both FlightGear and LittleNavMap connections.
4. Monitor connection status in the log window.

Ensure both applications are running and ports are open/firewall-allowed.

---

## Credits

Cloned from https://gitlab.com/tgasiba/fgconnect by Thiago Gasiba. I just replaced the wxWidget with Tkinter and added uv project dependencies management.

**Em-Ant 2025**
