class manacher:
    """Module for palindrome."""
    """ Ref : https://qiita.com/klattimia/items/3cbe4f702e2f20761f0d"""
    """Cache radius array of palindrome to judge in linear time."""
    def __init__(self, l):
        """Insert '&' to judge both even and odd length palindrome."""
        self.n = len(l)
        self.m = 2*self.n+1
        self.d = ['&']*self.m
        self.r = [0]*self.m
        for i in range(self.n):
            self.d[2*i+1] = l[i]
        self.make_r()
    
    def make_r(self):
        """Make self.r[i] (radius of palindrome whose center is self.d[i])."""
        i, j = 0, 0
        while i < self.m:
            while j <= i < self.m-j and self.d[i-j] == self.d[i+j]:
                j += 1
            self.r[i] = j
            k = 1
            while k <= i < self.m-k and k+self.r[i-k] < j:
                self.r[i+k] = self.r[i-k]
                k += 1
            i += k
            j -= k

    def judge(self, start, end):
        """Return 1 if l[start, end) is a palindrome."""
        center = start+end
        return 2*end-1 < center+self.r[center]

