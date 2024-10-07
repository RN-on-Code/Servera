s = "0ABCDEFGHIJKLMNOPQRSTUVWXYZ"
n = int(input("Enter the count no. of your name:"))
list1 = []
for i in range(n):
  word = input("enter the input")
  list1 += [int(word)]
for j in range(n):
    print(s[list1[j]])