import os
import subprocess
import time

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

# Define the team number and construct the IP address
team_number = "888"

team_number_ip = add_dot_to_string(team_number)

ip = "10." + team_number_ip + ".2"

log_path = "/dev/sda1/logs/"

local_log_path = os.path.expandvars("%USERPROFILE%/Documents/logs/")

filesUnparsed = ""

files = ""

def main():
    while True:
        result = get_logs()
        if result == "couldn't connect to the robot":
            print("Couldn't connect to the robot")
            time.sleep(3)
        elif result == "logs retrieved successfully":
            print("Logs retrieved successfully")
            time.sleep(60)
        elif result == "No new logs to retrieve":
            print("No new logs to retrieve")
            time.sleep(60)
        else:
            print(result)
            time.sleep(3)
def get_logs() -> str:
    try:
        filesUnparsed = subprocess.run(["ssh", "admin@" + ip + "'ls " + log_path + "'"], check=True, capture_output=True, text=True).stdout
    except subprocess.CalledProcessError as e:
        return "couldn't connect to the robot"
    files = filesUnparsed.splitlines()
    local_files = os.listdir(local_log_path)
    hasDoneSomething = False
    for file in files:
        if file not in local_files:
            try:
                subprocess.run(["scp", "admin@" + ip + ":" + log_path + file, local_log_path], check=True)
                hasDoneSomething = True
            except subprocess.CalledProcessError as e:
                return f"Error: Failed to retrieve {file}"
    if not hasDoneSomething:
        return "No new logs to retrieve"
    else:
        return "logs retrieved successfully"

main()