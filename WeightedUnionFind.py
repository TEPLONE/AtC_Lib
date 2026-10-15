import sys
sys.setrecursionlimit(10 ** 7)

class WeightedUnionFind:
    def __init__(self, N):
        self.N = N
        self.parents = [-1] * N
        self.rank = [0] * N
        self.weight = [0] * N

    def root(self, x):
        if self.parents[x] == -1:
            return x
        rx = self.root(self.parents[x])
        self.weight[x] += self.weight[self.parents[x]]
        self.parents[x] = rx
        return self.parents[x]
    
    def get_weight(self, x):
        self.root(x)
        return self.weight[x]

    def unite(self, x, y, d):
        '''
        A[x] - A[y] = d
        must be is_same(x,y)==False
        '''
        w = d + self.get_weight(x) - self.get_weight(y)
        rx = self.root(x)
        ry = self.root(y)
        if rx == ry:
            _, d_xy = self.diff(x, y)
            if d_xy == d:
                return True
            else:
                return False
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx
            w = -w
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1
        
        self.parents[ry] = rx
        self.weight[ry] = w
        return True

    def is_same(self, x, y):
        return self.root(x) == self.root(y)
    
    def diff(self, x, y):
        if self.is_same(x, y):
            return self.get_weight(y) - self.get_weight(x)
        else:
            return 0