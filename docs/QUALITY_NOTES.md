# Quality checks

The repository now declares `ruff.toml` so the correctness gate has the same scope
on developer machines and GitHub runners: E4/E7/E9 and F (imports, syntax-related
issues and undefined/unused names). CI passes an explicit config path and does
not convert lint or security failures into successful exits.

The first runner inherited a much broader global Ruff configuration, producing
additional modernization, import-order, exception-handling and style diagnostics
not declared by this project. Those diagnostics are not asserted to be fixed.
Broader cleanup should be reviewed incrementally with behavior tests rather than
silently rewriting the GUI and analysis modules to satisfy every host-specific
rule. A passing correctness gate is not a claim that all style/security concerns
have been eliminated.

The 234-test audit run required public tiktoken tables to be cached first and then
passed with external sockets disabled. Docker runtime and live AI-provider calls
were not tested. Dependency auditing applies to the resolved environment at the
time of the run, not every future resolution of the broad dependency ranges.
