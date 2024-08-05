from datetime import datetime
import os

# Generates a directory name based on the current timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
data_folder = f"data/{timestamp}"

# Ensure the directory exists
os.makedirs(data_folder, exist_ok=True)
