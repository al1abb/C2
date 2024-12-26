# Open the URL in the default browser
Start-Process -FilePath "cmd" -ArgumentList "/c start https://updatefaker.com/windows11/index.html" -WindowStyle Hidden

# Wait a few seconds for the browser to load
Start-Sleep -Seconds 2

# Simulate the F11 key press for full-screen mode
Add-Type -AssemblyName System.Windows.Forms
[System.Windows.Forms.SendKeys]::SendWait("{F11}")