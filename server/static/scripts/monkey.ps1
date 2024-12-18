# Specify the URL of the GIF file
$gifUrl = "http://192.168.80.24:5000/static/images/monkey.gif"

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
    Write-Output "Failed to download the file. Exiting script."
    exit
}

# Check if the file was downloaded successfully
if (-not (Test-Path -Path $localFilePath)) {
    Write-Output "File download unsuccessful. Exiting script."
    exit
}

# Open the GIF file in the default image viewer
$process = Start-Process -FilePath $localFilePath -PassThru

# Wait for the file to open
Start-Sleep -Seconds 3

# Use the COM object to send key presses
$wshell = New-Object -ComObject WScript.Shell

# Bring the image viewer window to the foreground
$wshell.AppActivate($process.Id)

# Wait a moment for focus to switch
Start-Sleep -Seconds 1

# Send F11 key to toggle fullscreen (for browsers or compatible viewers)
$wshell.SendKeys("{F11}")

# Delay to ensure fullscreen is active before resetting zoom
Start-Sleep -Seconds 2

# Reset the zoom level with Ctrl+0
$wshell.SendKeys("^0")

# Script ends here