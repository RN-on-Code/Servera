# your_program.py

import multiprocessing
import other_program

def run_main_function():
    other_program.main_function()

if __name__ == "__main__":
    # Create a new process for running the main function
    process = multiprocessing.Process(target=run_main_function)

    # Start the process
    process.start()

    # Continue with the execution of your main program
    print("Your main program is running...")

    # Optionally, wait for the process to finish
    process.join()

    print("Your main program completed.")
