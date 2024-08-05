import requests
import progressbar
import threading
import time
import queue

def show_progress(event):
    """
    Displays a progress bar that runs for a specified duration or until an event is set.

    @param event: threading.Event object that can be set to stop the progress bar early.
    """
    widgets = [
        'Progress: ', progressbar.Percentage(), ' ',
        progressbar.Bar(marker='=', left='[', right=']'), ' ',
        progressbar.ETA()
    ]
    duration = 50  # Duration for the progress bar
    bar = progressbar.ProgressBar(widgets=widgets, maxval=duration).start()
    
    for i in range(duration):
        if event.is_set():
            break
        time.sleep(0.1)  # Small sleep to update the progress bar
        bar.update(i + 1)
    
    bar.finish()

def validate_url(url, event, result_queue):
    """
    Validates a URL by sending a GET request and sets an event upon completion.
    Puts the result (True if valid, False if invalid) into the result queue.

    @param url: The URL to validate.
    @param event: threading.Event object to set when the validation is complete.
    @param result_queue: queue.Queue object to store the validation result.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        result_queue.put(True)
    except requests.RequestException:
        result_queue.put(False)
    finally:
        event.set()

def validate_url_with_progress(url):
    """
    Validates a URL with a progress bar indication. Spawns two threads: one for
    showing the progress bar and one for validating the URL.

    @param url: The URL to validate.

    @return: bool indicating whether the URL is valid (True) or not (False).
    """
    event = threading.Event()
    result_queue = queue.Queue()
    
    progress_thread = threading.Thread(target=show_progress, args=(event,))
    validation_thread = threading.Thread(target=validate_url, args=(url, event, result_queue))

    progress_thread.start()
    validation_thread.start()

    validation_thread.join()
    progress_thread.join()

    return result_queue.get()

def get_meeting_url():
    """
    Prompts the user to enter a meeting URL and validates it. Keeps prompting until
    a valid URL is entered.

    @return: str representing the valid meeting URL.
    """
    while True:
        meeting_url = input("\nPlease Enter the Meeting URL: ")
        if validate_url_with_progress(meeting_url):
            return meeting_url
        else:
            print("\nInvalid URL or the URL cannot be reached. Please try again.\n")

def get_float_input(prompt):
    """
    Prompts the user to enter a float value. Keeps prompting until a valid float is entered.

    @param prompt: str representing the prompt message to display to the user.

    @return: float representing the entered float value.
    """
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("\nInvalid input. Please enter a number.\n")

def get_int_input(prompt):
    """
    Prompts the user to enter a positive integer. Keeps prompting until a valid positive integer is entered.

    @param prompt: str representing the prompt message to display to the user.

    @return: int representing the entered positive integer.
    """
    while True:
        try:
            value = int(input(prompt))
            if value > 0:
                return value
            else:
                print("Invalid input. Please enter a positive integer.")
        except ValueError:
            print("Invalid input. Please enter an integer.")
