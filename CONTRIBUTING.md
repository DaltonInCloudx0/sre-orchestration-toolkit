# Adding a new operation

1. Create file under `src/sre_orchestration_toolkit/operations/`
2. Define a function with signature `fn(aws, dry_run, **kwargs)`
3. Register the operation in `operations/__init__.py`
4. Add an example YAML in `examples/`
5. Run `sre-toolkit run <your-example>` to verify
