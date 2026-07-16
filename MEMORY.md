# MEMORY

> Structured memory for cross-compression and cross-session continuity.
> This file is auto-maintained. Update it at task completion, before compression, and after key decisions.

## Active Topics

### Context-Mode + Memory Management
- RTK v0.39.0 at `~/.rtk/bin/rtk.exe`, OpenCode plugin configured
- context-mode MCP (FTS5 knowledge base), binary at `AppData\npm\node_modules\context-mode`
- Auto-recovery workflow: AGENTS.md checklist → context-mode FTS5 ctx_search → synthesize
- Files: `~/.config/opencode/AGENTS.md`, `~/AGENTS.md`, `~/MEMORY.md`

### MCP Tools Configuration
| MCP | Type | Purpose | Notes |
|-----|------|---------|-------|
| **context-mode** | local | FTS5 knowledge base indexing | PATH shim |
| **drawio** | local (`npx @drawio/mcp`) | Diagram generation | |
| **PaddleOCR** | local (python) | Offline OCR fallback | Pure text extraction only |
| **AnySearch** | remote HTTP | Web search (replaces built-in) | Bearer auth via `{env:ANYSEARCH_API_KEY}` |
| **Z.AI Vision** | local (batch wrapper) | Image/screenshot understanding | Free GLM-4.6V-Flash via bigmodel.cn, 8 tools |

### Available Models & Providers
| Provider | Models | Type | Notes |
|----------|--------|------|-------|
| **Modal** | zai-org/GLM-5-FP8, zai-org/GLM-5.1-FP8 | Free (modalresearch token) | **Default model**: GLM-5.1-FP8 |
| **ZenMux** | z-ai/glm-4.6v-flash-free, z-ai/glm-4.7-flash-free | Free | Fallback |

## Last Decisions

- **Memory strategy**: AGENTS.md + MEMORY.md + context-mode FTS5 (Plan B). Rejected modifier model as over-engineered.
- **RTK**: Complementary compression alongside context-mode (bash output compression + FTS5 indexing).
- **npm prefix**: Set to `%APPDATA%\npm` in `.npmrc` so global packages persist across nvm Node.js version switches. Fixed opencode-ai silently reverting from 1.15 → 1.2.15 after nvm upgrade.
- **MCP wrapper**: Z.AI Vision uses `zai-vision-wrapper.bat` that reads `Z_AI_API_KEY` from registry via `reg query`. Reason: `{env:XXX}` doesn't substitute in MCP `environment` blocks, and Git Bash doesn't inherit Windows USER env vars.
- **Z.AI Vision model**: `Z_AI_VISION_MODEL=glm-4.6v-flash` (free) overrides default paid `glm-4.6v`. `Z_AI_RETRY_COUNT=3` for free-tier rate limiting. PaddleOCR kept as offline fallback.
- **AnySearch MCP**: Replaces opencode's built-in websearch (restricted to OpenCode provider) with better general + vertical search.
- **Provider keys**: Hardcoded in opencode.json for now (Modal modalresearch_, ZenMux sk-ai-...). Move to `{env:XXX}` when/if profile-based env loading is reliable.
- **Model probe scripts** (`D:\models_check\*`): Kept on disk for reference, but results are cleaned from this memory file.

## Open Questions

- 是否需要补充更多 ZenMux 免费模型？

## Search Keywords

*Keywords: [context-mode, MCP, FTS5, AGENTS.md, MEMORY.md, RTK, AnySearch, Z.AI Vision, glm-4.6v-flash, bigmodel.cn, ZHIPU, PaddleOCR, drawio, Modal, GLM-5.1-FP8, ZenMux, nvm, npm prefix, AppData]*

## Completed Tasks

### Infrastructure & Memory
- [x] Install RTK v0.39.0 + configure OpenCode plugin
- [x] Install context-mode globally + configure MCP
- [x] Create AGENTS.md (global + project) with auto-recovery checklist
- [x] Create MEMORY.md template
- [x] Install opencode-brain@1.1.0, configure in plugin array, fix double-nesting bug
- [x] Create $PROFILE script: auto-load env vars from Windows registry
- [x] Set npm prefix to `%APPDATA%\npm`, migrate globals, fix nvm-switch package loss
- [x] Reinstall opencode-ai@1.15.12 (was silently reverted to 1.2.15)
- [x] Fix Modal cold-start timeout (set to false/300s)

### MCP: AnySearch
- [x] Configure remote HTTP MCP, set `ANYSEARCH_API_KEY` env var, verify search works

### MCP: Z.AI Vision
- [x] Upgrade Node.js v20→v22.20.0
- [x] Install `@z_ai/mcp-server@0.1.4`, configure 8 tools
- [x] Set `Z_AI_API_KEY` env var (bigmodel.cn)
- [x] Fix: `Z_AI_VISION_MODEL=glm-4.6v-flash` (was paid `glm-4.6v`)
- [x] Fix: wrapper batch reads key from registry (bypass `{env:XXX}` limitation)
- [x] Verify: analyze_image returns detailed Chinese descriptions with free model
