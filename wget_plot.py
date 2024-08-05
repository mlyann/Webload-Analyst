import time
import os
import numpy as np
import matplotlib.pyplot as plt
import re
import ast
from datetime import datetime,timedelta
import mplcursors

from config import data_folder

# Use 'data_folder' for file operations


def generate_filename(url, minutes, file_type='txt', ID = "LoadTimes"):
    """
    Generate a filename based on the URL and duration.

    @param url: The URL of the meeting.
    @param minutes: Duration of the meeting in minutes.
    @param ext: The file extension for the generated file.
    @return: A string representing the generated filename.
    """
    sanitized_url = re.sub(r'[^\w\s-]', '', url.replace('/', '_').replace(':', '_'))
    return os.path.join(data_folder, ID+f"{sanitized_url}_{minutes}min.{file_type}")


def plot_load_times(timestamps, load_times, stats, url, minutes, TIME_LINE, PAUSE_TIME_EXCEED, PAUSE_TIME_NOT_EXCEED):
    """
    Plots the webpage loading times over multiple requests, with time elapsed and loading time annotations.

    @param timestamps: List of timestamps in the format 'YYYY-MM-DD HH:MM:SS'.
    @param load_times: List of loading times corresponding to the timestamps.
    @param stats: A dictionary containing statistical information about the loading times.
                  Expected keys: 'count_exceeding', 'mean', 'median', 'max', 'min'.
    @param url: URL of the meeting.
    @param minutes: Duration of the meeting in minutes.
    @param TIME_LINE: Maximum acceptable loading time in seconds.
    @param PAUSE_TIME_EXCEED: Pause time in seconds if loading time exceeds TIME_LINE.
    @param PAUSE_TIME_NOT_EXCEED: Pause time in seconds if loading time does not exceed TIME_LINE.
    """
    print("Timestamps received:", timestamps)
    print(len(timestamps))

    # Initial timestamp processing
    start_time = datetime.strptime(timestamps[0], '%Y-%m-%d %H:%M:%S')
    end_time = datetime.strptime(timestamps[-1], '%Y-%m-%d %H:%M:%S')
    total_seconds = int((end_time - start_time).total_seconds())
    time_range = list(range(0, total_seconds + 1))
    relative_times = [(datetime.strptime(ts, '%Y-%m-%d %H:%M:%S') - start_time).total_seconds() for ts in timestamps]

    # Generate descriptive labels for each second
    relative_times_descriptive_filtered = [
        f"{int(t // 60)} Minute{'s' if int(t // 60) != 1 else ''}, {int(t % 60)} Second{'s' if int(t % 60) != 1 else ''}" 
        if int(t // 60) != 0 else f"{int(t % 60)} Second{'s' if int(t % 60) != 1 else ''}"
        for t in time_range
    ]
    
    # Update the first timestamp entry to "X:XXpm EST"
    relative_times_descriptive_filtered[0] = start_time.strftime('%I:%M%p EST')

    # Create the main plot
    fig, ax1 = plt.subplots(figsize=(15, 8))
    line1, = ax1.plot(relative_times, load_times, 'b-o', label='Loading Time (s)')
    ax1.set_xlabel('Time Elapsed')
    ax1.set_ylabel('Loading Time (s)', color='b')
    ax1.tick_params(axis='y', labelcolor='b')
    ax1.axhline(y=TIME_LINE, color='r', linestyle='--', label=f'Max Acceptable Time ({TIME_LINE}s)')
    plt.xticks(rotation=45, ha='right')  # Adjusting x-tick labels for better readability
    ax1.set_xticks(time_range[::20])  # Adjust x-axis to show every 20 seconds for better readability
    ax1.set_xticklabels(relative_times_descriptive_filtered[::20])

    # Add transparent scatter plot for the horizontal line
    scatter = ax1.scatter(relative_times, [TIME_LINE] * len(relative_times), alpha=0)

    # Titles and grid
    plt.title('Webpage Loading Times Over Multiple Requests')
    ax1.grid(True)
    
    # Additional descriptive texts and formatting
    plt.figtext(0.5, 1.08, "Starting Time: " + relative_times_descriptive_filtered[0], 
                        horizontalalignment='center', fontsize=12, fontweight='bold')
    additional_text = (f"Meeting URL: {url}\n"
                       f"Duration (minutes): {minutes}\n"
                       f"Maximum acceptable response time (seconds): {TIME_LINE}\n"
                       f"Pause time if exceeds the time line (seconds): {PAUSE_TIME_EXCEED}\n"
                       f"Pause time if does not exceed the time line (seconds): {PAUSE_TIME_NOT_EXCEED}\n")
    plt.figtext(0.5, -0.1, additional_text, wrap=True, horizontalalignment='center', fontsize=10)
    
    plt.legend()

    # Add mplcursors for interactive display of values
    cursor = mplcursors.cursor([line1, scatter], hover=True)

    @cursor.connect("add")
    def on_add(sel):
        index = int(sel.index)
        load_time = load_times[index]
        y_value = sel.target[1]
        if y_value == TIME_LINE:
            sel.annotation.set_text(f'Time: {relative_times_descriptive_filtered[index]}\nLoading Time: {load_time}s\nNote: This is the max acceptable time line')
        else:
            sel.annotation.set_text(f'Time: {relative_times_descriptive_filtered[index]}\nLoading Time: {load_time}s')
        print(f'Interactive data: Time: {relative_times_descriptive_filtered[index]}, Loading Time: {load_time}s')  # Debugging line

    # Layout and save
    plt.tight_layout()
    filename_png = generate_filename(url, minutes, 'png')
    plt.savefig(filename_png, bbox_inches='tight')
    print(f"Plot saved as {filename_png}")
    plt.show()



def plot_user_count(timestamps, load_times, url, minutes, TIME_LINE, PAUSE_TIME_EXCEED, PAUSE_TIME_NOT_EXCEED):
    """
    Plots user counts and loading times over time.

    @timestamps: List of timestamps in the format 'YYYY-MM-DD HH:MM:SS'.
    @load_times: List of loading times corresponding to the timestamps.
    @url: URL of the meeting.
    @minutes: Duration of the meeting in minutes.
    @TIME_LINE: Maximum acceptable loading time in seconds.
    @PAUSE_TIME_EXCEED: Pause time in seconds if loading time exceeds TIME_LINE.
    @PAUSE_TIME_NOT_EXCEED: Pause time in seconds if loading time does not exceed TIME_LINE.
    """
    print("Timestamps received:", timestamps)
    print(len(timestamps))

    # Initial timestamp processing
    start_time = datetime.strptime(timestamps[0], '%Y-%m-%d %H:%M:%S')
    end_time = datetime.strptime(timestamps[-1], '%Y-%m-%d %H:%M:%S')
    total_seconds = int((end_time - start_time).total_seconds())
    time_range = list(range(0, total_seconds + 1))
    relative_times = [(datetime.strptime(ts, '%Y-%m-%d %H:%M:%S') - start_time).total_seconds() for ts in timestamps]

    # Generate descriptive labels for each second
    relative_times_descriptive_filtered = [
        f"{int(t // 60)} Minute{'s' if int(t // 60) != 1 else ''}, {int(t % 60)} Second{'s' if int(t % 60) != 1 else ''}" 
        if int(t // 60) != 0 else f"{int(t % 60)} Second{'s' if int(t % 60) != 1 else ''}"
        for t in time_range
    ]
    
    # Update the first timestamp entry to "X:XXpm EST"
    relative_times_descriptive_filtered[0] = start_time.strftime('%I:%M%p EST')

    # Create the main plot
    fig, ax1 = plt.subplots(figsize=(15, 8))
    line1, = ax1.plot(relative_times, load_times, 'b-o', label='Loading Time (s)')
    ax1.set_xlabel('Time Elapsed')
    ax1.set_ylabel('Loading Time (s)', color='b')
    ax1.tick_params(axis='y', labelcolor='b')
    ax1.axhline(y=TIME_LINE, color='r', linestyle='--', label=f'Max Acceptable Time ({TIME_LINE}s)')
    plt.xticks(rotation=45, ha='right')  # Adjusting x-tick labels for better readability
    ax1.set_xticks(time_range[::20])  # Adjust x-axis to show every 10 seconds for better readability
    ax1.set_xticklabels(relative_times_descriptive_filtered[::20])

    # Add transparent scatter plot for the horizontal line
    scatter = ax1.scatter(relative_times, [TIME_LINE] * len(relative_times), alpha=0)

    # Secondary axis for user counts
    ax2 = ax1.twinx()
    with open('active_user_ranges.txt', 'r') as file:
        data = file.read()
    try:
        timestamp_dt = [datetime.strptime(ts, '%Y-%m-%d %H:%M:%S') for ts in timestamps]
        active_user = ast.literal_eval(data)
        time_ranges = [(datetime.strptime(entry[1], '%Y-%m-%d %H:%M:%S'), datetime.strptime(entry[2], '%Y-%m-%d %H:%M:%S')) for entry in active_user]
        
        # Calculate user counts for each second in the time range
        counts = [sum(start <= start_time + timedelta(seconds=t) <= end for start, end in time_ranges) for t in time_range]
        
        # Create bar plot for user counts, ensuring x-data is a list
        bars = ax2.bar(time_range, counts, color='g', alpha=0.6, label='User Count')
        ax2.set_ylabel('Count of Active Users', color='g')
        ax2.tick_params(axis='y', labelcolor='g')
        
    except Exception as e:
        print(f"Error parsing input: {e}")
        return
    
    # Titles and grid
    plt.title('Webpage Loading Times and User Counts Over Multiple Requests')
    ax1.grid(True)
    
    # Additional descriptive texts and formatting
    plt.figtext(0.5, 1.08, "Starting Time: " + relative_times_descriptive_filtered[0], 
                        horizontalalignment='center', fontsize=12, fontweight='bold')
    additional_text = (f"Meeting URL: {url}\n"
                       f"Duration (minutes): {minutes}\n"
                       f"Maximum acceptable response time (seconds): {TIME_LINE}\n"
                       f"Pause time if exceeds the time line (seconds): {PAUSE_TIME_EXCEED}\n"
                       f"Pause time if does not exceed the time line (seconds): {PAUSE_TIME_NOT_EXCEED}\n")
    plt.figtext(0.5, -0.1, additional_text, wrap=True, horizontalalignment='center', fontsize=10)
    
    # Add legends
    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    plt.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left')
    
    # Add mplcursors for interactive display of values
    cursor = mplcursors.cursor([line1, *bars, scatter], hover=True)

    @cursor.connect("add")
    def on_add(sel):
        index = sel.index
        # Calculate the actual second index from the target
        sec_index = int(sel.target[0])
        load_time = load_times[relative_times.index(sec_index)] if sec_index in relative_times else None
        user_count = counts[sec_index]
        if sel.target[1] == TIME_LINE:
            sel.annotation.set_text(f'Time: {relative_times_descriptive_filtered[sec_index]}\nLoading Time: {load_time}s\nUser Count: {user_count}\nNote: This is the max acceptable time line')
        else:
            sel.annotation.set_text(f'Time: {relative_times_descriptive_filtered[sec_index]}\nLoading Time: {load_time}s\nUser Count: {user_count}')
        print(f'Interactive data: Time: {relative_times_descriptive_filtered[sec_index]}, Loading Time: {load_time}s, User Count: {user_count}')  # Debugging line

    # Layout and save
    plt.tight_layout()
    filename_png = generate_filename(url, minutes, 'png',"User_Count")
    plt.savefig(filename_png, bbox_inches='tight')
    print(f"Plot saved as {filename_png}")
    plt.show()
