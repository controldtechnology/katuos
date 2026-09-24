<#
Create the six text-free Katu desktop wallpapers with the built-in GDI+ renderer.
This is an asset authoring utility only; it is not called by the ISO build.
#>
[CmdletBinding()]
param([string]$OutputDirectory = (Join-Path (Split-Path $PSScriptRoot -Parent -Parent) 'wallpapers'))

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing

$width = 1920
$height = 1080
$scale = 2

function New-Color([string]$Hex, [int]$Alpha = 255) {
    $c = [System.Drawing.ColorTranslator]::FromHtml($Hex)
    return [System.Drawing.Color]::FromArgb($Alpha, $c.R, $c.G, $c.B)
}

function Draw-Curve($Graphics, [string]$Hex, [int]$Alpha, [single]$LineWidth, [single[]]$Points) {
    $pen = [System.Drawing.Pen]::new((New-Color $Hex $Alpha), $LineWidth)
    $pen.StartCap = [System.Drawing.Drawing2D.LineCap]::Round
    $pen.EndCap = [System.Drawing.Drawing2D.LineCap]::Round
    $pen.LineJoin = [System.Drawing.Drawing2D.LineJoin]::Round
    $path = [System.Drawing.Drawing2D.GraphicsPath]::new()
    $path.AddBezier($Points[0], $Points[1], $Points[2], $Points[3], $Points[4], $Points[5], $Points[6], $Points[7])
    $Graphics.DrawPath($pen, $path)
    $path.Dispose()
    $pen.Dispose()
}

function Fill-Land($Graphics, [string]$Hex, [int]$Alpha, [single[]]$Top) {
    $path = [System.Drawing.Drawing2D.GraphicsPath]::new()
    $path.AddBezier($Top[0], $Top[1], $Top[2], $Top[3], $Top[4], $Top[5], $Top[6], $Top[7])
    $path.AddLine($Top[6], $Top[7], $width, $height)
    $path.AddLine($width, $height, 0, $height)
    $path.CloseFigure()
    $brush = [System.Drawing.SolidBrush]::new((New-Color $Hex $Alpha))
    $Graphics.FillPath($brush, $path)
    $brush.Dispose()
    $path.Dispose()
}

function Draw-Wallpaper([string]$Name, [string]$TopColor, [string]$BottomColor, [string]$Forest, [string]$Water, [bool]$Light, [bool]$Quiet) {
    $bmp = [System.Drawing.Bitmap]::new($width * $scale, $height * $scale, [System.Drawing.Imaging.PixelFormat]::Format24bppRgb)
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $g.CompositingQuality = [System.Drawing.Drawing2D.CompositingQuality]::HighQuality
    $g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    $g.ScaleTransform($scale, $scale)

    $bg = [System.Drawing.Drawing2D.LinearGradientBrush]::new(
        [System.Drawing.Rectangle]::new(0, 0, $width, $height),
        (New-Color $TopColor), (New-Color $BottomColor), 90)
    $g.FillRectangle($bg, 0, 0, $width, $height)
    $bg.Dispose()

    if ($Light) {
        $contourColor = '#46665b'; $contourAlpha = 24; $shore = '#d3c7a6'; $waterAlpha = 235
    } else {
        $contourColor = '#79a58c'; $contourAlpha = 23; $shore = '#d6a83e'; $waterAlpha = 226
    }

    # Fine river-basin contours. Their low contrast keeps desktop icons readable.
    if (-not $Quiet) {
        for ($i = 0; $i -lt 13; $i++) {
            $y = 115 + ($i * 66)
            $lift = ($i % 3) * 21
            Draw-Curve $g $contourColor $contourAlpha 1.15 ([single[]]@(800, $y, 1120, ($y - 105 - $lift), 1510, ($y + 185), 1970, ($y - 45)))
            Draw-Curve $g $contourColor $contourAlpha 1.0 ([single[]]@(-80, ($y + 90), 210, ($y - 65), 540, ($y + 185 + $lift), 920, ($y + 35)))
        }
    }

    # Forest ridgelines stay low and dark; the icon-safe left field remains quiet.
    if (-not $Quiet) {
        Fill-Land $g $Forest 175 ([single[]]@(0, 770, 280, 620, 430, 770, 760, 710))
        Fill-Land $g $Forest 205 ([single[]]@(0, 855, 390, 680, 550, 915, 900, 790))
        Fill-Land $g $Forest 225 ([single[]]@(0, 970, 440, 780, 735, 1010, 1100, 860))
    }

    if ($Light) { $riverCore = '#4a8871'; $riverInner = '#bdd8c9'; $glowAlpha = 32 }
    else { $riverCore = $Water; $riverInner = '#8fc8ad'; $glowAlpha = 24 }

    # One broad river arc, offset to the right so the left side remains useful for icons.
    $river = [single[]]@(1550, -120, 1390, 200, 1800, 310, 1570, 485, 1260, 730, 1730, 790, 1490, 1160)
    $p = [System.Drawing.Drawing2D.GraphicsPath]::new()
    $p.AddBeziers([System.Drawing.PointF[]]@(
        [System.Drawing.PointF]::new($river[0],$river[1]), [System.Drawing.PointF]::new($river[2],$river[3]), [System.Drawing.PointF]::new($river[4],$river[5]), [System.Drawing.PointF]::new($river[6],$river[7]),
        [System.Drawing.PointF]::new($river[8],$river[9]), [System.Drawing.PointF]::new($river[10],$river[11]), [System.Drawing.PointF]::new($river[12],$river[13])))
    foreach ($spec in @(@($Water,$glowAlpha,176), @($shore, 120, 154), @($riverCore,$waterAlpha,128), @($riverInner,50,3))) {
        $pen = [System.Drawing.Pen]::new((New-Color $spec[0] $spec[1]), [single]$spec[2])
        $pen.StartCap = [System.Drawing.Drawing2D.LineCap]::Round; $pen.EndCap = [System.Drawing.Drawing2D.LineCap]::Round; $pen.LineJoin = [System.Drawing.Drawing2D.LineJoin]::Round
        $g.DrawPath($pen, $p); $pen.Dispose()
    }
    $p.Dispose()

    # A small sun at the far edge gives the composition warmth without adding a logo or text.
    $sun = [System.Drawing.SolidBrush]::new((New-Color '#ffab00' 205))
    $g.FillEllipse($sun, 1645, 125, 76, 76)
    $sun.Dispose()

    # Sparse rosette rings identify the jaguar edition without turning the desktop into a pattern.
    if ($Name -eq 'katu-onca-4k.png') {
        foreach ($spot in @(@(1190,260,46),@(1375,165,30),@(1760,350,38),@(1115,535,28),@(1780,625,25),@(1325,835,34))) {
            $pen = [System.Drawing.Pen]::new((New-Color '#ffab00' 74), 2.2)
            $g.DrawEllipse($pen, [single]$spot[0], [single]$spot[1], [single]$spot[2], [single]$spot[2])
            $g.DrawEllipse($pen, [single]($spot[0]+$spot[2]*0.32), [single]($spot[1]+$spot[2]*0.32), [single]($spot[2]*0.36), [single]($spot[2]*0.36))
            $pen.Dispose()
        }
    }

    $target = Join-Path $OutputDirectory $Name
    $bmp.Save($target, [System.Drawing.Imaging.ImageFormat]::Png)
    $g.Dispose(); $bmp.Dispose()
    Write-Output "Created $target"
}

New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
Draw-Wallpaper 'katu-amazonia-4k.png' '#071811' '#0d2119' '#103c2b' '#155c48' $false $false
Draw-Wallpaper 'katu-onca-4k.png' '#091812' '#14271d' '#16432f' '#155a46' $false $false
Draw-Wallpaper 'katu-rio-4k.png' '#071a1b' '#0c2527' '#103a32' '#176c68' $false $false
Draw-Wallpaper 'katu-green-4k.png' '#f0eee5' '#e2e5d9' '#c8d2c3' '#598d79' $true $true
Draw-Wallpaper 'katu-dark-4k.png' '#080c11' '#111820' '#182129' '#253b42' $false $true
Draw-Wallpaper 'katu-minimal-4k.png' '#0d1117' '#171d22' '#1b2f2a' '#35564a' $false $true

# SDDM consumes a JPEG from its theme directory; export the same art without text.
$loginImage = [System.Drawing.Image]::FromFile((Join-Path $OutputDirectory 'katu-amazonia-4k.png'))
$loginImage.Save((Join-Path $OutputDirectory 'katu-login-background.jpg'), [System.Drawing.Imaging.ImageFormat]::Jpeg)
$loginImage.Dispose()
