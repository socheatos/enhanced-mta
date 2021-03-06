import NYCT
import API_functions as ap
from scipy.spatial import distance

#takes in two lists: [float latitude, float longitude]
#returns the distance between the two points
def euclidean(origin,destination):
    return distance.euclidean(tuple(origin),tuple(destination))

#checks the accessibility of a station
def accessible(points):
    available=[]
    for p in points:
        if p[0].accessibility!=0:
            available.append(p)
    return available

#separates stops into same and different groups for bus lines
#((origin stop, destination stop), sum of distances,routecolors,express)
def getsubwayroutes(subways):
    #colors key and access
    colors={"GS":"shuttle","FX":"orange",'A':'blue','C':'blue','E':'blue','B':'orange', 'D':'orange',"F":'orange',"M":'orange','G':'lime',"L":'gray',"J":'brown',"Z":'brown',"N":'yellow',"Q":"yellow","R":"yellow","W":"yellow","1":"red","2":"red","3":"red","4":"green","5":"green","6":"green","7":"purple"}

    same_sub=[]
    diff_sub=[]
    for s in subways:
        new=((s[0][0],s[0][1]),s[1],s[0][0].line!=s[0][1].line,2-s[0][0].express-s[0][1].express)
        if s[0][0].route_id==s[0][1].route_id:
            if new not in same_sub:
                same_sub.append(new)
        else:
            if new not in diff_sub:
                diff_sub.append(new)
    return same_sub,diff_sub

#separates stops into same and different groups for bus lines
#((origin stop, destination stop), sum of distances)
def getbusroutes(buses):
    
    sameroutes=[]
    diffroutes=[]

    for b in buses:
        if b[0][0].route_id==b[0][1].route_id:
            if b not in sameroutes:
                sameroutes.append(b)
        else:
            if b not in diffroutes:
                diffroutes.append(b)

    #sorts lists based on distance            
    return sameroutes,diffroutes


#takes in (graph node,str origin address,str destination address,float radius of search)
#returns a list of tuples (origin stop, destination stop)
    #ordered by (transfers, distance)
def findroutes(access,mode,origin,destination,graph,rad=0.001):
    
    #get geo_code of origin and destination
    loc=ap.get_geocode(origin)
    loc2=ap.get_geocode(destination)
    
    #finds nearby origin stops
    originpts=[]
    destpts = []
    for x in graph.stopIDs:
        node=graph.getStop(x)
        node_accessibility = node.accessibility
        add_node_access_flag = False
        if access == 'N' or access== 'n':
            add_node_access_flag = True
        else:
            if node_accessibility !=0:
                add_node_access_flag = True

        distance2origin = euclidean(loc, node.geocode)
        distance2dest = euclidean(loc2, node.geocode)
       
        if distance2origin<=rad and add_node_access_flag==True:
            new=(node,distance2origin)
            if new not in originpts:
                originpts.append(new)

        if distance2dest<=rad and add_node_access_flag==True:
            new=(node,distance2dest)
            if new not in destpts:
                destpts.append(new)

    #shortens origin and destination list based on radius
    if len(originpts)==0 or len(destpts)==0:
        print(f"Radius {rad} is too small")
        return []

    #separates routes by transportation type   
    subways=[]
    buses=[]
    mixedmode=[]
    # print(f'There are {len(originpts)} starting and {len(destpts)} ending')
    for o in originpts:
        for d in destpts:
            new=((o[0],d[0]),o[1]+d[1])
            # new=((o[0],d[0]),euclidean(o[0].geocode,d[0].geocode))
            if o[0].transit_type==d[0].transit_type:
                if o[0].transit_type=='bus':
                    buses.append(new)
                else:
                    subways.append(new)
            else:
                mixedmode.append(new)

    # print(f'bus {len(buses)}')
    # print(f'subs {len(subways)}')
    # print(f'mixed {len(mixedmode)}')

    if mode=="bus":
       samebus,diffbus=getbusroutes(buses)
       samebus.sort(key=lambda x: (x[1]))
       diffbus.sort(key=lambda x: (x[1]))
       return samebus+diffbus

    elif mode=="subway":
        samesub,diffsub=getsubwayroutes(subways)
        samesub.sort(key=lambda x:(x[1]))
        diffsub.sort(key=lambda x:(x[1],x[2],x[3]))
        return samesub+diffsub
    
    else:
        #separates stops from same route and different route
        #(node-pair,sum of both distances,if the routes are in the same color group F if yes, T if no,express: if none are express 2, if one is express 1, if both are express 0)
        samesub,diffsub = getsubwayroutes(subways)
        samebus,diffbus = getbusroutes(buses)

        #sorts same routes by distance
        sameroutes=samesub+samebus
        sameroutes.sort(key=lambda x:(x[1]))
    
        #sorts diffrent routes by distance
            #diffsub sorted by distance line and express
            #diffbus sorted by distance

        
        diffsub.sort(key=lambda x:(x[2],x[1],x[3]))
        diffbus.sort(key=lambda x:(x[1]))
        diffroutes = diffbus+diffsub

        #mixed mode sorted by distance
        # mixedmode.sort(key=lambda x:(x[1]))
        print(f'same {len(sameroutes)}')
        print(f'diff {len(diffroutes)}')
        print(f'mixed {len(mixedmode)}')

        
        # combines all modes together and sorts by distance
        allmodes = mixedmode+sameroutes+diffroutes
        allmodes.sort(key=lambda x:(x[1]))   
    
        return allmodes


