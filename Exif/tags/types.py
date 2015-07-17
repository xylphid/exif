# field type descriptions as (length, abbreviation, full name, unpack format) tuples
FIELD_TYPES = (
    (0, 'X', 'Proprietary'),  # no such type
    (1, 'B', 'Byte', 'c'),
    (1, 'A', 'ASCII', 'c'),
    (2, 'S', 'Short', 'H'),
    (4, 'L', 'Long', 'L'),
    (8, 'R', 'Ratio', 'L'),
    (1, 'SB', 'Signed Byte', 'i'),
    (1, 'U', 'Undefined', 'c'),
    (2, 'SS', 'Signed Short', 'h'),
    (4, 'SL', 'Signed Long', 'l'),
    (8, 'SR', 'Signed Ratio', 'L'),
)