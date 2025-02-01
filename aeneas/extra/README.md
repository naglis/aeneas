# aeneas extras 

This Python package contains
a collection of extra tools for aeneas,
mainly custom TTS engine wrappers.



## `ctw_espeak.py`

A wrapper for the `eSpeak` TTS engine
that executes `eSpeak` via `subprocess`.

This file is an example to illustrate
how to write a custom TTS wrapper,
and how to use it at runtime:

1. Copy the `ctw_espeak.py` file to `/tmp/ctw_espeak.py`
   (or any other directory you like).

2. Run any `aeneas.tools.*` with the following options:

    ```
    -r="tts=custom|tts_path=/tmp/ctw_espeak.py"
    ```

   For example:

    ```bash
    python -m aeneas.tools.execute_task --example-srt -r="tts=custom|tts_path=/tmp/ctw_espeak.py"
    ```

For details, please inspect the `ctw_espeak.py` file,
which is heavily commented and it should help you
create a new wrapper for your own TTS engine.

Note: if you want to use `eSpeak` as your TTS engine
in a production environment,
do NOT use the `ctw_espeak.py` wrapper!
`eSpeak` is the default TTS engine of `aeneas`,
and the `aeneas.espeakwrapper` in the main library
is faster than the `ctw_espeak.py` wrapper.
