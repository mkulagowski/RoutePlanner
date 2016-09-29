import googlemaps, json, sys
from pprint import pprint
from datetime import datetime

gmaps = googlemaps.Client(key='AIzaSyAiwjHH1WCiT5fRvbDsuYkNHxzeHeBVGTQ')

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


def main(argv):
    waypoints = []
    destinations = []

    with open("waypoints.txt", "r") as waypointsFile:
        waypoints = waypointsFile.readlines()
    print "\n=====Loaded waypoints.txt:"

    depTime = datetime.now()

    waypoints = [line.rstrip('\n') for line in waypoints]

    print waypoints

    print "\n=====Sending DistanceMatrix to gmaps"
    directionsMatrix = []
    for point in waypoints:
        distMatResult = gmaps.distance_matrix(origins = [ point ],
                                                 destinations = waypoints,
                                                 mode = "transit",
                                                 units = "metric")
        directionsMatrix.append(distMatResult["rows"][0])

    print "\n=====Building graph from results"
    roadsList = []
    for directionNode in directionsMatrix:
        roadSublist = []
        for element in directionNode["elements"]:
            val = element["duration"]["value"]
            roadSublist.append(val)
        roadsList.append(roadSublist)


    index = 0
    solutionList = [index]
    print "\n=====Calculating road"
    while index >= 0:
        roadSublist = roadsList[index]
        for roadIdx in range(0, len(roadSublist)):
            if roadIdx in solutionList:
                roadSublist[roadIdx] = 0
                
        index = NearestNeighbor(roadSublist)
        if index > 0:
            solutionList.append(index)      
            
        

    print "\n=====Shortest route would be:"
    for idx, solutionIdx in enumerate(solutionList):
        print "{}. {}".format(idx, waypoints[solutionIdx])

    return


if __name__ == '__main__':
    main(sys.argv)










##for a in roadsDict:
##    id1 = ord(a[0]) - 97
##    id2 = int(a[1])
##    str1 = "{} -> {} = {}min."
##    print str1.format(str(id1), str(id2), str(roadsDict[a] / 60))
##
##startNode = nodes[0]
##minVal = 100000000;
##minNode = startNode;
##for routes in roadsDict:
##    id1 = ord(a[0]) - 97
##    id2 = int(a[1])
##    val = roadsDict[routes]
##    if val < minVal:
##        minNode = id2
##        val = minVal
##        
##        minVal = val
##
##
##direct = gmaps.directions(origins[0], destinations[0], mode="transit", language="it")[0]
##
##print "Received directions:"
##legs = direct["legs"][0]
##for i in legs["steps"]:
##    html = i["html_instructions"]
##    print html + " " + i["travel_mode"]
##    if "steps" in i:
##        for j in i["steps"]:
##            if "html_instructions" in j and "travel_mode" in j:
##                print "\t" + j["html_instructions"] + " " + j["travel_mode"]
##
##matrixStr = "Matrix dur=" + legs2["duration"]["text"] + ", dist=" + legs2["distance"]["text"]
##dirStr = "Direction dur=" + legs["duration"]["text"] + ", dist=" + legs["distance"]["text"]
##
##print matrixStr
##print dirStr
##
