# Fetch external benchmark repositories into external/ (git-ignored).
$ErrorActionPreference = "Stop"
New-Item -ItemType Directory -Force external | Out-Null
Push-Location external
try {
    if (-not (Test-Path "AMLGym")) {
        git clone --depth 1 https://github.com/LamannaLeonardo/AMLGym.git
    }
    if (-not (Test-Path "downward-benchmarks")) {
        git clone --depth 1 --filter=blob:none --sparse https://github.com/aibasel/downward-benchmarks.git
        Push-Location downward-benchmarks
        git sparse-checkout set blocks gripper logistics00 depot driverlog rovers satellite miconic tpp visitall-opt11-strips floortile-opt11-strips barman-sat11-strips sokoban-opt08-strips
        Pop-Location
    }
} finally {
    Pop-Location
}
