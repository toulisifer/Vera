# Tái lập kết quả VeRA trên Windows (Docker Desktop). Chạy trong PowerShell, ở thư mục vera:
#
#   powershell -ExecutionPolicy Bypass -File repro\run.ps1          # mọi lượt chạy
#   powershell -ExecutionPolicy Bypass -File repro\run.ps1 E1       # chỉ E1
#
# Giống repro/run.sh: dựng Ubuntu 24.04 sạch rồi chạy scripts/reproduce.sh bên trong.
$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $PSScriptRoot
docker build -q -t vera-repro (Join-Path $repo "repro") | Out-Null
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
docker pull -q python:3.12-slim | Out-Null
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
docker run --rm -t `
  -v /var/run/docker.sock:/var/run/docker.sock `
  -v "${repo}:/src:ro" `
  -e VERA_SANDBOX_INLINE=1 `
  vera-repro bash /src/scripts/reproduce.sh @args
exit $LASTEXITCODE
