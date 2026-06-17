# TESSERA Operator Loop Chart

```text
+-----------+      +--------------------+      +----------+
| REHYDRATE | ---> | PYTHON LOOP KERNEL | ---> | LOOPBOOK |
+-----------+      +--------------------+      +----------+
        |                    |                       |
        v                    v                       v
+--------+          +----------------+        +---------------+
| LAUNCH | -------> | OBSERVER       | <----- | LIVE STATE    |
+--------+          | read-only UI   |        | status/events |
        |           +----------------+        +---------------+
        v
+--------+      +--------+      +-----+      +----------+
| WORKER | ---> | CHECK  | ---> | RUN | ---> | VALIDATE |
+--------+      +--------+      +-----+      +----------+
                                                |
                                                v
                                        +---------------+
                                        | LEDGER / PUSH |
                                        +---------------+
                                                |
                                                v
                                            +------+
                                            | ROOT |
                                            +------+
```

## Ownership

```text
Python owns: loopbook, observer state, worker phases, gates, runtime, validation, ledger, push routing.
PowerShell owns: opening terminal windows only.
```
