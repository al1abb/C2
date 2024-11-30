# Cat image
# https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/Cat_with_cute_eyes.jpeg/1300px-Cat_with_cute_eyes.jpeg

# https://random.dog/bb2dfc51-b7a3-4722-9ecd-b7d014a3a4dc.jpg

# Define the URL and the local file path
$imageUrl = "https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/Cat_with_cute_eyes.jpeg/2500px-Cat_with_cute_eyes.jpeg?20180901100342"

$tempFilePath = "$env:TEMP\wallpaper.jpg"

# Download the image
Invoke-WebRequest -Uri $imageUrl -OutFile $tempFilePath

# Set the wallpaper
Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;

public class Wallpaper {
    [DllImport("user32.dll", CharSet = CharSet.Auto)]
    public static extern int SystemParametersInfo(int uAction, int uParam, string lpvParam, int fuWinIni);
    public const int SPI_SETDESKWALLPAPER = 20;
    public const int SPIF_UPDATEINIFILE = 0x01;
    public const int SPIF_SENDCHANGE = 0x02;
    public static void SetWallpaper(string path) {
        SystemParametersInfo(SPI_SETDESKWALLPAPER, 0, path, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE);
    }
}
"@

[Wallpaper]::SetWallpaper($tempFilePath)

Write-Host "Wallpaper set successfully!"
