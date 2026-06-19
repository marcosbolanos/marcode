import builtins

from marcode.cli.entrypoint import entrypoint

# this "probe" function raises an error if called
_stdin_message: str = "Probe function was called!"
def stdin_prompt_probe(args: str):
    raise RuntimeError(_stdin_message)

def test_entrypoint_calls_input(monkeypatch):
    # we replace the builtin function by the probe funcion
    monkeypatch.setattr(builtins, "input", stdin_prompt_probe)

    # if the entrypoint calls input(), the probe function will run
    probe_was_called: bool = False
    try:
        entrypoint()
    except Exception as e:
        # we make sure it's exactly the error raised by the probe
        if isinstance(e, RuntimeError) and str(e) == _stdin_message:
            probe_was_called = True

    # if the probe was called, that means the function did take stdin
    assert probe_was_called == True
        
