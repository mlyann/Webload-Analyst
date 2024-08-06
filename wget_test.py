import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
import pyfiglet
from datetime import datetime
import time
import os
import requests
import re


import wget_plot
import wget_valid_input


from config import data_folder

"""
Webpage Loading Time Tester

Author: Minglai Yang

This script measures and analyzes the loading times of a specific webpage at regular intervals for a given duration. It utilizes `wget` to fetch the page, records the loading times, and provides statistics and visualizations to evaluate performance.

Modules:
- `wget_valid_input`: A module to handle user input with validation for meeting URL, duration, and response times.

Functions:
- `collect_load_times(MeetingURL, duration_minutes, recordfile)`: Collects loading times for a given meeting URL over a specified duration. Records data to a file.
  - Parameters:
    - `MeetingURL` (str): The URL of the meeting page to test.
    - `duration_minutes` (float): The duration in minutes for which to run the test.
    - `recordfile` (str): The filename to which the collected data will be saved.
  - Returns:
    - `timestamps` (list of str): Timestamps of each request.
    - `load_times` (list of float): Corresponding loading times.

- `calculate_statistics(load_times, loading_time_line)`: Computes statistics from the recorded loading times.
  - Parameters:
    - `load_times` (list of float): List of loading times.
    - `loading_time_line` (float): The maximum acceptable loading time.
  - Returns:
    - `stats` (dict): A dictionary containing count of exceeding times, mean, median, max, and min loading times.

- `plot_load_times(timestamps, load_times, stats)`: Plots the loading times against timestamps and prints statistics.
  - Parameters:
    - `timestamps` (list of str): Timestamps of each request.
    - `load_times` (list of float): Corresponding loading times.
    - `stats` (dict): Statistics about the loading times.

- `generate_filename(url, minutes)`: Generates a filename based on the URL and duration for saving the collected data.
  - Parameters:
    - `url` (str): The meeting URL.
    - `minutes` (float): The duration of the test in minutes.
  - Returns:
    - `filename` (str): The generated filename.

- `print_loading_times(timestamps, load_times, filename)`: Prints the collected loading times and saves them to a file.
  - Parameters:
    - `timestamps` (list of str): Timestamps of each request.
    - `load_times` (list of float): Corresponding loading times.
    - `filename` (str): The filename where the data was saved.

- `main()`: The main function that orchestrates the entire process. It collects loading times, calculates statistics, generates plots, and prints results.

Usage:
1. Modify the `wget_valid_input` module if needed to adjust how inputs are obtained and validated.
2. Run the script. It will prompt for a meeting URL, duration, and response times.
3. The script will output loading times, statistics, and visualizations to evaluate the performance of the webpage.

Notes:
- Ensure `wget` is installed and accessible in your environment.
- The `matplotlib` library is used for plotting graphs.
- If interrupted, the script will save the current data and exit gracefully.

"""



ascii_art = pyfiglet.figlet_format("MING")
print(ascii_art)

time.sleep(1)

def print_introduction():
    print("================================================================================")
    print("                           Webpage Load Time Monitor                           ")
    print("================================================================================")
    print("Author: Minglai Yang")
    print("Date: Aug 05, 2024")
    print("Description:")
    print("This script measures the loading times of a webpage over a specified duration.")
    print("It records the loading times and checks if they exceed a given acceptable response time.")
    print("The results are saved to a file and visualized using a plot.")
    print("================================================================================\n")

# Print introduction at the start of the program
print_introduction()




# https://blackstoneamoffice.com/editors/Reports/MeetingStatusReport.aspx?meetingid=2873
MeetingURL = wget_valid_input.get_meeting_url()
print("\nEnter Meeting URL Successfully!!\n")
DURATION_MINUTES = wget_valid_input.get_float_input("\nPlease Enter the Duration Time (minutes): ")  # Duration in minutes for the script to run
print("\nEnter Duration Time Successfully!!\n")
TIME_LINE = wget_valid_input.get_int_input("Please Tell Me Maximum Acceptable Response Time (seconds): ")
print("\nEnter Maximum Acceptable Response Time Successfully!!\n")
PAUSE_TIME_NOT_EXCEED = wget_valid_input.get_int_input("Number of Seconds to Pause Each Request If It Does NOT EXCEED Maximum Acceptable Response Time  (seconds): ")
print("\nEnter Acceptable Loading Page's Pausing Time Successfully!!\n")
PAUSE_TIME_EXCEED  = wget_valid_input.get_int_input("Number of Seconds to Pause Each Request If It EXCEED Maximum Acceptable Response Time (seconds): ")
print("\nEnter Unacceptable Loading Page's Pausing Time Successfully!!\n")


# Calculate the maximum length for the content lines
max_length = max(len("Meeting URL " + MeetingURL),
                 len(f"Duration (minutes) {DURATION_MINUTES}"),
                 len(f"Maximum acceptable response time (seconds) {TIME_LINE}"),
                 len(f"Pause time if exceeds the time line (seconds) {PAUSE_TIME_EXCEED}"),
                 len(f"Pause time if does not exceed the time line (seconds) {PAUSE_TIME_NOT_EXCEED}"))

# Define the total width of the box
box_width = max_length + 4
print("\n\n")
# Print the box
print("*" * box_width)
print("* " + "Meeting URL " + MeetingURL + " " * (box_width - 4 - len("Meeting URL " + MeetingURL)) + " *")
print(f"* Duration (minutes) {DURATION_MINUTES} " + " " * (box_width - 4 - len(f"Duration (minutes) {DURATION_MINUTES}")) + "*")
print(f"* Maximum acceptable response time (seconds) {TIME_LINE} " + " " * (box_width - 4 - len(f"Maximum acceptable response time (seconds) {TIME_LINE}")) + "*")
print(f"* Pause time if exceeds the time line (seconds) {PAUSE_TIME_EXCEED} " + " " * (box_width - 4 - len(f"Pause time if exceeds the time line (seconds) {PAUSE_TIME_EXCEED}")) + "*")
print(f"* Pause time if does not exceed the time line (seconds) {PAUSE_TIME_NOT_EXCEED} " + " " * (box_width - 4 - len(f"Pause time if does not exceed the time line (seconds) {PAUSE_TIME_NOT_EXCEED}")) + "*")
print("*" * box_width+"\n\n")


def collect_load_times(MeetingURL, duration_minutes, recordfile):
    """
    Collects load times for a given URL over a specified duration and records them.

    @param MeetingURL: The URL to be loaded.
    @param duration_minutes: The total duration for collecting load times in minutes.
    @param recordfile: The file to record the load times.
    @return: A tuple of timestamps and load times.
    """
    end_time = time.time() + duration_minutes * 60
    start_time = time.time()
    timestamps = []
    load_times = []
    i = 0
    count = 0
    try:
        with open(recordfile, 'w') as f:
            f.write("Meeting URL \t "+MeetingURL+" \n" )
            f.write(f"Duration (minutes) \t{DURATION_MINUTES}\n")
            f.write(f"Maximum acceptable response time (seconds) \t{TIME_LINE}\n")
            f.write(f"Pause time if exceeds the time line (seconds) \t{PAUSE_TIME_EXCEED}\n")
            f.write(f"Pause time if does not exceed the time line (seconds) \t{PAUSE_TIME_NOT_EXCEED}\n")
            f.write("\n")
            f.write("\n")
            f.write("Data Records: \n")
            f.write("Timestamp \tTotal Elapsing Time (seconds) \tTotal Remaining Time (seconds) \tLoading Times (seconds) \tPause Each Request (seconds) \tIS ACCEPTABLE? \tTotal Counts of Exceeding Time Line\n")

        while time.time() < end_time:
            ACCEPT = True
            current_time = time.time()
            elapsed_time = current_time - start_time
            remaining_time = end_time - current_time

            # Wget and Remove File
            start = time.time()
            filename = f"MeetingStatusReport_{i}.aspx"
            os.system(f'wget {MeetingURL} -O {filename}')
            end = time.time()
            os.system(f"rm {filename}")
            delta = end - start

            print("--------------------Current Data Report--------------------")
            print(f"Current Loading Time: {delta:.2f} seconds")
            print(f"Total Elapsed Time: {elapsed_time:.2f} seconds")
            print(f"Remaining Time: {remaining_time:.2f} seconds")
            print(f"Total Counts of Exceeding Time Line: {count}")
            print("-----------------------------------------------------------")

            if delta < TIME_LINE:
                pause = PAUSE_TIME_NOT_EXCEED  # Pause between requests
                print("")
                print(f"YES!! I am not exceeding your time line. Let's wait - {pause} - seconds.")
                print("")
            else:
                pause = PAUSE_TIME_EXCEED
                ACCEPT = False
                count += 1
                print("")
                print(f"Oops! I am exceeding your time line! Let's wait - {pause} - seconds. ")
                print("")

            time.sleep(pause)
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start))
            line = f"{timestamp} \t{elapsed_time:.2f} \t{remaining_time:.2f} \t {delta:.2f} \t {pause} \t {ACCEPT}\t{count} \n"

            with open(recordfile, 'a') as f:
                f.write(line)

            timestamps.append(timestamp)
            load_times.append(delta)

            i += 1

    except KeyboardInterrupt:
        print("\n")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("! Interrupted! Saving current data...  !")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("")

    return timestamps, load_times

def calculate_statistics(load_times, loading_time_line):
    """
    Calculates statistics from the collected load times.

    @param load_times: A list of load times.
    @param loading_time_line: The threshold for acceptable load times.
    @return: A dictionary with statistical measures.
    """
    stats = {}
    stats['count_exceeding'] = np.sum(np.array(load_times) > loading_time_line)
    stats['mean'] = np.mean(load_times)
    stats['median'] = np.median(load_times)
    stats['max'] = np.max(load_times)
    stats['min'] = np.min(load_times)

    return stats


def generate_filename(url, minutes, file_type='txt'):
    """
    Generates a sanitized filename based on the URL and duration.

    @param url: The URL to be used in the filename.
    @param minutes: The duration in minutes to be included in the filename.
    @param file_type: The file extension/type.
    @return: A sanitized filename string.
    """
    sanitized_url = re.sub(r'[^\w\s-]', '', url.replace('/', '_').replace(':', '_'))
    # Save files in the newly created directory
    return os.path.join(data_folder, f"LoadTimes_{sanitized_url}_{minutes}min.{file_type}")


def print_loading_times(timestamps, load_times, filename):
    """
    Prints the loading times and the corresponding timestamps.

    @param timestamps: A list of timestamps.
    @param load_times: A list of load times.
    @param filename: The name of the file where data is saved.
    """
    print("")
    print("Timestamp and Loading Times:")
    print("------------Head-------------")
    for timestamp, load_time in zip(timestamps, load_times):
        line = f"{timestamp}: {load_time:.2f} seconds\n"
        print(line, end='')
    print("-----------The End-----------")
    print("")

    # Print as a Regular Box
    max_length = max(len(f"| Data saved to {filename} |"), len(f"| Data saved to {filename[:-4]}.png |"))

    # Print the frame and messages
    print("-" * (max_length + 2))
    print(f"| Data saved to {filename}".ljust(max_length) + " |")
    print(f"| Data saved to {filename[:-4]}.png".ljust(max_length) + " |")
    print("-" * (max_length + 2))

def run():
    filename = generate_filename(MeetingURL, DURATION_MINUTES)
    timestamps, load_times = collect_load_times(MeetingURL, DURATION_MINUTES, filename)
    if timestamps and load_times:
        stats = calculate_statistics(load_times, TIME_LINE)
        wget_plot.plot_load_times(timestamps, load_times, stats, MeetingURL, DURATION_MINUTES, TIME_LINE=TIME_LINE,PAUSE_TIME_EXCEED=PAUSE_TIME_EXCEED,PAUSE_TIME_NOT_EXCEED=PAUSE_TIME_NOT_EXCEED)
        print_loading_times(timestamps, load_times, filename)
        print("")
        print("")
        print("Meeting URL Again for Checking!")
        print(MeetingURL)
        print("")
        
        response = input("Do you have the active user start and end time stamps? If so, I can plot the counts for you. Please reply Yes/No: ")
        if response.lower() == 'yes':
            print("\n\nRunning the program...\n")
            print("\nPlease enter your user counts as [(ID, START, END, Landed_OR_NOT),(ID, START, END, Landed_OR_NOT)], eg: [(11, '2024-08-02 17:42:32', '2024-08-02 17:43:32', False),...] into active_user_ranges.txt. \n")
            user_input = input("Do you copy all the output from selenium testing output? Please reply Yes/No.")
            if user_input.lower == "yes":
                wget_plot.plot_user_count(timestamps,load_times, MeetingURL, DURATION_MINUTES, TIME_LINE=TIME_LINE,PAUSE_TIME_EXCEED=PAUSE_TIME_EXCEED,PAUSE_TIME_NOT_EXCEED=PAUSE_TIME_NOT_EXCEED)
            else:
                print("Pass.. I will exit soon.")
                time.sleep(1)
        else:
            print("Pass.. I will exit soon.")
            time.sleep(1)
        print("\nThank you for using WGET testing product run by WGET.")
        print("Have a great day!")
        print("")

    else:
        print("")
        print("!!!!!!!!!!!!!!!!!!!!!!")
        print("! No data collected. !")
        print("!!!!!!!!!!!!!!!!!!!!!!")
        print("")
        print("")
        print("Meeting URL Again for Checking!")
        print(MeetingURL)
        print("")
        print("Thank you for using WGET testing product run by WGET.")
        print("Have a great day!")
        print("")


def main():
    run()

    
if __name__ == "__main__":
    main()
