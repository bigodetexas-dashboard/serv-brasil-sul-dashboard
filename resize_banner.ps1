Add-Type -AssemblyName System.Drawing
$inputPath = "C:\Users\Wellyton\.gemini\antigravity\brain\3915a2c1-8dc2-42b0-bb30-72533c61171b\bigodetexas_banner_1764091407624.png"
$outputPath = "C:\Users\Wellyton\.gemini\antigravity\brain\3915a2c1-8dc2-42b0-bb30-72533c61171b\bigodetexas_banner_final.png"

if (-not (Test-Path $inputPath)) {
    Write-Error "Input file not found: $inputPath"
    exit 1
}

try {
    $image = [System.Drawing.Image]::FromFile($inputPath)
    $newImage = new-object System.Drawing.Bitmap(680, 240)
    $graphics = [System.Drawing.Graphics]::FromImage($newImage)
    $graphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    $graphics.DrawImage($image, 0, 0, 680, 240)
    $newImage.Save($outputPath, [System.Drawing.Imaging.ImageFormat]::Png)
    
    $image.Dispose()
    $newImage.Dispose()
    $graphics.Dispose()
    
    Write-Host "Resized image saved to $outputPath"
} catch {
    Write-Error "Error resizing image: $_"
    exit 1
}
