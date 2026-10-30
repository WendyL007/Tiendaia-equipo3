param([string]$Entorno = "local")
$env:PYTHONIOENCODING = "utf-8"
New-Item -ItemType Directory -Force docs/lab3 | Out-Null
$csv = "docs/lab3/mediciones_$Entorno.csv"
$txt = "docs/lab3/lineas_$Entorno.txt"
"workers,rep,total_s,rendimiento" | Set-Content $csv -Encoding ascii
"" | Set-Content $txt -Encoding utf8

foreach ($n in 1,2,4,8) {
    docker compose up -d --scale worker=$n
    Start-Sleep 20
    foreach ($rep in 1..3) {
        docker compose exec -T rabbitmq rabbitmqctl purge_queue inferencias | Out-Null
        $linea = python scripts/carga_asincrona.py http://localhost:8080 200
        Write-Host "workers=$n rep=$rep -> $linea"
        "workers=$n rep=$rep $linea" | Add-Content $txt -Encoding utf8
        $null = $linea -match 'total=([\d.]+)s'
        $total = $Matches[1]
        $null = $linea -match 'rendimiento=([\d.]+) sol'
        $rend = $Matches[1]
        "$n,$rep,$total,$rend" | Add-Content $csv -Encoding ascii
    }
}
