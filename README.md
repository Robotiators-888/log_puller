# log_puller
Automatically Pulls Logs from a robo rio\
Just run main.py and it will try to pull logs every 3 seconds\
If it doesn't find a rio, it will try again in 3 sec\
If it does, it will pull logs that are not already in your log folder locally\
It will then wait 60 seconds before trying to pull\
This also applies if there are no new logs to pull\
If it fails to pull those logs, it will try again in 3 seconds

I want to eventually hash existing logs to verify validity especially if communication is lost