# Specify the URL of the GIF file
$gifUrl = "http://192.168.30.20:5000/static/images/monkey.gif"

# Specify the local directory to save the file
$localDirectory = "C:\Users\$env:USERNAME\Desktop"

# Specify the local file name
$localFileName = "monkey.gif"
$localFilePath = Join-Path -Path $localDirectory -ChildPath $localFileName

# Download the GIF file with error handling
try {
    Invoke-WebRequest -Uri $gifUrl -OutFile $localFilePath -ErrorAction Stop
}
catch {
    exit
}

# Check if the file was downloaded successfully
if (-not (Test-Path -Path $localFilePath)) {
    exit
}

# Open the GIF file in the default image viewer
Start-Process -FilePath $localFilePath

# Wait for the file to open
Start-Sleep -Seconds 3

# Simulate key presses to go full screen and zoom in
$wshell = New-Object -ComObject WScript.Shell

# Send F11 key to toggle fullscreen (works for some viewers like browsers or apps)
$wshell.SendKeys("{F11}")

# Delay to ensure fullscreen is active before zooming
Start-Sleep -Seconds 2

# Simulate Ctrl + Plus (Zoom In) multiple times
for ($i = 0; $i -lt 10; $i++) {
    $wshell.SendKeys("^{+}")
    Start-Sleep -Milliseconds 500
}