# AO Stack Judge Quick Test

This test uses the released AO2 `0.5.3` binary and a disposable,
credential-free fixture. It does not rebuild source, contact an AI provider,
or modify an existing repository.

## Public release anchors

- AO2 release: `https://github.com/uesugitorachiyo/ao2/releases/tag/v0.5.3`
- Tag target: `947e566bd3f54ed902f3c14fc0c90e21a24359bc`
- Asset count: `5`
- Approved manifest digest: `6f9da69f76b07dc2181f50a411a4350ec1bef0a31b006cb6a57a5fdad7c71a97`
- Optional Control Plane release: `https://github.com/uesugitorachiyo/ao2-control-plane/releases/tag/v0.1.18`
- Control Plane asset count: `7`
- Control Plane approved manifest digest:
  `a2f159896eea954e43d6e19914f4ef6b43aa5686ace72016dffdf0ef0ed4f455`

The final package includes the published `SHA256SUMS`. Verify that file and
the platform archive before running anything.

## macOS aarch64

```sh
set -eu
ROOT="$(mktemp -d "${TMPDIR:-.}/ao-stack-judge.XXXXXX")"
cd "$ROOT"
curl -fL -O "https://github.com/uesugitorachiyo/ao2/releases/download/v0.5.3/ao2-0.5.3-macos-aarch64.tar.gz"
test "$(shasum -a 256 ao2-0.5.3-macos-aarch64.tar.gz | awk '{print $1}')" = "ef89f159fd7d3521c89fe7588e7fee5d32664905c1a3bb1373ce5887a95140ad"
tar -xzf ao2-0.5.3-macos-aarch64.tar.gz
./verify-release.sh
./bin/ao2 version --json
./bin/ao2 doctor --json
```

## Linux x86_64

Use the macOS block with `sha256sum` and:

```text
ao2-0.5.3-linux-x86_64.tar.gz
f0a14b739625f45ec2364681f82047a65381502f8d370952feaf7c17aa7c2c58
```

## Linux aarch64

AO2 v0.5.3 does not publish a Linux aarch64 archive. On Apple Silicon or
other aarch64 hosts, use Docker with `--platform linux/amd64` for the Linux
x86_64 archive and label the result as emulated.

## Windows x86_64 PowerShell

```powershell
$Root = Join-Path $env:TEMP ("ao-stack-judge-" + [guid]::NewGuid())
New-Item -ItemType Directory -Path $Root | Out-Null
Set-Location $Root
$Archive = "ao2-0.5.3-windows-x86_64.tar.gz"
Invoke-WebRequest -Uri "https://github.com/uesugitorachiyo/ao2/releases/download/v0.5.3/$Archive" -OutFile $Archive
if ((Get-FileHash $Archive -Algorithm SHA256).Hash.ToLower() -ne "a553c4d570960817887feef5f04d9119cf7cf025ac67723094ab6577742e736f") { throw "checksum mismatch" }
tar -xzf $Archive
.\Verify-Release.ps1
.\bin\ao2.exe version --json
.\bin\ao2.exe doctor --json
```

## Run the bundled fixture

Copy `fixture/disposable-judge-demo` from the judge package into the disposable
root. Then run from that root, adjusting `AO2` to the extracted binary:

```sh
AO2=/absolute/path/to/extracted/bin/ao2
cp -R /absolute/path/to/judge-package/fixture/disposable-judge-demo ./fixture
git -C fixture init -q
git -C fixture add .
git -C fixture -c user.name="AO Judge" -c user.email="judge@example.invalid" commit -qm baseline
"$AO2" run fixture/workflow/risky-pr.yaml --target fixture --run-id judge-demo
"$AO2" runs show judge-demo --target fixture --json
"$AO2" report judge-demo --target fixture
```

Expected final result: `macOS native passed; Linux x86_64 Docker emulation passed; hosted Ubuntu/macOS/Windows public release consumer smoke run 29809470476 passed`. The accepted run must
report zero digest failures and retain local evidence. The workflow may stop
at an exact-action-digest approval gate; follow the released CLI’s printed
resume instruction only after reviewing the patch and digest.

Cleanup is `rm -rf "$ROOT"` on macOS/Linux or
`Remove-Item -Recurse -Force $Root` on Windows.

This proves that the published archive verifies and that AO2 can execute,
gate, replay, and report one bounded local workflow on the tested host. It
does not start all fourteen services, contact a provider, deploy software, or
prove every production environment.
