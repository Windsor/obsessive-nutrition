# GoAPI Midjourney Generator

Generate images via GoAPI's Midjourney endpoint.

## Files
- `generate.py` — Create Midjourney imagine tasks, poll for results, upscale

## Usage
```bash
python3 generate.py --prompt "your prompt" --aspect "10:16"
```

## Config
- API key in `TOOLS.md`
- Uses `service_mode: public` (private bot expired)
- Also supports Gemini image gen, Flux, and other models via GoAPI
