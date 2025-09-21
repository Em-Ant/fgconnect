################################################################################
#
# (C) 2021, Tiago Gasiba
#           tiago.gasiba@gmail.com
#
################################################################################
#
# Example of usage:
#
#     x = ByteStream()
#
#     x.add("uint8",1)
#     x.add("uint16",2)
#     x.add("uint32",3)
#     x.add("uint64",4)
#     x.add("float",1013.25)
#     x.add("date",2021,1,1,12,0,0)
#     x.addCurrDateTime()
#     x.add("pascalstring","tiago")
#     
#     print(x.len())
#     print(x)
#     
#     print(x.get("uint8"))
#     print(x.get("uint16"))
#     print(x.get("uint32"))
#     print(x.get("uint64"))
#     print(x.get("float"))
#     print(x.get("date"))
#     print(x.get("date"))
#     print(x.get("pascalstring"))
#
################################################################################
from datetime import date, datetime, timezone, timedelta
from struct import pack, unpack, calcsize
from time import time

class ByteStream:
  def __init__(self, bytesIn=None):
    if bytesIn:
      self.stream = bytesIn
    else:
      self.stream = b""

  def setStream(self, bytesIn):
    self.stream = bytesIn

  def len(self):
    return len(self.stream)

  def append(self, inp):
    if type(inp)==ByteStream:
      self.stream = self.stream + inp.stream
    elif type(inp)==bytes:
      self.stream = self.stream + inp
    else:
      raise Exception("Cannot append "+str(type(inp)))

  def _dumpHex( self, inHex, maxLen=None ):
    retStr = ""
    for ii in range(len(inHex)):
      if (maxLen) and (maxLen<ii): break
      if ii%16 == 0: retStr += "{0:04x}: ".format(ii)
      u = inHex[ii]
      retStr += "{0:02x} ".format(u)
      if ii%16==15: retStr += "\n"
    retStr += "\n"
    return retStr

  def _packDate( self, year, month, day, hour, minute, second, millisecond=0 ):
    dBase     = date(1900, 1, 1) # is represented as 0x24d9ad
    dFinal    = date(year, month, day)
    dDelta    = dFinal - dBase
    deltaDays = dDelta.days
    myDate    = 0x24d9ad + deltaDays
    myTime    = 1000*(3600*hour + 60*minute + second) + millisecond
    timeSpec  = 1 # UTC time
    p = pack(">IIIB",0,myDate,myTime,timeSpec)
    return p

  def _unpackDate( self, bytesIn ):
   x,myDate,myTime,timeSpec = unpack(">IIIB",bytesIn)
   dBase        = date(1900, 1, 1) # is represented as 0x24d9ad
   dDelta       = myDate - 0x24d9ad
   dFinal       = dBase + timedelta(days=dDelta)
   tmp          = myTime
   milliseconds = tmp % 1000
   tmp          = tmp // 1000
   seconds      = tmp % 60
   tmp          = tmp // 60
   minutes      = tmp % 60
   tmp          = tmp // 60
   hours        = tmp
   return (dFinal.year, dFinal.month, dFinal.day, hours, minutes, seconds, milliseconds)

  def _packPascalString( self, string ):
    strUTF8 = string.encode("utf-8")
    strLen  = len(strUTF8)
    p = pack("B",strLen) + strUTF8
    return p

  def _unpackPascalString( self, bytesIn ):
    nChars, = unpack("B",bytesIn[0:1])
    if nChars>0:
      unpackString = "{0}B".format(nChars)
      myString = bytesIn[1:1+nChars]
      return myString.decode("utf-8")
    else:
      return ""

  def add(self, varType, *values):
    if varType == "uint8":
      p = pack(">B",values[0] & 0xff)
      self.stream += p
    elif varType == "int8":
      p = pack(">b",values[0] & 0xff)
      self.stream += p
    elif varType == "uint16":
      p = pack(">H",values[0] & 0xffff)
      self.stream += p
    elif varType == "int16":
      p = pack(">h",values[0] & 0xffff)
      self.stream += p
    elif varType == "uint32":
      p = pack(">I",values[0] & 0xffffffff)
      self.stream += p
    elif varType == "int32":
      p = pack(">i",values[0] & 0xffffffff)
      self.stream += p
    elif varType == "uint64":
      p = pack(">Q",values[0])
      self.stream += p
    elif varType == "int64":
      p = pack(">q",values[0])
      self.stream += p
    elif varType == "float":
      p = pack(">f",values[0])
      self.stream += p
    elif varType == "double":
      p = pack(">d",values[0])
      self.stream += p
    elif varType == "date":
      try:
        year, month, day, hour, minute, second, microsecond = values
      except :
        year, month, day, hour, minute, second = values
        microsecond = 0
      p = self._packDate( year, month, day, hour, minute, second, microsecond )
      self.stream += p
    elif varType == "pascalstring":
      p = self._packPascalString(values[0])
      self.stream += p
    elif varType == "currtimestamp":
      t = int(time())
      p = pack(">I",t)
      self.stream += p
    else:
      raise Exception("Unknown variable type" + str(varType))

  def addCurrDateTime(self):
    nowUTC      = datetime.now(timezone.utc)
    year        = nowUTC.year
    month       = nowUTC.month
    day         = nowUTC.day
    hour        = nowUTC.hour
    minute      = nowUTC.minute
    second      = nowUTC.second
    millisecond = nowUTC.microsecond // 1000
    self.add("date",year,month,day,hour,minute,second,millisecond)

  def get(self, varType):
    if varType == "uint8":
      nBytes = 1
      if len(self.stream) < nBytes: raise Exception("Buffer exhausted")
      varVal = unpack(">B",self.stream[0:nBytes])
      self.stream = self.stream[nBytes:]
      return varVal[0]
    elif varType == "int8":
      nBytes = 1
      if len(self.stream) < nBytes: raise Exception("Buffer exhausted")
      varVal = unpack(">b",self.stream[0:nBytes])
      self.stream = self.stream[nBytes:]
      return varVal[0]
    elif varType == "uint16":
      nBytes = 2
      if len(self.stream) < nBytes: raise Exception("Buffer exhausted")
      varVal = unpack(">H",self.stream[0:nBytes])
      self.stream = self.stream[nBytes:]
      return varVal[0]
    elif varType == "int16":
      nBytes = 2
      if len(self.stream) < nBytes: raise Exception("Buffer exhausted")
      varVal = unpack(">h",self.stream[0:nBytes])
      self.stream = self.stream[nBytes:]
      return varVal[0]
    elif varType == "uint32":
      nBytes = 4
      if len(self.stream) < nBytes: raise Exception("Buffer exhausted")
      varVal = unpack(">I",self.stream[0:nBytes])
      self.stream = self.stream[nBytes:]
      return varVal[0]
    elif varType == "int32":
      nBytes = 4
      if len(self.stream) < nBytes: raise Exception("Buffer exhausted")
      varVal = unpack(">i",self.stream[0:nBytes])
      self.stream = self.stream[nBytes:]
      return varVal[0]
    elif varType == "uint64":
      nBytes = 8
      if len(self.stream) < nBytes: raise Exception("Buffer exhausted")
      varVal = unpack(">Q",self.stream[0:nBytes])
      self.stream = self.stream[nBytes:]
      return varVal[0]
    elif varType == "int64":
      nBytes = 8
      if len(self.stream) < nBytes: raise Exception("Buffer exhausted")
      varVal = unpack(">q",self.stream[0:nBytes])
      self.stream = self.stream[nBytes:]
      return varVal[0]
    elif varType == "float":
      nBytes = 4
      if len(self.stream) < nBytes: raise Exception("Buffer exhausted")
      varVal = unpack(">f",self.stream[0:nBytes])
      self.stream = self.stream[nBytes:]
      return varVal[0]
    elif varType == "double":
      nBytes = 8
      if len(self.stream) < nBytes: raise Exception("Buffer exhausted")
      varVal = unpack(">d",self.stream[0:nBytes])
      self.stream = self.stream[nBytes:]
      return varVal[0]
    elif varType == "date":
      nBytes = 13
      if len(self.stream) < nBytes: raise Exception("Buffer exhausted")
      varVal = self._unpackDate(self.stream[0:nBytes])
      if self.stream[12]==2: nBytes += 4 # FIXME: skip the time offset!
      if len(self.stream) < nBytes: raise Exception("Buffer exhausted")
      self.stream = self.stream[nBytes:]
      return varVal
    elif varType == "pascalstring":
      varVal = self._unpackPascalString(self.stream)
      nBytes = 1 + len(varVal)
      self.stream = self.stream[nBytes:]
      return varVal
    else:
      raise Exception("Unknown variable type" + str(varType))

  def __repr__(self):
    if len(self.stream)==0: return "Empty stream"
    return self._dumpHex(self.stream)

  def __str__(self):
    if len(self.stream)==0: return "Empty stream"
    return self._dumpHex(self.stream)

