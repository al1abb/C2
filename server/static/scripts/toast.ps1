function toast {
    param(
        [string]$headlineText = "Default Headline",
        [string]$bodyText = "Default Body Text"
    )

    # Toast notification XML structure
    $xml = @"
<toast>
    <visual>
        <binding template="ToastGeneric">
            <text>$($headlineText)</text>
            <text>$($bodyText)</text>
        </binding>
    </visual>
    <audio silent="true"/>
</toast>
"@

    # Show toast notification
    $XmlDocument = [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime]::New()
    $XmlDocument.loadXml($xml)
    $AppId = '{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\WindowsPowerShell\v1.0\powershell.exe'
    [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime]::CreateToastNotifier($AppId).Show($XmlDocument)

    Write-Output "Toast notification displayed: $headlineText - $bodyText"
}
