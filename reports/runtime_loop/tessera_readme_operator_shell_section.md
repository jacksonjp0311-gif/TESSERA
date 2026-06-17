<!-- TESSERA_OPERATOR_SHELL_START -->
## Tessera v0.2.2 PowerShell Operator Shell

Tessera now has a local Hermes-style PowerShell operator shell. It compresses the runtime loop into grouped sections, status rows, checkers, and run commands so the operator does not have to watch raw implementation code scroll by.

```text
rehydrate -> shell -> compile -> check -> run -> validate -> ledger -> push -> root
```

<details>
<summary><strong>Open the operator shell</strong></summary>

```powershell
cd "C:\Users\jacks\OneDrive\Desktop\Tessera"
.\scripts\tessera-shell.ps1
```

Commands inside the shell:

```text
status
compile
check
run
validate
full
push
help
exit
```

</details>

<details>
<summary><strong>Run the full compressed loop without entering the shell</strong></summary>

```powershell
cd "C:\Users\jacks\OneDrive\Desktop\Tessera"
.\scripts\run-tessera-full-loop.ps1
```

Bash:

```bash
./scripts/run-tessera-full-loop.sh
```

</details>

<details>
<summary><strong>Checkers</strong></summary>

```powershell
python scripts/rcc/check_rcc_nexus.py
python scripts/validation/validate_architecture_contracts.py
python scripts/readme/audit_readme_nexus_discipline.py
python scripts/validation/validate_operator_shell.py
python scripts/validation/validate_runtime_loop_compiler.py
python -m unittest discover -s tests
python -m tessera validate --run outputs/runs/latest
```

</details>

<details>
<summary><strong>Boundary</strong></summary>

```text
The shell may observe.
The shell may compile.
The shell may run local validation.
The shell may push after validation.
The shell may not claim real telemetry transfer.
The shell may not become autonomous authority.
The shell may not import Hermes runtime authority or ASF safety claims.
```

</details>

<!-- TESSERA_OPERATOR_SHELL_END -->