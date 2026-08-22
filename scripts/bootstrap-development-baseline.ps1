param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]] $BootstrapArgs
)

$ErrorActionPreference = "Stop"
$Controller = Join-Path $PSScriptRoot "bootstrap_development_baseline.py"

if (Get-Command python3 -ErrorAction SilentlyContinue) {
    & python3 $Controller @BootstrapArgs
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    & py -3 $Controller @BootstrapArgs
} else {
    & python $Controller @BootstrapArgs
}
exit $LASTEXITCODE
