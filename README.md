# ComfyUI Smart Aspect Ratio

A ComfyUI custom node that converts a megapixel target and aspect ratio into pixel dimensions (`width` × `height`). The ratio can be fixed, randomized, or **detected automatically from a connected prompt**.

---

## Features

- **23 aspect ratios** from 1:1 to 32:9 (portrait, square, landscape)
- **Prompt-based detection** — connect your text prompt and the node picks the right ratio automatically
- **Explicit ratio override** — writing `16:9` anywhere in the prompt forces that exact ratio
- **Keyword matching** — terms like `cinematic`, `widescreen`, `portrait`, or `anamorphic` map to weighted ratio pools
- **Randomization** — seed-controlled random ratio when nothing is detected
- **Editable keyword rules** — click *Edit Keywords* on the node to add, remove, or modify rules live

---

## Installation

**Via ComfyUI Manager:** search for `Smart Resolution`.

**Manual:**
```bash
cd ComfyUI/custom_nodes
git clone https://github.com/dawncreatescode/comfyui-ResolutionAndAspectRatio
```

Restart ComfyUI. The node appears under the **Resolution** category.

---

## Inputs

| Input | Type | Description |
|-------|------|-------------|
| `megapixels` | Dropdown | Target image size, 0.1–2.5 MP |
| `aspect_ratio` | Dropdown | Fallback ratio when detection is off or finds nothing |
| `divisible_by` | Dropdown | Round dimensions to this multiple (8 / 16 / 32 / 64) |
| `keyword_mode` | Dropdown | Controls which prompt keywords trigger detection |
| `randomize` | Boolean | Pick a random ratio when no keyword/prompt match fires |
| `seed` | INT | Controls which ratio is picked when randomizing |
| `prompt` | STRING *(optional)* | Text to scan — connect to the same node as your CLIP encoder |

## Outputs

| Output | Description |
|--------|-------------|
| `width` | Image width in pixels |
| `height` | Image height in pixels |
| `ratio` | Selected ratio with detection source, e.g. `16:9 (cinematic)` |

> `divisible_by 64` works for most models (SD 1.5, SDXL). Use 8 or 16 for custom VAEs.

---

## Ratio Detection

Detection runs in this priority order:

1. **Explicit ratio in the prompt** — `16:9` anywhere forces that exact ratio
2. **Keyword match** — picks from a weighted pool based on matched term
3. **Fallback** — fixed `aspect_ratio` dropdown, or random if *Randomize* is on

The `ratio` output string shows what triggered the selection: `21:9 (from prompt)`, `16:9 (cinematic)`, etc. Connect it to a Show Text node to monitor it.

### Keyword Mode

| Mode | What triggers |
|------|--------------|
| **Off** | Nothing — uses fixed or random ratio |
| **AR only** | Only explicit ratios written in the prompt |
| **Limited keywords** *(default)* | Explicit ratios + unambiguous AR terms |
| **All keywords** | Explicit ratios + all rules including content words |

`Limited keywords` only matches terms that clearly describe a format (`widescreen`, `anamorphic`, `ultrawide`). `All keywords` also catches content words like `cinematic`, `portrait`, `poster`, or `phone`.

### Default Keyword Rules

| Words | Ratio pool | Mode |
|-------|------------|------|
| `anamorphic` | `21:9` | Limited+ |
| `imax` | `4:3` | Limited+ |
| `ultrawide` | `21:9` `32:9` | Limited+ |
| `widescreen` | `16:9` `19:9` `21:9` | Limited+ |
| `panorama`, `panoramic` | `16:9` `19:9` `21:9` `32:9` | Limited+ |
| `square`, `avatar`, `thumbnail` | `1:1` | All |
| `mobile`, `phone`, `smartphone` | `9:16` `9:19` `9:21` | All |
| `poster` | `2:3` `3:4` `4:5` | All |
| `cinematic` | `16:9` `21:9` `32:9` | All |
| `banner` | `16:9` `21:9` `32:9` | All |
| `wallpaper` | `16:9` `21:9` `32:9` | All |
| `landscape`, `horizontal`, `wide angle`, `wide shot` | All landscape ratios | All |
| `portrait`, `vertical`, `tall` | All portrait ratios | All |

When a keyword maps to multiple ratios, one is picked by weighted random using the seed. Change the seed for a different pick within the same pool.

---

## Editing Keywords

Click **Edit Keywords** on the node to open the live editor. Each rule has:

- **Words** — comma-separated trigger words/phrases (case-insensitive, phrase-aware)
- **Ratios** — comma-separated ratio pool, or `$LANDSCAPE` / `$PORTRAIT` for the full sets
- **Weights** — optional; controls probability of each ratio (leave blank for equal chance)
- **Category** — `limited` = active in Limited + All modes; `all` = active in All mode only

Changes are saved to `keywords.json` in the node folder and take effect immediately.

---

## Supported Aspect Ratios

**Portrait:** `2:3` `3:4` `3:5` `4:5` `5:7` `5:8` `7:9` `9:16` `9:19` `9:21` `9:32`

**Square:** `1:1`

**Landscape:** `3:2` `4:3` `5:3` `5:4` `7:5` `8:5` `9:7` `16:9` `19:9` `21:9` `32:9`

---

## License

[MIT](LICENSE)
