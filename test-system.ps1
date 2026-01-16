# Test the License Plate System
# This adds a test detection to see if everything works

Write-Host "`n=================================" -ForegroundColor Cyan
Write-Host "Testing License Plate System" -ForegroundColor Cyan
Write-Host "=================================`n" -ForegroundColor Cyan

# Test data
$testPlates = @(
    @{ plateNumber = "ABC123"; confidence = 0.95 },
    @{ plateNumber = "XYZ789"; confidence = 0.88 },
    @{ plateNumber = "DEF456"; confidence = 0.92 }
)

foreach ($plate in $testPlates) {
    Write-Host "Adding test plate: $($plate.plateNumber)..." -ForegroundColor Yellow
    
    $body = @{
        plateNumber = $plate.plateNumber
        gateId = "gate_01"
        confidence = $plate.confidence
        timestamp = (Get-Date).ToString("o")
    } | ConvertTo-Json
    
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3000/api/plates" -Method POST -Body $body -ContentType "application/json" -UseBasicParsing
        
        if ($response.StatusCode -eq 201) {
            Write-Host "  ✓ Added successfully!" -ForegroundColor Green
        }
    } catch {
        Write-Host "  ✗ Error: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    Start-Sleep -Milliseconds 500
}

Write-Host "`n✓ Test complete!" -ForegroundColor Green
Write-Host "Check your dashboard - you should see 3 new plates!`n" -ForegroundColor Cyan
Write-Host "Dashboard: c:\Projects2\License_Plate_Scanning\dashboard.html`n" -ForegroundColor Yellow
