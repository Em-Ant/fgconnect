################################################################################
#
# (C) 2021, Tiago Gasiba
#           tiago.gasiba@gmail.com
#
################################################################################
#
# engineTypeByte  (atools/src/fs/sc/simconnectaircraft.h)
#   PISTON       = 0,
#   JET          = 1,
#   NO_ENGINE    = 2,
#   HELO_TURBINE = 3,
#   UNSUPPORTED  = 4,
#   TURBOPROP    = 5
#
# shortFlags (atools/src/fs/sc/simconnecttypes.h)
#  NONE              = 0x0000,
#  ON_GROUND         = 0x0001,
#  IN_CLOUD          = 0x0002,
#  IN_RAIN           = 0x0004,
#  IN_SNOW           = 0x0008,
#  IS_USER           = 0x0010,
#  SIM_FSX_P3D       = 0x0020,
#  SIM_XPLANE        = 0x0040,
#  SIM_PAUSED        = 0x0080,
#  SIM_REPLAY        = 0x0100,
#  SIM_ONLINE        = 0x0200,
#  SIM_ONLINE_SHADOW = 0x0400
#
################################################################################
import os, sys
sys.path.append(os.path.dirname(__file__))

from bytestream import ByteStream
from datetime   import datetime, timezone
from time       import time

class LittleNavMapConnect:
  def __init__(self):
    self.buffer = None

    # Internal Constants
    self.MAGIC_NUMBER  = 0xf75e0af3
    self.PROTO_VERSION = 11
    
    # Internal Data
    self.packetID = 1
    self.packetTS = int(time())
    self.hasUserAirplane = 0
    self.thisAirplane = {}
    self.AIAirplanes = []

  def getBuffer(self):
    return self.buffer.stream

  def loadBuffer(self, bytesIn):
    self.buffer = ByteStream(bytesIn)

  def _readAirplane(self):
    d = {   "objectID" : self.buffer.get("uint32"),
            "byteFlags" : self.buffer.get("uint8"),
            "shortFlags" : self.buffer.get("uint16"),
            "title" : self.buffer.get("pascalstring"),
            "model" : self.buffer.get("pascalstring"),
            "reg" : self.buffer.get("pascalstring"),
            "type" : self.buffer.get("pascalstring"),
            "airline" : self.buffer.get("pascalstring"),
            "flightNr" : self.buffer.get("pascalstring"),
            "fromIdent" : self.buffer.get("pascalstring"),
            "toIdent" : self.buffer.get("pascalstring"),
            "lonx" : self.buffer.get("float"),
            "laty" : self.buffer.get("float"),
            "altitude" : self.buffer.get("float"),
            "headingTrueDeg" : self.buffer.get("float"),
            "headingMagDeg" : self.buffer.get("float"),
            "groundSpeedKts" : self.buffer.get("float"),
            "indicatedSpeedKts" : self.buffer.get("float"),
            "verticalSpeedFeetPerMin" : self.buffer.get("float"),
            "indicatedAltitudeFt" : self.buffer.get("float"),
            "trueAirspeedKts" : self.buffer.get("float"),
            "machSpeed" : self.buffer.get("float"),
            "numberOfEngines" : self.buffer.get("uint8"),
            "wingSpanFt" : self.buffer.get("uint16"),
            "modelRadiusFt" : self.buffer.get("uint16"),
            "deckHeight" : self.buffer.get("uint16"),
            "categoryByte" : self.buffer.get("uint8"),
            "engineTypeByte" : self.buffer.get("uint8"),
            "transponderCode" : self.buffer.get("int16"),
            "properties" : self.buffer.get("uint16")
        }
    return d

  def _readUserAirplane(self):
    d = { "windSpeedKts" : self.buffer.get("float"),
          "windDirectionDegT" : self.buffer.get("float"),
          "altitudeAboveGroundFt" : self.buffer.get("float"),
          "groundAltitudeFt" : self.buffer.get("float"),
          "altitudeAutopilotFt" : self.buffer.get("float"),
          "ambientTemperatureCelsius" : self.buffer.get("float"),
          "totalAirTemperatureCelsius" : self.buffer.get("float"),
          "seaLevelPressureMbar" : self.buffer.get("float"),
          "pitotIcePercent" : self.buffer.get("uint8"),
          "structuralIcePercent" : self.buffer.get("uint8"),
          "aoaIcePercent" : self.buffer.get("uint8"),
          "inletIcePercent" : self.buffer.get("uint8"),
          "propIcePercent" : self.buffer.get("uint8"),
          "statIcePercent" : self.buffer.get("uint8"),
          "windowIcePercent" : self.buffer.get("uint8"),
          "carbIcePercent" : self.buffer.get("uint8"),
          "airplaneTotalWeightLbs" : self.buffer.get("float"),
          "airplaneMaxGrossWeightLbs" : self.buffer.get("float"),
          "airplaneEmptyWeightLbs" : self.buffer.get("float"),
          "fuelTotalQuantityGallons" : self.buffer.get("float"),
          "fuelTotalWeightLbs" : self.buffer.get("float"),
          "fuelFlowPPH" : self.buffer.get("float"),
          "fuelFlowGPH" : self.buffer.get("float"),
          "magVarDeg" : self.buffer.get("float"),
          "ambientVisibilityMeter" : self.buffer.get("float"),
          "trackMagDeg" : self.buffer.get("float"),
          "trackTrueDeg" : self.buffer.get("float"),
          "localDateTime" : self.buffer.get("date"),
          "zuluDateTime" : self.buffer.get("date")
        }
    return d

  def deserializeBufer(self):
    # Process Header
    bufMagicNumber = self.buffer.get("uint32")
    if bufMagicNumber != self.MAGIC_NUMBER:
      raise Exception("Wrong magic number")
    bufPacketSize = self.buffer.get("uint32")
    if bufPacketSize != self.buffer.len():
      raise Exception("Wrong buffer size")
    bufProtoVersion = self.buffer.get("uint32")
    if bufProtoVersion != self.PROTO_VERSION:
      raise Exception("Wrong protocol version")
    self.packetID = self.buffer.get("uint32")
    self.packetTS = self.buffer.get("uint32")

    # Process User Airplane
    self.hasUserAirplane = self.buffer.get("uint8")
    if self.hasUserAirplane==1:
      myAirplane     = self._readAirplane()
      myUserAirplane = self._readUserAirplane()
      thisAirplane   = myAirplane | myUserAirplane
      self.thisAirplane = thisAirplane

    # Process AI Airplanes
    numAI = self.buffer.get("uint16")
    self.AIAirplanes = []
    for ii in range(numAI):
      d = AIAirplane = self._readAirplane()
      self.AIAirplanes.append(d)

    # Process METAR data (FIXME)
    numMETAR = self.buffer.get("uint16")

  def _serializeAirplane(self, myAirplane):
    buf = ByteStream()
    ########################################################################### Default Values
    buf.add("uint32", myAirplane.get("objectID",0))                           #  objectID                   = 0
    buf.add("uint8", myAirplane.get("byteFlags",0))                           #  byteFlags                  = 0
    buf.add("uint16", myAirplane.get("shortFlags",0x0051))                    #  shortFlags                 = 0x0051
    buf.add("pascalstring", myAirplane.get("title","MyTitle"))                #  title                      = "MyTitle"
    buf.add("pascalstring", myAirplane.get("model","Airbus"))                 #  model                      = "Airbus"
    buf.add("pascalstring", myAirplane.get("reg","A320"))                     #  reg                        = "A320"
    buf.add("pascalstring", myAirplane.get("type","400"))                     #  type                       = "400"
    buf.add("pascalstring", myAirplane.get("airline","SmoothFlight"))         #  airline                    = "SmoothFlight"
    buf.add("pascalstring", myAirplane.get("flightNr","DLH4424"))             #  flightNr                   = "DHL4424"
    buf.add("pascalstring", myAirplane.get("fromIdent",""))                   #  fromIdent                  = ""
    buf.add("pascalstring", myAirplane.get("toIdent",""))                     #  toIdent                    = ""
    buf.add("float", myAirplane.get("lonx",11.795230555555556))               #  lonX                       = 11.795230555555556
    buf.add("float", myAirplane.get("laty",48.354438888888889))               #  laty                       = 48.616333333333333
    buf.add("float", myAirplane.get("altitude",1482.0))                       #  altitude                   = 1482 ft
    buf.add("float", myAirplane.get("headingTrueDeg",0.0))                    #  headingTrueDeg             = 0.0
    buf.add("float", myAirplane.get("headingMagDeg",0.0))                     #  headingMagDeg              = 0.0
    buf.add("float", myAirplane.get("groundSpeedKts",0.0))                    #  groundSpeedKts             = 0.0
    buf.add("float", myAirplane.get("indicatedSpeedKts",0.0))                 #  indicatedSpeedKts          = 0.0
    buf.add("float", myAirplane.get("verticalSpeedFeetPerMin",0.0))           #  verticalSpeedFeetPerMin    = 0.0
    buf.add("float", myAirplane.get("indicatedAltitudeFt",1482.0))            #  indicatedAltitudeFt        = 1482 ft
    buf.add("float", myAirplane.get("trueAirspeedKts",0.0))                   #  trueAirspeedKts            = 0.0
    buf.add("float", myAirplane.get("machSpeed",0.0))                         #  machSpeed                  = 0.0
    buf.add("uint8", myAirplane.get("numberOfEngines",1))                     #  numberOfEngines            = 1
    buf.add("uint16", myAirplane.get("wingSpanFt",0))                         #  wingSpanFt                 = 0
    buf.add("uint16", myAirplane.get("modelRadiusFt",0))                      #  modelRadiusFt              = 0
    buf.add("uint16", myAirplane.get("deckHeight",0))                         #  deckHeight                 = 0
    buf.add("uint8", myAirplane.get("categoryByte",0))                        #  categoryByte               = 0
    buf.add("uint8", myAirplane.get("engineTypeByte",4))                      #  engineTypeByte             = 4
    buf.add("int16", myAirplane.get("transponderCode",0o1234))                #  transponderCode            = 0o1234
    buf.add("uint16", myAirplane.get("properties",0))                         #  properties                 = 0
    return buf

  def _serializeUserAirplane(self, myUserAirplane):
    buf = ByteStream()

    nowUTC       = datetime.now(timezone.utc)
    year         = nowUTC.year
    month        = nowUTC.month
    day          = nowUTC.day
    hour         = nowUTC.hour
    minute       = nowUTC.minute
    second       = nowUTC.second
    millisecond  = nowUTC.microsecond // 1000
    localUTCTime = (year,month,day,hour,minute,second,millisecond)
    ########################################################################### Default Values
    buf.add("float", myUserAirplane.get("windSpeedKts",0.0))                  #  windSpeedKts               = 0.0
    buf.add("float", myUserAirplane.get("windDirectionDegT",0.0))             #  windDirectionDegT          = 0.0
    buf.add("float", myUserAirplane.get("altitudeAboveGroundFt",0.0))         #  altitudeAboveGroundFt      = 0.0
    buf.add("float", myUserAirplane.get("groundAltitudeFt",0.0))              #  groundAltitudeFt           = 0.0
    buf.add("float", myUserAirplane.get("altitudeAutopilotFt",10000.0))       #  altitudeAutopilotFt        = 10000.0
    buf.add("float", myUserAirplane.get("ambientTemperatureCelsius",15.0))    #  ambientTemperatureCelsius  = 15.0
    buf.add("float", myUserAirplane.get("totalAirTemperatureCelsius",15.0))   #  totalAirTemperatureCelsius = 15.0
    buf.add("float", myUserAirplane.get("seaLevelPressureMbar",1013.25))      #  seaLevelPressureMbar       = 1013.25 hPa
    buf.add("uint8", myUserAirplane.get("pitotIcePercent",0))                 #  pitotIcePercent            = 0
    buf.add("uint8", myUserAirplane.get("structuralIcePercent",0))            #  structuralIcePercent       = 0
    buf.add("uint8", myUserAirplane.get("aoaIcePercent",0))                   #  aoaIcePercent              = 0
    buf.add("uint8", myUserAirplane.get("inletIcePercent",0))                 #  inletIcePercent            = 0
    buf.add("uint8", myUserAirplane.get("propIcePercent",0))                  #  propIcePercent             = 0
    buf.add("uint8", myUserAirplane.get("statIcePercent",0))                  #  statIcePercent             = 0
    buf.add("uint8", myUserAirplane.get("windowIcePercent",0))                #  windowIcePercent           = 0
    buf.add("uint8", myUserAirplane.get("carbIcePercent",0))                  #  carbIcePercent             = 0
    buf.add("float", myUserAirplane.get("airplaneTotalWeightLbs",2000.0))     #  airplaneTotalWeightLbs     = 2000.0
    buf.add("float", myUserAirplane.get("airplaneMaxGrossWeightLbs",4000.0))  #  airplaneMaxGrossWeightLbs  = 4000.0
    buf.add("float", myUserAirplane.get("airplaneEmptyWeightLbs",1500.0))     #  airplaneEmptyWeightLbs     = 1500.0
    buf.add("float", myUserAirplane.get("fuelTotalQuantityGallons",25.0))     #  fuelTotalQuantityGallons   = 25.0
    buf.add("float", myUserAirplane.get("fuelTotalWeightLbs",140.0))          #  fuelTotalWeightLbs         = 140.0
    buf.add("float", myUserAirplane.get("fuelFlowPPH",0.0))                   #  fuelFlowPPH                = 0.0
    buf.add("float", myUserAirplane.get("fuelFlowGPH",0.0))                   #  fuelFlowGPH                = 0.0
    buf.add("float", myUserAirplane.get("magVarDeg",0.0))                     #  magVarDeg                  = 0.0
    buf.add("float", myUserAirplane.get("ambientVisibilityMeter",40200.0))    #  ambientVisibilityMeter     = 40200.0
    buf.add("float", myUserAirplane.get("trackMagDeg",351.0))                 #  trackMagDeg                = 351.0
    buf.add("float", myUserAirplane.get("trackTrueDeg",349.0))                #  trackTrueDeg               = 349.0
    buf.add("date", *myUserAirplane.get("localDateTime",localUTCTime))        #  localDateTime              = "current UTC time"
    buf.add("date", *myUserAirplane.get("zuluDateTime",localUTCTime))         #  zuluDateTime               = "current UTC time"
    return buf
 
  def serializeBuffer(self, myAirplane, AIAirplanes=[]):
    # Temporary buffer needed, since we need to add its size to the header
    buf = ByteStream()

    # Add part of header
    buf.add("uint32",self.PROTO_VERSION)
    buf.add("uint32",self.packetID)        
    buf.add("currtimestamp")

    # Create the User Airplane
    buf.add("uint8",1)
    p = self._serializeAirplane(myAirplane)
    buf.append(p)
    p = self._serializeUserAirplane(myAirplane)
    buf.append(p)

    # Create the AI Airplanes
    buf.add("uint16",len(AIAirplanes))
    for ii in range(len(AIAirplanes)):
      p = self._serializeAirplane(AIAirplanes[ii])
      buf.append(p)

    # Create the METAR data (FIXME)
    buf.add("uint16",0)

    # Create serialized object
    self.buffer = ByteStream()
    self.buffer.add("uint32",self.MAGIC_NUMBER)
    self.buffer.add("uint32",buf.len())
    self.buffer.append(buf)

