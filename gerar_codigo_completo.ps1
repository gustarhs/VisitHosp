$output = Join-Path (Get-Location) 'codigo_completo.txt'
$files = Get-ChildItem -Path '.\frontend', '.\backend' -File -Recurse |
    Where-Object { $_.FullName -notmatch '\\__pycache__\\' -and $_.Extension -in '.py', '.sql', '.html', '.css', '.js' } |
    Sort-Object FullName

$sections = foreach ($file in $files) {
    $relative = $file.FullName.Substring((Get-Location).Path.Length + 1).Replace('\', '/')
    "===== INICIO: $relative ====="
    Get-Content -LiteralPath $file.FullName -Raw
    "===== FIM: $relative ====="
    ''
}

[System.IO.File]::WriteAllText($output, ($sections -join [Environment]::NewLine), [System.Text.UTF8Encoding]::new($false))
Write-Output "Arquivos incluídos: $($files.Count)"
Write-Output "Arquivo criado: $output"
