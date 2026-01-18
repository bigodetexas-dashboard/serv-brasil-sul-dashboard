$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("C:\Users\Wellyton\Desktop\Control Center BigodeTexas.lnk")
$Shortcut.TargetPath = "d:\dayz xbox\BigodeBot\launcher.bat"
$Shortcut.WorkingDirectory = "d:\dayz xbox\BigodeBot"
$Shortcut.IconLocation = "d:\dayz xbox\BigodeBot\icon.ico"
$Shortcut.Save()
