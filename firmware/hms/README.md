# English Bambu Lab HMS messages

`hms_en.json` pins the complete mapping from Bambu Lab HMS catalogue version
`202609231145`. It contains 1,982 error-code mappings, 313 concise English
display messages, 13 categories and all 409 original English source texts.
Display text uses printable ASCII and at most 50 characters. Categories use
at most 23 characters to fit the firmware's alert title buffer.

Regenerate the firmware header with an existing Python 3 interpreter:

```text
python firmware/hms/generate.py
```

Verify that the header matches its source:

```text
python firmware/hms/generate.py --check
```

The generator uses only Python's standard library and works offline. It
validates message lengths, severity, indices, code ranges and ordering.
`--input` and `--output` can select alternate files.

Each compact entry in `codes` follows `code_fields`: hexadecimal attribute,
hexadecimal code, message index, category index, severity, AMS unit, AMS-HT
flag and slot. Severity is `info`, `warning` or `critical`. Indices preserve
the existing firmware mapping. Each message stores its display `text` and
the original English descriptions in `en`; the original descriptions can
be longer than the display message.

Update the JSON first, then regenerate `firmware/claudinho/hms_en.h`. No live
download or account connection is used during builds.
