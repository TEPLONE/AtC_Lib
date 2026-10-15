class ModComb:
    __slots__ = ("MOD", "fact", "invfact","limn")

    def __init__(self, n, MOD):
        self.MOD = MOD

        limn = min(10**5, n)
        fact = [1] * (limn + 1)
        invfact = [1] * (limn + 1)

        for i in range(1, limn + 1):
            fact[i] = fact[i - 1] * i % MOD

        invfact[limn] = pow(fact[limn], MOD - 2, MOD)

        for i in range(limn, 0, -1):
            invfact[i - 1] = invfact[i] * i % MOD

        self.fact = fact
        self.invfact = invfact
        self.limn = limn
    def get_invfact(self,k):
        if not(0<=k<len(self.invfact)):
            raise IndexError
        return self.invfact[k]

    def Comb(self, n, k):
        k = min(k, n-k)
        MOD = self.MOD
        if not 0 <= k <= n:
            return 0
        if n<=self.limn:
            ans = self.fact[n] * self.invfact[k] % MOD * self.invfact[n-k] % MOD
            ans %= MOD
        else:
            ans = 1
            for i in range(k):
                ans *= n-i
                ans %= MOD
            limk = self.limn
            if k>limk:
                ans *= self.invfact[limk]
                ans %= MOD
                for i in range(limk+1,k+1):
                    ans *= pow(i, MOD-2, MOD)
                    ans %= MOD
            else:
                ans *= self.invfact[k]
                ans %= MOD
        return ans
