import builtins, os

from marcode.cli.entrypoint import entrypoint

# this "probe" function raises an error if called
_stdin_message: str = "Probe function was called!"

os.environ["OPENAI_API_KEY"] = "foo"


# The entrypoint should return 1 and not do anything else if no API key
def test_API_key_check(monkeypatch):
    # an empty string is falsy
    monkeypatch.setenv("OPENAI_API_KEY", "")
    assert entrypoint() == 1


def test_entrypoint_calls_input(monkeypatch):

    def stdin_prompt_probe(*args, **kwargs):
        raise RuntimeError(_stdin_message)

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


# test if the function handles keybardinterrupt signals
def test_entrypoint_ends_gracefully(monkeypatch):

    # mock the user doing KeyboardInterrupt
    def interrupt_probe(*args, **kwargs):
        raise KeyboardInterrupt

    # we replace input() with keybardinterrupt
    monkeypatch.setattr(builtins, "input", interrupt_probe)
    entrypoint()  # if the keyboardinterrupt isn't handled, test fails
