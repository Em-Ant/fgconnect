#!python3
################################################################################
#
# (C) 2021-2022, Tiago Gasiba
#                tiago.gasiba@gmail.com
#
################################################################################
from multiprocessing import Process, Value, Queue
from lib.fg          import FlightGearConnect
from lib.lnm         import LittleNavMapConnect
from lib.helper      import *
import getopt
import socket
import time
import sys

nAIPlanes = 60

################################################################################
def processReadFromFlightGear(stopSignal, evtQ, pCfg):
  fgIP_ADDR  = pCfg["IP_ADDR"]
  fgUDP_PORT = pCfg["UDP_PORT"]
  sleepTime  = pCfg["sleepTime"]
  xmlCfgFile = pCfg["xmlCfgFile"]
  fgCon      = FlightGearConnect(xmlCfgFile)
  sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
  sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  sock.bind( (fgIP_ADDR, fgUDP_PORT) )
  sock.setblocking(0)
  rxAirplaneData = None
  while 0==stopSignal.value:
    try:
      data, addr = sock.recvfrom(16384)
    except socket.error:
      rxAirplaneData = None
    else:
      rxAirplaneData = fgCon.parseUDPPacket(data)
    if (not evtQ.full()) and (rxAirplaneData!= None):
      evtQ.put( rxAirplaneData )
      rxAirplaneData= None
    time.sleep(sleepTime)

################################################################################
def processReadAIFromFlightGear(stopSignal, evtQ, pCfg):
  fgIP_ADDR  = pCfg["IP_ADDR"]
  fgUDP_PORT = pCfg["UDP_PORT"]
  sleepTime  = pCfg["sleepTime"]
  fgCon      = FlightGearConnect(None, fgIP_ADDR, 5400)
  sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
  sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  sock.bind( (fgIP_ADDR, fgUDP_PORT) )
  sock.setblocking(0)
  rxAIData = None
  while 0==stopSignal.value:
    try:
      rxAIData = fgCon.loadNAIAirplanes(nAIPlanes)
    except socket.error:
      rxAIData = None
    if (not evtQ.full()) and (rxAIData != None):
      evtQ.put( rxAIData )
      rxAIData = None
    time.sleep(sleepTime)

################################################################################
def processWriteToLittleNavMap(stopSignal, myEvtQ, AIEvtQ, pCfg):
  lnmIP_ADDR  = pCfg["IP_ADDR"]
  lnmUDP_PORT = pCfg["UDP_PORT"]
  sleepTime   = pCfg["sleepTime"]
  verbose     = pCfg.get("verbose", False)
  lnm         = LittleNavMapConnect()

  # Create a TCP/IP socket
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  
  # Connect the socket to the port where the server is listening
  server_address = ('localhost', 51968)
  sock.bind( (lnmIP_ADDR, lnmUDP_PORT) )
  
  # Listen for incoming connections
  sock.listen(1)

  rxAirplaneData = None
  rxAIData       = None
  memAirplane    = {}
  memAI          = []
  while 0==stopSignal.value:
    conn, clientAddr = sock.accept()
    try:
      while 0==stopSignal.value:
        # Read data about my own Airplane
        if not myEvtQ.empty():
          rxAirplaneData = myEvtQ.get()
        # Read data AI airplanes
        if not AIEvtQ.empty():
          rxAIData = AIEvtQ.get()
          
        # Translate my own Airplane data FlightGear to LittleNavMap
        if rxAirplaneData:
          memAirplane = translateToAirplane(rxAirplaneData)
          
          # --- CALCULATE FUEL FLOW AND LEVEL ---
          fuel_flow_gph = 0.0
          fuel_level_gal = 0.0

          for i in range(4):
              # Because lib/fg.py maps using `nNode`, we query the exact XML node paths
              flow = float(rxAirplaneData.get(f"/engines/engine[{i}]/fuel-flow-gph", 0.0))
              running = rxAirplaneData.get(f"/engines/engine[{i}]/running", 0)
              
              # FlightGear natively exports bools as 1/0 or 'true' via %d/%s
              if str(running).strip().lower() in ['1', 'true', 'yes', 't']: 
                  fuel_flow_gph += flow
              
              level = float(rxAirplaneData.get(f"/consumables/fuel/tank[{i}]/level-gal_us", 0.0))
              selected = rxAirplaneData.get(f"/consumables/fuel/tank[{i}]/selected", 0)
              
              if str(selected).strip().lower() in ['1', 'true', 'yes', 't']: 
                  fuel_level_gal += level

          # Map values back to memAirplane for LittleNavMap serialization
          memAirplane['fuelFlowGPH'] = fuel_flow_gph
          memAirplane['fuelTotalQuantityGallons'] = fuel_level_gal
          # -------------------------------------

          if verbose:
            print(f"USER: alt={memAirplane.get('altitude','MISSING'):.1f} ft, "
                  f"agl={memAirplane.get('altitudeAboveGroundFt',0):.1f} ft, "
                  f"ground={memAirplane.get('groundAltitudeFt',0):.1f} ft, "
                  f"vs={memAirplane.get('verticalSpeedFeetPerMin',0):.1f} fpm, "
                  f"lat={memAirplane.get('laty',0):.4f}, lon={memAirplane.get('lonx',0):.4f}, "
                  f"flow={fuel_flow_gph:.1f} gph, fuel={fuel_level_gal:.1f} gal")
            
        # Translate AI data FlightGear to LittleNavMap
        if rxAIData:
          memAI = translateToAI(rxAIData)
          if verbose and memAI:
            a = memAI[0]
            print(f"AI[0]: alt={a.get('altitude','MISSING')} ft, "
                  f"vs={a.get('verticalSpeedFeetPerMin',0):.1f} fpm, "
                  f"lat={a.get('laty',0):.4f}, lon={a.get('lonx',0):.4f}")
                  
        # Serialize and packetize data
        lnm.serializeBuffer(memAirplane, memAI)
        # Send data to LittleNavMap
        myPacket = lnm.getBuffer()
        conn.sendall(myPacket)
        # Receive reply from LittleNavMap
        data = conn.recv(300)
        time.sleep(sleepTime)
        # Reset received data
        rxAirplaneData = None
        rxAIData       = None
    finally:
      conn.close()

if __name__ == '__main__':
  standAloneMode = False
  # Default Values (Console)
  lnmIP          = "127.0.0.1"
  lnmPT          = 51968
  fgIP           = "127.0.0.1"
  fglnmPT        = 7755
  fghttpPT       = 5400

  verbose = False
  try:
    opts, args = getopt.getopt(sys.argv[1:], "hsv", ["help", "verbose", "lnmip", "lnmpt", "fgip", "fglnmpt", "fghttppt"])
  except getopt.GetoptError as err:
    print(err)
    sys.exit(2)
  for o, a in opts:
    if (o == "-h") or (o=="--help"):
      print("Command line arguments:")
      print("")
      print("  Argument      Default    Description")
      print("  [-h]                     Help")
      print("  [-s]                     Stand-Alone Mode")
      print("  [-v] [--verbose]         Verbose debug output")
      print("  [--lnmip]     127.0.0.1  IP Address / Host Name of LittleNavMap")
      print("  [--lnmpt]     51968      UDP Port of LittleNavMap")
      print("  [--fgip]      127.0.0.1  IP Address / Host Name of FlightGear")
      print("  [--fglnmpt]   7755       UDP Port of FlightGear - LittleNavMap Plugin")
      print("  [--fghttppt]  5400       HTTP port of FlightGear")
      print("")
      sys.exit()
    elif (o == "-s"):
      standAloneMode = True
    elif (o == "-v") or (o=="--verbose"):
      verbose = True
    elif (o == "--lnmip"):    lnmIP = a
    elif (o == "--lnmpt"):    lnmPT = int(a)
    elif (o == "--fgip"):     fgIP = a
    elif (o == "--fglnmpt"):  fglnmPT = int(a)
    elif (o == "--fghttppt"): fghttpPT = int(a)
    else:
      assert False, "unhandled option"

  print("Starting FlightGear Connect Tool...")
  print("Press CTRL-C a couple times to stop")
  if standAloneMode:
    myEvtQ = Queue(maxsize=1)
    AIEvtQ = Queue(maxsize=1)
    #############
    flag1 = Value("i",0)
    pCfg = { "IP_ADDR"    : fgIP,
             "UDP_PORT"   : fglnmPT,
             "sleepTime"  : 1/10.0,
             "xmlCfgFile" : "littlenavmap.xml",
           }
    p1 = Process( target=processReadFromFlightGear, args=(flag1, myEvtQ, pCfg) )
    p1.start()
    #############
    pCfg = { "IP_ADDR"    : fgIP,
             "UDP_PORT"   : fghttpPT,
             "sleepTime"  : 1/2.0,
           }
    p0 = Process( target=processReadAIFromFlightGear, args=(flag1, AIEvtQ, pCfg) )
    p0.start()
    #############
    flag2 = Value("i",0)
    pCfg = { "IP_ADDR"    : lnmIP,
             "UDP_PORT"   : lnmPT,
             "sleepTime"  : 1/10.0,
             "verbose"    : verbose,
           }
    p2 = Process( target=processWriteToLittleNavMap, args=(flag2, myEvtQ, AIEvtQ, pCfg) )
    p2.start()
    #############
    while True:
      time.sleep(4)

  else:
    from gui_tk import *
    app = MainApp()
    app.mainloop()
