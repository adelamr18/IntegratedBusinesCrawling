$exclude = @("venv", "carrefour_bot.zip")
$files = Get-ChildItem -Path . -Exclude $exclude
Compress-Archive -Path $files -DestinationPath "carrefour_bot.zip" -Force