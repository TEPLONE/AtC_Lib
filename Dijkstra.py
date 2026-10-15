from heapq import *
def dijkstra(graph, start=0, calc_parent=False):
    """graph->[[(vertex,cost)]]"""
    n = len(graph)
    visited = [-1]*n
    queue = []
    heapify(queue)
    heappush(queue, (0,start))
    visited[start] = 0
    if calc_parent:
        parent = [None]*n
        parent[start] = -1
    while queue:
        cost,now = heappop(queue)
        if visited[now]!=-1 and visited[now]<cost:
            continue
        for next,dc in graph[now]:
            nc = dc+cost
            if visited[next]==-1 or nc<visited[next]:
                visited[next] = nc
                if calc_parent:
                    parent[next] = now
                heappush(queue, (nc,next))
    if calc_parent:
        return visited,parent
    else:
        return visited
