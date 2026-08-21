# Reusable Windows preflight

Run from a fresh checkout and choose one profile:

```powershell
python factory/windows-remediation/reusable-windows-preflight/windows_preflight.py --profile binary --json --root (Get-Location)
```

Profiles are `binary`, `ao-source`, and `go-node`. The tool is read-only: it
does not install packages, alter PATH, change Git configuration, inspect
credentials, or call providers. Exit `0` means every required check passed;
exit `1` identifies missing or unusable capabilities in machine-readable JSON.

The executable path fields are exact diagnostic output. Public retained
evidence must sanitize user-specific paths while preserving tool names,
versions, classifications, and failure guidance.
