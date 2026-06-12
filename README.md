# ComfyUI Smart Aspect Ratio

A ComfyUI custom node that converts a megapixel target and aspect ratio into pixel dimensions (`width` × `height`). The ratio can be fixed, randomized, or **detected automatically from a connected prompt**.

Type `cinematic ultrawide city at night` and the node hands your latent a 21:9 resolution. Write `16:9` anywhere in the prompt and it obeys exactly. Or skip detection entirely and use it as a clean megapixels-plus-ratio resolution picker and/or randomize the aspect ratio for each run.

![node screenshot](docs/nodeScreenShot.png)

---


## Features

- **23 aspect ratios** from 9:32 portrait to 32:9 landscape
- **Prompt-based detection** — connect your prompt text and the node picks a fitting ratio automatically
- **Explicit override** — writing `16:9` (or any accepted ratio) in the prompt forces it exactly
- **Keyword matching** — terms like `cinematic`, `widescreen`, `portrait`, or `anamorphic` map to weighted ratio pools
- **Seed-controlled randomization** — choose between a fixed or random ratio when nothing matches, reproducible via seed
- **Editable keyword rules** — click *Edit Keywords* on the node to change the mapping, no restart needed

## Installation

**ComfyUI Manager:** search for **Smart Aspect Ratio**. <!-- keep this in sync with the registry DisplayName -->

**Manual:**

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/dawncreatescode/comfyui-ResolutionAndAspectRatio
```

Restart ComfyUI. The node appears under the **Resolution** category.

## Quick start

1. Add the node: **Add Node → Resolution → Smart Aspect Ratio**.
2. On your **Empty Latent Image**, connect `width` and `height` to this node.
3. *(Optional, for prompt detection)* Feed the **same prompt string** into both your CLIP Text Encode and this node's `prompt` input — e.g. from a String/Primitive node:

```
[String: prompt] ──┬──→ [CLIP Text Encode] ──→ ...
                   └──→ [Smart Aspect Ratio] ──width───→ [Empty Latent Image]
                                              ──height──→
```

4. Pick a `megapixels` target (1.0 ≈ SDXL native) and you're done. Without a `prompt` connection, the node is a simple ratio/resolution picker using the `aspect_ratio` dropdown.

## How the ratio is chosen

Detection runs in strict priority order — first match wins:

1. **Explicit ratio in the prompt.** `16:9 photo of a harbor` → `16:9 (from prompt)`. Always wins.
2. **Keyword match.** `anamorphic close-up` → `21:9 (anamorphic)`. When a keyword maps to several ratios (e.g. `widescreen` → 16:9 / 19:9 / 21:9), one is picked by weighted random using the seed.
3. **Fallback.** Nothing matched → the fixed `aspect_ratio` dropdown, or a random ratio if `randomize` is on.

The `ratio` output always tells you *what fired* — `21:9 (from prompt)`, `16:9 (cinematic)`, `4:5 (fallback)`. Connect it to a Show Text node while you're tuning.

### Keyword modes — and why `Limited` is the default

| Mode | What triggers detection |
|---|---|
| **Off** | Nothing — fixed or random ratio only |
| **AR only** | Only explicit ratios written in the prompt (`16:9`, `3:2`, …) |
| **Limited keywords** *(default)* | Explicit ratios + unambiguous format terms (`widescreen`, `anamorphic`, `ultrawide`, …) |
| **All keywords** | Everything above + content words (`cinematic`, `portrait`, `poster`, `phone`, …) |

Content words are powerful but can be unintended: in `portrait of a king`, "portrait" describes the *subject*, not the orientation — yet `All` mode will dutifully make the image tall. `Limited` only reacts to words that unambiguously describe a format, which is why it's the default. Switch to `All` when you want maximum hands-off behavior and your prompts don't use those words for content.

### Default keyword rules

| Words | Ratio pool | Active in |
|---|---|---|
| `anamorphic` | `21:9` | Limited + All |
| `imax` | `4:3` | Limited + All |
| `ultrawide` | `21:9` `32:9` | Limited + All |
| `widescreen` | `16:9` `19:9` `21:9` | Limited + All |
| `panorama`, `panoramic` | `16:9` `19:9` `21:9` `32:9` | Limited + All |
| `square`, `avatar`, `thumbnail` | `1:1` | All only |
| `mobile`, `phone`, `smartphone` | `9:16` `9:19` `9:21` | All only |
| `poster` | `2:3` `3:4` `4:5` | All only |
| `cinematic` | `16:9` `21:9` `32:9` | All only |
| `banner`, `wallpaper` | `16:9` `21:9` `32:9` | All only |
| `landscape`, `horizontal`, `wide angle`, `wide shot` | all landscape ratios | All only |
| `portrait`, `vertical`, `tall` | all portrait ratios | All only |

## Supported aspect ratios

**Portrait:** `2:3` `3:4` `3:5` `4:5` `5:7` `5:8` `7:9` `9:16` `9:19` `9:21` `9:32` · **Square:** `1:1` · **Landscape:** `3:2` `4:3` `5:3` `5:4` `7:5` `8:5` `9:7` `16:9` `19:9` `21:9` `32:9`

### Editing the rules

Click **Edit Keywords** on the node. Each rule has:

- **Words** — comma-separated triggers (case-insensitive, phrase-aware)
- **Ratios** — comma-separated pool, or `$LANDSCAPE` / `$PORTRAIT` for the full sets
- **Weights** — optional per-ratio probabilities (blank = equal chance)
- **Category** — `limited` (active in Limited + All) or `all` (All mode only)

Changes save to `keywords.json` in the node folder and apply immediately.


## Node reference

### Inputs

| Input | Type | Description |
|---|---|---|
| `megapixels` | dropdown | Pixel budget, 0.1–2.5 MP (1.0 ≈ SDXL native, ~0.25 ≈ SD 1.5 native) |
| `aspect_ratio` | dropdown | Fallback ratio when detection is off or finds nothing |
| `divisible_by` | dropdown | Round dimensions to a multiple of 8 / 16 / 32 / 64 — see below |
| `keyword_mode` | dropdown | Which prompt keywords trigger detection (see [modes](#keyword-modes--and-why-limited-is-the-default)) |
| `randomize` | boolean | Pick a random ratio when nothing matches |
| `seed` | INT | Fixed seed → reproducible picks; set *control_after_generate* to `randomize` for variety per run |
| `prompt` | STRING *(optional)* | The text to scan — same string you feed your CLIP Text Encode |

### Outputs

| Output | Description |
|---|---|
| `width` | Image width in pixels |
| `height` | Image height in pixels |
| `ratio` | Selected ratio + what triggered it, e.g. `16:9 (cinematic)` |

### Choosing `divisible_by`

Stable Diffusion latents require dimensions divisible by 8, so 8 is the hard minimum. Larger multiples (32, 64) are safer across models and avoid edge artifacts some checkpoints show at odd sizes — at the cost of landing slightly further from your exact ratio and megapixel target. **Rule of thumb: leave it at 64; drop to 16 or 8 only if you need shapes as exact as possible and know your model handles them.**


## Troubleshooting

**My keyword isn't detected.** Check `keyword_mode` — content words like `cinematic` need `All keywords`. Also confirm the `prompt` input is actually connected; the node can't see text it isn't given.

**Dimensions aren't exactly my ratio.** That's `divisible_by` rounding. Lower it for a closer fit.

**`randomize` gives the same ratio every run.** The seed is fixed. Set the seed widget's *control_after_generate* to `randomize`.

**Which ratio fired, and why?** Connect the `ratio` output to a Show Text node — it names the trigger.

## License

[MIT](LICENSE)
