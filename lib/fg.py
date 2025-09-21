################################################################################
#
# (C) 2021, Tiago Gasiba
#           tiago.gasiba@gmail.com
#
################################################################################
import os, sys
sys.path.append(os.path.dirname(__file__))

from helper import distanceKm
import xmltodict
import requests
import json

class FlightGearConnect:
  def __init__(self, xmlCfgFile, hostName=None, hostPort=None):
    if xmlCfgFile:
      self.cfg = self._readXmlConfig(xmlCfgFile)
    else:
      self.cfg = None
    self.hostName = hostName
    self.hostPort = hostPort

  def _readXmlConfig( self, xmlCfgFile ):
    with open(xmlCfgFile,"r") as f:
      fileContents = f.read()
    cfgDict = xmltodict.parse(fileContents)
    outCfg  = cfgDict["PropertyList"]["generic"]["output"]
    lineSep = outCfg["line_separator"]
    varSep  = outCfg["var_separator"]
    chunk   = outCfg["chunk"]
    retCfg  = { "linesep": lineSep, "varsep": varSep, "outchunk":[] }
    for c in chunk:
      varName = c["name"].split(" ")[0]
      varType = c["type"]
      varFmt  = c["format"]
      varNode = c["node"]
      retCfg["outchunk"].append( {"name":varName, "type":varType, "format":varFmt, "node": varNode} )
    return retCfg

  def _readValType( self, valStr, valType ):
    if valType=="float":
      return float(valStr)
    elif valType=="short":
      return int(valStr)
    elif valType=="integer":
      return int(valStr)
    elif valType=="int":
      return int(valStr)
    elif valType=="string":
      return valStr
    else:
      raise Exception("ERROR: unkown value type "+str(valType))

  def parseUDPPacket(self, packet):
    pkt  = packet.decode("utf-8")
    vals = pkt.split(self.cfg["varsep"])
    if len(vals)!=len(self.cfg["outchunk"]):
      raise Exception("ERROR in dimensions")
    readVals = {}
    for n in range(len(vals)):
      nValStr = vals[n]
      nName   = self.cfg["outchunk"][n]["name"]
      nNode   = self.cfg["outchunk"][n]["node"]
      nType   = self.cfg["outchunk"][n]["type"]
      nVal    = self._readValType(nValStr,nType)
      readVals[nNode] = nVal
    return readVals

  def _loadChildren( self, jIn ):
    n    = len(jIn)
    dRet = {}
    for ii in range(n):
      jN = jIn[ii]
      try:
        myChildren = jN["children"]
        dChildren  = self._loadChildren(myChildren)
        dRet |= dChildren
        continue
      except:
        pass
      try:
        myPath       = jN["path"]
        myType       = jN["type"]
        myValue      = jN["value"]
        dRet[myPath] = myValue
      except:
        pass
    return dRet

  def loadAIAirplanesFrom(self):
    r  = requests.get("http://"+self.hostName+":"+str(self.hostPort)+"/json/ai/models?d=4")
    rj = json.loads(r.text)
    children = rj["children"]
    c = self._loadChildren(children)
    return c

  def _getOwnLatitudeLongitude(self):
    r  = requests.get("http://"+self.hostName+":"+str(self.hostPort)+"/json/position/latitude-deg")
    rj = json.loads(r.text)
    self.myLatitude = rj["value"]
    r  = requests.get("http://"+self.hostName+":"+str(self.hostPort)+"/json/position/longitude-deg")
    rj = json.loads(r.text)
    self.myLongitude = rj["value"]

  def loadNAIAirplanes(self, n):
    self._getOwnLatitudeLongitude()
    ai       = self.loadAIAirplanesFrom()
    nAI      = ai["/ai/models/count"]
    AISort   = []
    aiKeys = {}
    for k in ai.keys():
      s = k.split("/")[0:4]
      if "aircraft" in s[3]:
        newKey = "/".join(s)
        aiKeys[newKey] = 1
    for aiKey in aiKeys.keys():
      longitude = ai[aiKey + "/position/longitude-deg"]
      latitude  = ai[aiKey + "/position/latitude-deg"]
      dKm = distanceKm( (self.myLongitude,self.myLatitude), (longitude,latitude) )
      AISort.append( (dKm, aiKey) )
    AISort.sort(key=lambda x:x[0])
    AIPlanes = AISort[:n]
    retPlanes = []
    for ii in range(len(AIPlanes)):
      aiKey = AIPlanes[ii][1]
      addPlane = {}
      for k in ai:
        if aiKey in k:
          newKey = k[1+len(aiKey):]
          addPlane[newKey] = ai[k]
      retPlanes.append(addPlane)
    return retPlanes

