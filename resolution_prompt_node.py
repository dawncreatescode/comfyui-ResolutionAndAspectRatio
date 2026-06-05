import json
import random
import re
from pathlib import Path
from .ratios import (
    ALL_RATIOS, ALL_RATIOS_LABELED,
    LANDSCAPE_RATIOS, PORTRAIT_RATIOS,
    RATIO_SET, unlabel,
)

_KEYWORDS_FILE = Path(__file__).parent / "keywords.json"

# Detection modes
MODE_OFF      = "Off"
MODE_AR_ONLY  = "AR only"
MODE_LIMITED  = "Limited keywords"
MODE_ALL      = "All keywords"
MODES = [MODE_OFF, MODE_AR_ONLY, MODE_LIMITED, MODE_ALL]

_SPECIAL_RATIO_POOLS = {
    "$LANDSCAPE": LANDSCAPE_RATIOS,
    "$PORTRAIT":  PORTRAIT_RATIOS,
}

# Each rule: (label, compiled_regex, pool, weights, min_mode)
_keyword_rules = []


def _words_to_regex(words):
    """Build a case-insensitive pattern from a list of words/phrases."""
    parts = []
    for w in words:
        # Split phrase into tokens, escape each, join with \s+ for flexible spacing
        tokens = [re.escape(t) for t in w.split()]
        parts.append(r'\b' + r'\s+'.join(tokens) + r'\b')
    return re.compile('|'.join(parts), re.I)


def _load_keywords():
    global _keyword_rules
    try:
        with open(_KEYWORDS_FILE, encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = []

    rules = []
    for entry in data:
        words    = entry.get("words", [])
        raw_ratios = entry.get("ratios", [])
        weights  = entry.get("weights") or None
        category = entry.get("category", "all")

        if isinstance(raw_ratios, str):
            pool = _SPECIAL_RATIO_POOLS.get(raw_ratios, [])
        else:
            pool = [r for r in raw_ratios if r in RATIO_SET]

        min_mode = MODE_LIMITED if category == "limited" else MODE_ALL
        rules.append((entry.get("label", ""), _words_to_regex(words), pool, weights, min_mode))

    _keyword_rules = rules


_load_keywords()


def _detect(prompt: str, mode: str):
    """Returns (fixed_ratio_or_None, label_or_None, pool_or_None, weights_or_None)."""
    if mode == MODE_OFF:
        return None, None, None, None

    # Explicit ratio written in the prompt (e.g. "16:9") — always active
    for w, h in re.findall(r'\b(\d+):(\d+)\b', prompt):
        candidate = f"{w}:{h}"
        if candidate in RATIO_SET:
            return candidate, "from prompt", None, None

    # Keyword rules filtered by mode
    if mode != MODE_AR_ONLY:
        for label, pattern, pool, weights, min_mode in _keyword_rules:
            if mode == MODE_LIMITED and min_mode == MODE_ALL:
                continue
            if pattern.search(prompt):
                return None, label, pool, weights

    return None, None, None, None


def _dims(ratio_str, megapixels, round_to):
    w_ratio, h_ratio = map(int, ratio_str.split(":"))
    total_pixels = float(megapixels) * 1_000_000
    dimension = (total_pixels / (w_ratio * h_ratio)) ** 0.5
    width  = round(int(dimension * w_ratio) / round_to) * round_to
    height = round(int(dimension * h_ratio) / round_to) * round_to
    return width, height


# ── API routes ────────────────────────────────────────────────────────────────
try:
    from server import PromptServer
    from aiohttp import web

    @PromptServer.instance.routes.get("/smart_resolution/keywords")
    async def _get_keywords(request):
        try:
            with open(_KEYWORDS_FILE, encoding="utf-8") as f:
                data = json.load(f)
            return web.json_response(data)
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)

    @PromptServer.instance.routes.post("/smart_resolution/keywords")
    async def _save_keywords(request):
        try:
            data = await request.json()
            with open(_KEYWORDS_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            _load_keywords()
            return web.json_response({"ok": True})
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)

except Exception:
    pass  # PromptServer not available outside ComfyUI (e.g. tests)


# ── Node ──────────────────────────────────────────────────────────────────────
class ResolutionNode:
    @classmethod
    def INPUT_TYPES(cls):
        megapixel_options = [f"{i / 10:.1f}" for i in range(1, 26)]
        return {
            "required": {
                "megapixels":   (megapixel_options, {"default": "1.0"}),
                "aspect_ratio": (ALL_RATIOS_LABELED, {"default": "1:1 (Perfect Square)"}),
                "divisible_by": (["8", "16", "32", "64"], {"default": "64"}),
                "keyword_mode": (MODES, {"default": MODE_LIMITED}),
                "randomize":    ("BOOLEAN", {"default": False, "label_on": "Random", "label_off": "Fixed"}),
                "seed":         ("INT", {"default": 0, "min": 0, "max": 0xFFFFFFFFFFFFFFFF}),
            },
            "optional": {
                "prompt": ("STRING", {"forceInput": True}),
            },
        }

    RETURN_TYPES  = ("INT", "INT", "STRING")
    RETURN_NAMES  = ("width", "height", "ratio")
    FUNCTION      = "calculate"
    CATEGORY      = "Resolution"

    @classmethod
    def IS_CHANGED(cls, randomize, **kwargs):
        if randomize:
            return float("nan")
        return False

    def calculate(self, megapixels, aspect_ratio, divisible_by, keyword_mode, randomize, seed, prompt=""):
        round_to = int(divisible_by)
        rng = random.Random(seed)

        fixed_ratio, label, pool, weights = _detect(prompt or "", keyword_mode)

        if fixed_ratio:
            ratio_str = fixed_ratio
        elif pool is not None:
            ratio_str = rng.choices(pool, weights=weights, k=1)[0]
        else:
            ratio_str = rng.choice(ALL_RATIOS) if randomize else unlabel(aspect_ratio)
            label = None

        ratio_out = f"{ratio_str} ({label})" if label else ratio_str
        width, height = _dims(ratio_str, megapixels, round_to)
        return width, height, ratio_out


NODE_CLASS_MAPPINGS = {
    "ResolutionNode": ResolutionNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ResolutionNode": "Smart Resolution",
}
