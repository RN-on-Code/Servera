class Myclass:
    def fun(hi,self):
        hi  = "Hi there"
        return hi
        

    def fun3(self,s):
        s = self.fun(hi="")
        return s
obj = Myclass()
print(obj.fun3(s=""))
