from concurrent.futures import ThreadPoolExecutor
import time
import concurrent.futures

def print_numbers():
    for i in range(100):
        print(i)
        time.sleep(1)  # Simulating some processing time

def handle_input():
    while True:
        user_input = input("Enter 'hi' to print 'hi': ")
        if user_input.lower() == 'hi':
            print("hi")

if __name__ == '__main__':
    with ThreadPoolExecutor(max_workers=2) as executor:
        # Start the print_numbers function in one thread
        future_print = executor.submit(print_numbers)

        # Start the handle_input function in another thread
        future_input = executor.submit(handle_input)

        # Wait for both tasks to complete
        concurrent.futures.wait([future_print, future_input], return_when=concurrent.futures.FIRST_COMPLETED)