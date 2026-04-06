# log_puller
Automatically Pulls Logs from a robo rio\
Just run main.py and it will try to pull logs every 3 seconds\
If it doesn't find a rio, it will try again in 3 sec\
If it does, it will pull logs that are not already in your log folder locally\
Also if the file size is not correct for a log, it will pull that log again\
It will then wait 60 seconds before trying to pull logs again\
This also applies if there are no new logs to pull\
If it fails to pull those logs, it will try again in 3 seconds\
Note: pressing control + c will wait for the current log to finish copying before exiting
