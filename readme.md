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
