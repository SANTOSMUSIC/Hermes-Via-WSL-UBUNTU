# Final Plan for Configuration Update

1.  **Backup**: Already done (`/home/rafi_ansf/.hermes/config.yaml.bak.20261102_174000`).
2.  **Configuration Edits**:
    *   **Auxiliary**: Adding the missing section at the end of the file.
    *   **Compression**: Move `threshold_tokens: 80000` to the `compression:` block (below `protect_last_n: 15`).
    *   **Compression**: Remove `threshold_tokens: 80000` from `prompt_caching:` (it's currently misidentified as prompt caching).
    *   **Agent**: Move `api_max_retries: 2` into `agent:` block; remove top-level definition.

**Validation Strategy**:
1. Run `hermes config check` (if available) or `yaml.safe_load` via local script to ensure validity.
2. Verify with `grep` that `threshold_tokens` is unique and `api_max_retries` is unique.
3. Show diff before apply.
4. Final check of active values.

**Code Verification (Source)**:
- `auxiliary.background_review.enabled` is used in `/home/rafi_ansf/.hermes/hermes-agent/agent/background_review.py`.
- `auxiliary.title_generation.model_upgrade_enabled` is used in `/home/rafi_ansf/.hermes/hermes-agent/agent/title_generator.py`.
Both keys are explicitly parsed in the codebase.

**Plan approved?** If yes, I will generate the final edit.