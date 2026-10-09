# Investigations

These scripts were used to discover the actual public API surface of
the installed Deltakit SDK (version 0.10.1, deltakit-explorer 0.9.3)
before writing tests against it.

They are kept in the repository because the method - inspect first,
then test - is part of the deliverable. Every one of these scripts is
the reason a specific test exists, or a specific defect was found.

| Script                                | Purpose                                                |
|---------------------------------------|--------------------------------------------------------|
| explore_api.py                        | Enumerate top-level packages and verify entry points   |
| inspect_repetition_code.py            | Discover the real attributes of RepetitionCode         |
| inspect_stabilisers.py                | Determine the structure of .stabilisers across codes   |
| inspect_rotated_planar.py             | Discover the true signature of RotatedPlanarCode       |
| inspect_rotated_planar_structure.py   | Examine stabiliser and parity-matrix structure         |
| inspect_stabiliser_bases.py           | Disambiguate grouping convention in .stabilisers       |
| inspect_remaining_api.py              | Measurements, decoders, Client, exception types        |

To re-run:

    python investigations/<script>.py
