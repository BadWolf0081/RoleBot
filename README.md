# RoleBot
A discord python bot to check for users with specified roles on source server and assign associated roles on destination.

# Installation
1.  Clone Repo
2.  Create venv ```python -m venv rolevenv```
3.  install dependency ```rolevenv/bin/pip install discord.py```
4.  Modify script with the following items:
   
     Source Server ID
    
     Destination Servers
    
     Source Roles mapped to destination
    
     Your bot token
    
6.  Run bot ```rolevenv/bin/python rolebot.py```

7.  OPTIONAL - Run in pm2 ```pm2 start "/home/user/RoleBot/rolevenv/bin/python rolebot.py" --name RoleBot``` 
