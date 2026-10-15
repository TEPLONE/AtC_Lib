class FenwickTree:
    """
    Fenwick Tree (BIT)

    対応:
        ・加算
        ・XOR
        ・乗算(mod)

    mode:
        "add" : 加算
        "xor" : XOR
        "mul" : 乗算(mod)

    例:
        fw = FenwickTree(n, "add")
        fw = FenwickTree(n, "xor")
        fw = FenwickTree(n, "mul", MOD)
    """

    __slots__ = ("n", "data", "mode", "mod")

    def __init__(self, n: int, mode="add", mod=None):

        self.n = n
        self.mode = mode
        self.mod = mod

        if mode == "mul":
            self.data = [1] * (n + 1)
        else:
            self.data = [0] * (n + 1)

    def add(self, p: int, x: int):

        p += 1

        data = self.data
        n = self.n
        mode = self.mode

        if mode == "add":

            while p <= n:
                data[p] += x
                p += p & -p

        elif mode == "xor":

            while p <= n:
                data[p] ^= x
                p += p & -p

        else:
            mod = self.mod

            while p <= n:
                data[p] = data[p] * x % mod
                p += p & -p

    def pref(self, r: int):

        data = self.data
        mode = self.mode

        if mode == "mul":

            mod = self.mod
            s = 1

            while r:
                s = s * data[r] % mod
                r -= r & -r

        else:

            s = 0

            if mode == "add":

                while r:
                    s += data[r]
                    r -= r & -r

            else:

                while r:
                    s ^= data[r]
                    r -= r & -r

        return s

    def prod(self, l: int, r: int):

        mode = self.mode

        if mode == "add":
            return self.pref(r) - self.pref(l)

        if mode == "xor":
            return self.pref(r) ^ self.pref(l)

        mod = self.mod

        return self.pref(r) * pow(self.pref(l), mod - 2, mod) % mod