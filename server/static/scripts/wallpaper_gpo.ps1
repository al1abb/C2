# Registry path and value for the "Prevent changing desktop background" GPO
$regPath = "HKCU:\Software\Policies\Microsoft\Windows\Control Panel\Desktop"
$regName = "NoChangingWallPaper"
$regValue = 1

# Ensure the registry path exists
New-Item -Path $regPath -Force

# Set the value to enable the GPO
Set-ItemProperty -Path $regPath -Name $regName -Value $regValue

# Force Group Policy to update
gpupdate /force