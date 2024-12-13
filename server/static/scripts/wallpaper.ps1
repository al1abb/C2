function set-wallpaper {
    param(
        [string]$imageUrl = "https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/Cat_with_cute_eyes.jpeg/2500px-Cat_with_cute_eyes.jpeg?20180901100342",  # Default image URL
        [string]$tempFilePath = "$env:TEMP\wallpaper.jpg"  # Default local file path
    )

    # Download the image from the URL to the specified path
    Invoke-WebRequest -Uri $imageUrl -OutFile $tempFilePath

    # Add code to change the desktop wallpaper
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

    # Set the wallpaper
    [Wallpaper]::SetWallpaper($tempFilePath)

    Write-Host "Wallpaper set successfully: $imageUrl!"
}