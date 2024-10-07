# Open a file in read mode ('r')

hey = "hey"
there = "there"
with open('replies.txt', 'a') as file:
                         file.write(hey + there)
file_path = 'replies.txt'
search_query = 'Hey'  # Replace with the line you're searching for

# Open a file in exclusive creation mode ('x')
# This will create a new file, but if the file already exists, it will raise a FileExistsError.


try:
    with open(file_path, 'r') as file:
        # Read all lines in the file
        lines = file.readlines()
        print(lines)

        # Check each line for the search query
        found = False
        for line_number, line in enumerate(lines, start=1):
            if search_query in line:
                print(f'Line found at line {line_number}: {line}')
                found = True
                break

        if not found:
            print('Line not found in the file.')

except FileNotFoundError:
    print(f'The file "{file_path}" does not exist.')
except Exception as e:
    print(f'An error occurred: {e}')
