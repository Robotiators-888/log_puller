import os
import subprocess
import time
import signal
import sys

shouldEnd: bool = False
hasEnded: bool = False

def signal_handler():
    shouldEnd = True
    while not hasEnded:
        pass
    sys.exit(0)
    

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
        if result == "couldn't connect to the robot":
            print("Couldn't connect to the robot")
            # Maybe sleep not needed becuase of ssh's built in waiting period
            time.sleep(bad_retry)
        elif result == "logs retrieved successfully":
            print("Logs retrieved successfully")
            time.sleep(good_retry)
        elif result == "No new logs to retrieve":
            print("No new logs to retrieve")
            time.sleep(good_retry)
        elif result == "Ending":
            print(result)
            break
        else:
            print(result)
            time.sleep(bad_retry)

def get_logs() -> str:
    try:
        result = subprocess.run(["powershell", "-Command", "ssh " + "admin@" + ip + " 'ls " + log_path + "'"], check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Exception {e}")
        return "couldn't connect to the robot"
    filesUnparsed = result.stdout
    files = filesUnparsed.splitlines()
    files.pop()
    files.pop()
    files.pop()
    files.pop()
    local_files = os.listdir(local_log_path)
    hasDoneSomething = False
    for file in files:
        if file not in local_files:
            try:
                subprocess.run(["scp", "-r", "-p", "admin@" + ip + ":" + log_path + file, local_log_path], check=True)
                hasDoneSomething = True
            except subprocess.CalledProcessError as e:
                return f"Error: Failed to retrieve {file}"
        if shouldEnd:
            hasEnded = True
            return "Ending"
    if not hasDoneSomething:
        return "No new logs to retrieve"
    else:
        return "logs retrieved successfully"

main()