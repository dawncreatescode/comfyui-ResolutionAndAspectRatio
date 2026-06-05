# Ordered list of (ratio, short descriptor) used across all nodes.
_RATIO_ENTRIES = [
    ("1:1",  "Perfect Square"),
    # Portrait
    ("2:3",  "Classic Portrait"),
    ("3:4",  "Standard Portrait"),
    ("3:5",  "Tall Portrait"),
    ("4:5",  "Artistic Portrait"),
    ("5:7",  "Balanced Portrait"),
    ("5:8",  "Elegant Portrait"),
    ("7:9",  "Modern Portrait"),
    ("9:16", "Vertical Video"),
    ("9:19", "Tall Mobile"),
    ("9:21", "Ultra Tall"),
    ("9:32", "Extreme Tall"),
    # Landscape
    ("3:2",  "Classic Landscape"),
    ("4:3",  "Standard Landscape"),
    ("5:3",  "Wide Landscape"),
    ("5:4",  "Balanced Landscape"),
    ("7:5",  "Elegant Landscape"),
    ("8:5",  "Widescreen"),
    ("9:7",  "Artful Landscape"),
    ("16:9", "HD Cinematic"),
    ("19:9", "Modern Ultrawide"),
    ("21:9", "Anamorphic"),
    ("32:9", "Super Ultrawide"),
]

_LABEL_MAP = {r: label for r, label in _RATIO_ENTRIES}

LANDSCAPE_RATIOS = ["3:2", "4:3", "5:3", "5:4", "7:5", "8:5",
                    "9:7", "16:9", "19:9", "21:9", "32:9"]

PORTRAIT_RATIOS  = ["2:3", "3:4", "3:5", "4:5", "5:7", "5:8",
                    "7:9", "9:16", "9:19", "9:21", "9:32"]

ALL_RATIOS = ["1:1"] + PORTRAIT_RATIOS + LANDSCAPE_RATIOS

RATIO_SET = set(ALL_RATIOS)


def labeled(ratio: str) -> str:
    """'16:9' → '16:9 (HD Cinematic)'"""
    desc = _LABEL_MAP.get(ratio, "")
    return f"{ratio} ({desc})" if desc else ratio


def unlabel(labeled_str: str) -> str:
    """'16:9 (HD Cinematic)' → '16:9'"""
    return labeled_str.split(" ")[0]


# Pre-built labeled lists for INPUT_TYPES dropdowns
ALL_RATIOS_LABELED       = [labeled(r) for r in ALL_RATIOS]
LANDSCAPE_RATIOS_LABELED = [labeled(r) for r in LANDSCAPE_RATIOS]
PORTRAIT_RATIOS_LABELED  = [labeled(r) for r in PORTRAIT_RATIOS]
