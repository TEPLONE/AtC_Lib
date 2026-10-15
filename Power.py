def Power(a,b,MOD):
    "return a**b (mod MOD)"
    d = [-1]*(len(bin(b))-2)
    d[0] = a
    for i in range(1,len(d)):
        d[i] = d[i-1]**2 % MOD
    ans = 1
    for i in range(len(d)):
        if b&(1<<i):
            ans *= d[i]
            ans %= MOD
    return ans
