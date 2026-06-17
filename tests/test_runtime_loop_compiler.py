from tessera import loop_compiler

def test_loop_manifest_schema():
    data = loop_compiler.manifest()
    assert data["schema"] == "TESSERA-runtime-loop-compiler-v0.2.0"
    assert len(data["loop_steps"]) >= 8

def test_ascii_contains_disconnect():
    text = loop_compiler.ascii_text()
    assert "DISCONNECT" in text
    assert "TESSERA RUNTIME LOOP COMPILER" in text

def test_runbooks_include_validation():
    assert "validate_runtime_loop_compiler.py" in loop_compiler.bash_text()
    assert "validate_runtime_loop_compiler.py" in loop_compiler.powershell_text()