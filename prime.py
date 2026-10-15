class Eratosthenes:
    def __init__(self, n: int):

        self.n = n
        self.spf = list(range(n + 1))
        self.is_prime_table = [True] * (n + 1)

        if n >= 0:
            self.is_prime_table[0] = False
        if n >= 1:
            self.is_prime_table[1] = False

        for i in range(2, int(n ** 0.5) + 1):
            if self.spf[i] == i:
                for j in range(i * i, n + 1, i):
                    if self.spf[j] == j:
                        self.spf[j] = i
                        self.is_prime_table[j] = False

        self.primes = [i for i in range(2,n+1) if self.spf[i]==i]

    def get_primes(self) -> list:
        return self.primes

    def is_prime(self, x: int) -> bool:
        if x < 0 or x > self.n:
            raise ValueError("x is out of range")
        return self.is_prime_table[x]

    def factorize(self, x: int) -> dict:
        if x < 1 or x > self.n:
            raise ValueError("x is out of range")

        res = {}
        while x > 1:
            p = self.spf[x]
            res[p] = res.get(p, 0) + 1
            x //= p
        return res

    def divisors(self, x: int) -> list:
        if x < 1 or x > self.n:
            raise ValueError("x is out of range")

        factors = self.factorize(x)
        divisors = [1]

        for p, cnt in factors.items():
            new_divs = []
            for d in divisors:
                val = 1
                for _ in range(cnt):
                    val *= p
                    new_divs.append(d * val)
            divisors += new_divs

        return sorted(divisors)