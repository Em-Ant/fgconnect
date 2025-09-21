################################################################################
#
# (C) 2021, Tiago Gasiba
#           tiago.gasiba@gmail.com
#
################################################################################
import pprint
import math
import os

earthRadiusKm = 6373.0

# based on: https://stackoverflow.com/questions/19412462/getting-distance-between-two-points-based-on-latitude-longitude
def distanceKm( p1, p2 ):
  lon1 = math.radians(p1[0])
  lat1 = math.radians(p1[1])
  lon2 = math.radians(p2[0])
  lat2 = math.radians(p2[1])

  dlon = lon2 - lon1
  dlat = lat2 - lat1
  a    = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
  c    = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
  
  return earthRadiusKm * c

def translateToAirplane( fgData ):
  flightModel = fgData["/sim/flight-model"]
  if "jsb" in flightModel:
    airplaneTotalWeightLbs = fgData["/fdm/jsbsim/inertia/weight-lbs"]
    fuelFlowGPH            = fgData["/fdm/jsbsim/propulsion/engine/fuel-flow-rate-gph"]
    fuelFlowPPH            = fgData["/fdm/jsbsim/propulsion/engine/fuel-flow-rate-pps"]
  else:
    airplaneTotalWeightLbs = fgData["/fdm/yasim/gross-weight-lbs"]
    fuelFlowGPH            = fgData["/engines/engine/fuel-flow-gph"]
    fuelFlowPPH            = fgData["/engines/engine[1]/fuel-flow-gph"]  # FIXME
  myAirplane = { "lonx"                       : fgData["/position/longitude-deg"],
                 "laty"                       : fgData["/position/latitude-deg"],
                 "altitudeAboveGroundFt"      : fgData["/position/altitude-agl-ft"],
                 "groundAltitudeFt"           : fgData["/position/ground-elev-ft"],
                 "headingTrueDeg"             : fgData["/orientation/heading-deg"],
                 "headingMagDeg"              : fgData["/orientation/heading-magnetic-deg"],
                 "groundSpeedKts"             : fgData["/velocities/groundspeed-kt"],
                 "indicatedAltitudeFt"        : fgData["/instrumentation/altimeter/indicated-altitude-ft"],
                 "indicatedSpeedKts"          : fgData["/instrumentation/airspeed-indicator/indicated-speed-kt"],
                 "trueAirspeedKts"            : fgData["/instrumentation/airspeed-indicator/true-speed-kt"],
                 "machSpeed"                  : fgData["/instrumentation/airspeed-indicator/indicated-mach"],
                 "verticalSpeedFeetPerMin"    : fgData["/instrumentation/vertical-speed-indicator/indicated-speed-fpm"],
                 "windSpeedKts"               : fgData["/environment/wind-speed-kt"],
                 "windDirectionDegT"          : fgData["/environment/wind-from-heading-deg"],
                 "ambientTemperatureCelsius"  : fgData["/environment/temperature-degc"],
                 "seaLevelPressureMbar"       : fgData["/environment/pressure-sea-level-inhg"] / 0.029530,
                 "airplaneTotalWeightLbs"     : airplaneTotalWeightLbs,
                 "fuelTotalQuantityGallons"   : fgData["/consumables/fuel/total-fuel-gals"],
                 "fuelTotalWeightLbs"         : fgData["/consumables/fuel/total-fuel-lbs"],
                 "fuelFlowGPH"                : fuelFlowGPH,
                 "fuelFlowPPH"                : fuelFlowPPH,
                 "magVarDeg"                  : fgData["/environment/magnetic-variation-deg"],
                 "ambientVisibilityMeter"     : fgData["/environment/effective-visibility-m"],
                 "trackMagDeg"                : fgData["/orientation/track-magnetic-deg"],
                 "trackTrueDeg"               : fgData["/orientation/true-heading-deg"],
                 "title"                      : fgData["/sim/description"],
                 "model"                      : fgData["/sim/aircraft"],
                 "reg"                        : fgData["/sim/multiplay/callsign"],
                 "type"                       : "",
                 "airline"                    : "",
                 "flightNr"                   : "",
                 "fromIdent"                  : "",
                 "toIdent"                    : "",
               }
  return myAirplane

def translateToAI( fgAllData ):
  myAI = []
  for ii in range(len(fgAllData)):
    fgData = fgAllData[ii]
    myAirplane = { "objectID"                   : fgData["id"],
                   "shortFlags"                 : 0x0040,
                   "lonx"                       : fgData["position/longitude-deg"],
                   "laty"                       : fgData["position/latitude-deg"],
                   "headingTrueDeg"             : fgData["orientation/true-heading-deg"],
                   "fromIdent"                  : fgData["departure-airport-id"],
                   "toIdent"                    : fgData["arrival-airport-id"],
                   "altitude"                   : fgData["position/altitude-ft"],
                   "altitudeAboveGroundFt"      : fgData["position/altitude-ft"],
                   "groundAltitudeFt"           : fgData["position/altitude-ft"],
                   "flightNr"                   : fgData["callsign"],
                   "groundSpeedKts"             : fgData["velocities/true-airspeed-kt"],
                   "verticalSpeedFeetPerMin"    : fgData["velocities/vertical-speed-fps"]/60.0,
                   "reg"                        : fgData["callsign"],
                   "model"                      : "AI",
                   "type"                       : "",
                   "airline"                    : "",
                   "title"                      : "",
                   "headingMagDeg"              : 0.0,
                   "indicatedAltitudeFt"        : 0.0,
                   "indicatedSpeedKts"          : 0.0,
                   "trueAirspeedKts"            : 0.0,
                   "machSpeed"                  : 0.0,
                   "windSpeedKts"               : 0.0,
                   "windDirectionDegT"          : 0.0,
                   "ambientTemperatureCelsius"  : 0.0,
                   "seaLevelPressureMbar"       : 1013.25,
                   "airplaneTotalWeightLbs"     : 0.0,
                   "fuelTotalQuantityGallons"   : 0.0,
                   "fuelTotalWeightLbs"         : 0.0,
                   "fuelFlowGPH"                : 0.0,
                   "fuelFlowPPH"                : 0.0,
                   "magVarDeg"                  : 0.0,
                   "ambientVisibilityMeter"     : 0.0,
                   "trackMagDeg"                : 0.0,
                   "trackTrueDeg"               : 0.0,
                 }
    myAI.append(myAirplane)
  return myAI
