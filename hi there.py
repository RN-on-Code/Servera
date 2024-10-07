matrix = [[1,1,1],[1,1,0],[1,0,1]]
list1 = matrix[0]
list2 = matrix[1]
list3 = matrix[2]
for i in range(3):
    for j in range(3):
        if matrix[i][j] == 1:
            matrix[i][j] = 2


   

print(matrix)