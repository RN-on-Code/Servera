alpha = "0ABCDEFGHIJKLMNOPQRSTUVWXYZ"
i = int(input("enter the no. of alphas in your name:"))
list1 = []
list2 = []
string = ""
list2 = []
for j in range(i):
    list1 += input("Enter the occurence of the alphabets of your name:")

for k in range(i):
    string+=list1[k]
    string = int(string)
    list2 += string

print(list2)
