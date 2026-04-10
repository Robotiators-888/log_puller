#####################IMPORTS######################
import os
import subprocess
import time
import signal
import sys
import glob
#####################CODE######################

shouldEnd = False
isCopying = False

# Handles copying interrupt logic
def signal_handler(signal, frame):
    if not isCopying:
        print("Ending not copying")
        sys.exit(0)
    else:
        global shouldEnd
        shouldEnd = True

signal.signal(signal.SIGINT, signal_handler) # Registers

bad_retry = 3
good_retry = 60

# Define the team number and construct the IP address
team_number = "888"

ip = "10." + team_number[:1] + "." + team_number[1:] + ".2"

log_path = "/media/sda1/logs/"

# Windows-friendly local path: use %USERPROFILE% and os.path.join so separators are correct
local_log_path = os.path.join(os.path.expandvars("%USERPROFILE%"), "Documents", "logs")

filesUnparsed = ""

files = ""

def main():
    while True:
        result = get_logs()
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

def get_logs():
    try:
        # find [log_path] -type f finds all files in the log path and -exec ls -l {} + gives us info about every file
        # We only care about the name and the size of the files
        # Also {} gets subsituted by the filename and + tells the find command to take all the results and feed them into ls all at once like ls -l file1 file2 instade of running ls -l once for every file which speeds things up a lot
        result = subprocess.run(["powershell", "-Command", "ssh " + f"admin@{ip}" + " 'find " + log_path + " -type f -exec ls -l {} +'"], check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Exception {e}")
        return "Couldn't connect to the robot"
    # Split files by newlines
    filesUnparsed = result.stdout
    fileinfos = filesUnparsed.splitlines()
    # Get rid of those 4 NI auth login lines
    result.split("\n")
    for i in range(4):
        fileinfos.pop()
    # Removes any empty lines
    cleanFileInfos = [x for x in fileinfos if x]
    filenames = []
    filesizes = []
    # Fill the name and length lists
    for file in cleanFileInfos:
        # Split the output by the spaces
        parsedInfo = file.split(' ')
        # The 8th segment gives us the absolute path of the file
        # We then convert this to a relative path from the log path
        filenames.append(parsedInfo[8].replace(log_path, ""))
        # The 4th segment gives us the size of the file in bytes
        filesizes.append(parsedInfo[4])
    # Build a map of existing local files (relative to local_log_path)
    local_files_full = [p for p in glob.glob(os.path.join(local_log_path, "**", "*"), recursive=True) if os.path.isfile(p)]
    local_file_sizes = {os.path.relpath(p, local_log_path): os.path.getsize(p) for p in local_files_full}

    hasDoneSomething = False
    # Iterate by index to compare remote filenames/sizes with local files
    for i in range(len(filenames)):
        # remote filenames from the device are relative to log_path and use '/'
        remote_name = filenames[i].lstrip('/\\')
        try:
            remote_size = int(filesizes[i])
        except ValueError:
            # If parsing failed, skip this file
            continue
        needs_copy = False
        if remote_name not in local_file_sizes:
            needs_copy = True
        elif local_file_sizes.get(remote_name, -1) != remote_size:
            needs_copy = True
        if needs_copy:
            # Build a platform-correct local destination path from the remote (split on '/')
            local_dest = os.path.join(local_log_path, *remote_name.split('/'))
            local_dir = os.path.dirname(local_dest)
            if local_dir and not os.path.exists(local_dir):
                os.makedirs(local_dir, exist_ok=True)
            try:
                # Copy the single file into the full destination path
                global isCopying
                isCopying = True
                breakpoint
                subprocess.run(["scp", "-p", f"admin@{ip}:" + log_path + remote_name, local_dest], check=True)
                isCopying = False
                hasDoneSomething = True
            except subprocess.CalledProcessError as e:
                return f"Error: Failed to retrieve {remote_name}"
        if shouldEnd:
            print("Ending after copy")
            sys.exit(0)
    if hasDoneSomething:
        return "Logs retrieved successfully"
    else:
        return "No new logs to retrieve"

main()
