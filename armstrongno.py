a = int(input("enter the no."))
b=0
temp = a 
while temp>0:
    n= temp%10
    b += n*n*n
    temp=temp//10

if a == b:
    print("is a Armstrong no.")
    print(temp)
else:
    print("hi")    





