class ModComb:
    def __init__(self, maxn, MOD):
        """nCk (mod M) by O(N^2)(precalc), O(1)(ans)"""
        self.MOD = MOD
        binom = [[0]*(maxn+1) for _ in range(maxn+1)]
        for n in range(1,maxn+1):
            binom[n][0] = 1
            binom[n][n] = 1
            for k in range(1,n):
                binom[n][k] = (binom[n-1][k-1]+binom[n-1][k])%MOD
        self.binom = binom
    def Comb(self, n, k):
        k = min(k, n-k)
        if not(0<=k<=n):
            return 0
        return self.binom[n][k]
