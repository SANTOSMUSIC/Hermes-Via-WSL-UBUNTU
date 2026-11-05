# ADR 001: Cost Pricing Configuration for 9Router and NVIDIA NIM Free Tier

**Date:** 2026-11-05  
**Status:** Accepted  
**Author:** Supermaster (Hermes Multi-Agent)

## Context

The Hermes agent tracks API usage costs via `session_model_usage` table, but all entries showed `cost_status=unknown`, `cost_source=none`, and `estimated_cost_usd=0.0` because:

1. **No pricing for 9Router aliases**: Profile models `hermes-kuat`, `hermes-kode`, `hermes-hemat` route via 9Router (localhost:20128) which maps to NVIDIA NIM models, but no pricing entry existed for these aliases or the NVIDIA NIM models.
2. **Missing cache pricing**: The agent sends `cache_read_tokens` (e.g., 8768 tokens) from 9Router responses, but pricing entries lacked `cache_read_cost_per_million`, causing the pricing engine to return `_unknown_cost("none")` when cache tokens > 0.

## Decision

Added two pricing snapshots to `usage_pricing.py`:

### 1. NVIDIA NIM Free Tier (`nvidia-nim-free-2026-11`)
- Provider: `nvidia`
- 12 models at $0.00 input / $0.00 output / $0.00 cache_read
- Models: `nemotron-3-ultra-550b-a55b`, `moonshotai/kimi-k2.6`, `minimaxai/minimax-m2.7`, `minimaxai/minimax-m3`, `z-ai/glm-5.2`, `deepseek-ai/deepseek-v4-pro`, `deepseek-ai/deepseek-v4-flash`, `nemotron-3-super-120b-a12b`, `nemotron-3-nano-omni-30b-a3b-reasoning`, `nemotron-4-340b-instruct`, `llama-3.1-nemotron-70b-instruct`, `llama-3.1-nemotron-51b-instruct`

### 2. 9Router Aliases (`9router-aliases-2026-11`)
- Provider: `custom` (matches 9Router profile config)
- 3 aliases at $0.00 input / $0.00 output / $0.00 cache_read
- Models: `hermes-kuat`, `hermes-kode`, `hermes-hemat`

Both snapshots include `cache_read_cost_per_million="0.00"` to handle 9Router's cache token reporting.

## Files Changed

- `/home/rafi_ansf/.hermes/hermes-agent/agent/usage_pricing.py` (main installation)
- `/home/rafi_ansf/.hermes/installs/031eda30dd5b63c3/environments/ad53cfcffc3c4e4a9c891fcbc9d27827/workspace/agent/usage_pricing.py` (install environment)

## Verification

**Before fix:**
```
hermes-kuat|custom|http://localhost:20128/v1|0.0|0.0|unknown|none
```

**After fix:**
```
hermes-kuat|custom|http://localhost:20128/v1|0.0|0.0|estimated|official_docs_snapshot
```

Cost report now correctly shows `cost_status=estimated` and `cost_source=official_docs_snapshot` for new sessions.

## Notes

- NVIDIA NIM direct API (integrate.api.nvidia.com/v1) returns 403 with current API key — fallback chain is single-provider (9Router only). True cross-provider redundancy requires valid NVIDIA NIM chat completion access.
- Cost tracking threshold: 830 API calls/day, 8M tokens/day (2x observed peak). Current usage well within limits.
- Pricing applies to **new sessions only**; historical data remains at $0.00/unknown.

## Related

- ADR 000: Hermes Self-Assessment Baseline
- VERIF-4: Secret Scanning (detected NVIDIA_API_KEY in config)
- Slot 6: Live Fallback Test Results