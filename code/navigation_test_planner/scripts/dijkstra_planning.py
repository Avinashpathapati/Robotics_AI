import rospy
from alice_msgs.srv import MakePlan, MakePlanResponse
import numpy as np
import heapq
import math
import sys

class Dijkstra(object): 
    
    def __init__(self):

        self.make_plan_service = rospy.Service("/move_base/GlobalPlannerPython/make_plan", MakePlan, self.make_plan)

    def minDistance(self, dist, sptSet): 
  
        # Initilaize minimum distance for next node 
        min = sys.maxint 
  
        # Search not nearest vertex not in the  
        # shortest path tree 
        for v in range(self.V):
            if dist[v] < min and sptSet[v] == False: 
                min = dist[v] 
                min_index = v 
  
        return min_index

    def find_neighbours(self,pixel,width):

        neighbours = []
        temp = []
        temp.append([pixel - 1, 1])
        temp.append([pixel + 1, 1])
        temp.append([pixel + width - 1, math.sqrt(2)])
        temp.append([pixel + width,1])
        temp.append([pixel + width + 1, math.sqrt(2)])
        temp.append([pixel - width,1])
        temp.append([pixel - width - 1, math.sqrt(2)])
        temp.append([pixel - width + 1, math.sqrt(2)])
        for p in temp:
        # if ( p not in self.blocked ) and ( p in pixels ):
            if p[0] >= 0 and p[0] < self.V and self.graph[p[0]] == 0:
                neighbours.append(p)
        return neighbours

    def make_plan(self, req):
    ## This is the data you get from the request
               
        costmap = req.costmap_ros   ## The costmap, a single array version of an image
        width = req.width
        height = req.height
        map_size = height * width
        start_index = req.start
        goal_index = req.goal
        self.V = map_size
        self.graph = costmap
        dist = [sys.maxint] * self.V
        dist[start_index] = 0
        sptSet = [False] * self.V 
        parent_arr = [sys.maxint] * self.V
        h = []
        heapq.heappush(h, (costmap[start_index],start_index))


        while h:
  
            # Pick the minimum distance vertex from  
            # the set of vertices not yet processed.  
            # u is always equal to src in first iteration
            u = heapq.heappop(h)[1]
            #u = self.minDistance(dist, sptSet)
  
            # Put the minimum distance vertex in the  
            # shotest path tree 
            sptSet[u] = True
            # print neighbours

            if u == goal_index:
                break
            neighbours = self.find_neighbours(u,width)
            # Update dist value of the adjacent vertices  
            # of the picked vertex only if the current  
            # distance is greater than new distance and 
            # the vertex in not in the shotest path tree
            for v in neighbours:
        
                if sptSet[v[0]] == False and dist[v[0]] > dist[u] + v[1]:
                    parent_arr[v[0]] = u
                    dist[v[0]] = dist[u] + v[1]
                    heapq.heappush(h, (dist[v[0]],v[0]))
  
        #make a response object
        resp = MakePlanResponse()
        path_arr = []
        cur_goal = goal_index
        path_arr.insert(0,goal_index)
        for count in range(self.V):
            parent = parent_arr[cur_goal]
            if parent == start_index:
                path_arr.insert(0,parent)
                break
            elif parent == sys.maxint:
                break
            path_arr.insert(0,parent)
            cur_goal = parent
        
        resp.plan = path_arr
        
        print 'done'
        return resp

if __name__ == "__main__":

    rospy.init_node("dijkstra_planner")
    
    dijkstra = Dijkstra()
    
    rospy.spin()
