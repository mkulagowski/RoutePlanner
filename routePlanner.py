import googlemaps, json, sys, re
from pprint import pprint
from datetime import datetime

gmaps = googlemaps.Client(key='AIzaSyAiwjHH1WCiT5fRvbDsuYkNHxzeHeBVGTQ')

def RemoveTags(raw_html):
  cleanr =re.compile('<.*?>')
  cleantext = re.sub(cleanr,'', raw_html)
  return cleantext

def QueryDistanceMatrix(waypoints):
    directionsMatrix = []
    for point in waypoints:
        distMatResult = gmaps.distance_matrix(origins = [ point ],
                                              destinations = waypoints,
                                              mode = "transit",
                                              units = "metric")
        directionsMatrix.append(distMatResult["rows"][0])
    return directionsMatrix

def QueryDirections(origin, destination):
    direct = gmaps.directions(origin,
                              destination,
                              mode = "transit",
                              language = "eng")
    return direct[0]["legs"][0]["steps"]

def BuildRoadsMatrix(directionMatrix):
    roadsList = []
    for directionNode in directionMatrix:
        roadSublist = []
        if "elements" in directionNode:
            for element in directionNode["elements"]:
                if "duration" in element:
                    val = element["duration"]["value"]
                    roadSublist.append(val)
        roadsList.append(roadSublist)
    return roadsList

def NearestNeighbor(valList):
    minNod = 0
    minVal = 100000
    for idx, val in enumerate(valList):
        if val > 0 and val < minVal:
            minVal = val
            minNod = idx

    if minNod == 0:
        return -1
    
    return minNod

def CalculateShortestRoute(roadsMatrix):
    index = 0
    solutionList = [index]
    while index >= 0:
        roadSublist = roadsMatrix[index]
        for roadIdx in range(0, len(roadSublist)):
            if roadIdx in solutionList:
                roadSublist[roadIdx] = 0
                
        index = NearestNeighbor(roadSublist)
        if index > 0:
            solutionList.append(index)

    return solutionList

def printComment(text, isHeader = True, tabNo = 0):
    log = ''
    if isHeader is True:
        log += "\n====="
    elif tabNo > 0:
        log += (tabNo * '\t')

    log += text
    print(log)

def printWalkNode(node):
    for walkStep in node:
        if "html_instructions" in walkStep:
            stepTxt = RemoveTags(walkStep["html_instructions"])
            destPos = stepTxt.rfind("Destination")
            if destPos >= 0:
                stepTxt1 = stepTxt[:destPos]
                stepTxt = stepTxt[destPos:]
                printComment(stepTxt1, False, 2)
            printComment(stepTxt, False, 2)


def printTransitNode(node):
    depS = node["departure_stop"]["name"]
    arrS = node["arrival_stop"]["name"]
    veh1 = node["line"]["vehicle"]["name"]
    veh2 = node["line"]["short_name"]
    printComment("Take {}-{} from stop \'{}\' to stop \'{}\'".format(veh1, veh2, depS, arrS), False, 2)

def main(argv):
  
    waypoints = []
    with open("waypoints.txt", "r") as waypointsFile:
        waypoints = waypointsFile.readlines()

    if waypoints is [] or waypoints is '':
      return
    
    printComment("Loaded waypoints.txt:")
    waypoints = [line.rstrip('\n') for line in waypoints]
    print(waypoints)
    print("DONE")
            
    printComment("Sending DistanceMatrix to gmaps")
    directionsMatrix = QueryDistanceMatrix(waypoints)
    print("DONE")
    
    printComment("Building graph from results")
    roadsMatrix = BuildRoadsMatrix(directionsMatrix)
    print("DONE")
    
    printComment("Calculating road")      
    solutionList = CalculateShortestRoute(roadsMatrix)
    print("DONE")
    
    printComment("Shortest route would be:")
    for idx, solutionIdx in enumerate(solutionList):
        print("{}. {}".format(idx, waypoints[solutionIdx]))

    printComment("Directions:")

    for idx in range(0, len(solutionList) - 1):
        orig = waypoints[solutionList[idx]]
        dest = waypoints[solutionList[idx + 1]]
        directions = QueryDirections(orig, dest)

        printComment("From: {}, To: {}".format(orig[:orig.find(',')], dest[:dest.find(',')]), False)
        for direction in directions:
            directionMainTxt = direction["html_instructions"]
            printComment(RemoveTags(directionMainTxt), False, 1)
            if "steps" in direction:
                printWalkNode(direction["steps"])   
            elif "transit_details" in direction:
                printTransitNode(direction["transit_details"])
    
    return

if __name__ == '__main__':
    main(sys.argv)
