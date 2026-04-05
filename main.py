import os
import subprocess
import time
import signal
import sys
import glob

shouldEnd: bool = False

def signal_handler(signal, frame):
    global shouldEnd
    shouldEnd = True

signal.signal(signal.SIGINT, signal_handler)

# Helper function
def add_dot_to_string(s: str) -> str:
    ret = ""
    i = 0
    for char in s:
        ret += char
        i += 1
        if i == len(s) - 2:
            ret += "."
    return ret

bad_retry: int = int(3)
good_retry: int = int(60)

# Define the team number and construct the IP address
team_number: str = "888"

team_number_ip: str = add_dot_to_string(team_number)

ip: str = "10." + team_number_ip + ".2"

log_path: str = "/media/sda1/logs/"

local_log_path: str = os.path.expandvars("%USERPROFILE%/Documents/logs/")

filesUnparsed: str = ""

files: str = ""

def main():
    while True:
        result: str = get_logs()
        if result == "Couldn't connect to the robot":
            print(result)
            # Maybe sleep not needed becuase of ssh's built in waiting period
            time.sleep(bad_retry)
        elif result == "Logs retrieved successfully":
            print(result)
            time.sleep(good_retry)
        elif result == "No new logs to retrieve":
            print(result)
            time.sleep(good_retry)
        elif result == "Ending":
            print(result)
            break
        else:
            print(result)
            time.sleep(bad_retry)

def get_logs() -> str:
    try:
        # find [log_path] -type f finds all files in the log path and -exec ls -l {} + gives us info about every file
        # We only care about the name and the size of the files
        # Also {} gets subsituted by the filename and + tells the find command to take all the results and feed them into ls all at once like ls -l file1 file2 instade of running ls -l once for every file which speeds things up a lot
        result = subprocess.run(["powershell", "-Command", "ssh " + "admin@" + ip + " 'find " + log_path + " -type f -exec ls -l {} +'"], check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Exception {e}")
        return "Couldn't connect to the robot"
    # Split files by newlines
    filesUnparsed = result.stdout
    fileinfos = filesUnparsed.splitlines()
    # Get rid of those 4 NI auth login lines, not using a loop is probably more optimized
    fileinfos.pop()
    fileinfos.pop()
    fileinfos.pop()
    fileinfos.pop()
    filenames = []
    filesizes = []
    # Fill the name and length lists
    for file in fileinfos:
        # Split the output by the spaces
        parsedInfo = file.split(' ')
        # The 8th segment gives us the absolute path of the file
        # We then convert this to a relative path from the log path
        filenames.append(parsedInfo[8].replace(log_path, ""))
        # The 4th segment gives us the size of the file in bytes
        filesizes.append(parsedInfo[4])
    # Gets file names using glob
    # Takes our directory
    local_file_names = map(lambda path: path.replace(local_log_path, ""), glob.glob(local_log_path+"*/*"))
    local_file_sizes = map(lambda name: os.path.getsize(local_log_path+name), local_file_names)
    hasDoneSomething = False
    for i in len(filenames):
        if filenames[i] not in local_file_names or filesizes[i] != local_file_sizes[i]:
            try:
                subprocess.run(["scp", "-p", "admin@" + ip + ":" + log_path + filenames[i], local_log_path], check=True)
                hasDoneSomething = True
            except subprocess.CalledProcessError as e:
                return f"Error: Failed to retrieve {filenames[i]}"
        if shouldEnd:
            print("Ending")
            sys.exit(0)
    if hasDoneSomething:
        return "Logs retrieved successfully"
    else:
        return "No new logs to retrieve"

main()
