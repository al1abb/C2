$result = Test-Connection -ComputerName google.com -Count 4 -Quiet
if ($result) {
    Write-Host 'Connected to Internet' -ForegroundColor Green
} else {
    Write-Host 'No internet connection' -ForegroundColor Red
}