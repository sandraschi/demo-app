# demo-app IDEAS.md - the tack-on roadmap

This app is the fleet's playground. Everything below is a real tack-on using
actual fleet MCP servers, hardware, and infrastructure. Pick one, wire it in,
watch it grow. The builder (`meta_mcp/scripts/fullstack-builder.ps1`) can
regenerate the base any time - this file is the memory.

## Already built in (v0.1 scaffold)

- [x] **SQLite foundation** - `src/demo_app/db.py`: members, products, orders
      tables, WAL mode, seeded products (patrol sticker, keycap, MCP mug, t-shirt).
- [x] **Membership roster** - `/api/members` CRUD + Members page (add/remove,
      data-testid covered). Start populating it with the fleet.
- [x] **Basic onboarding** - 3-step wizard + Dashboard welcome banner
      (localStorage). Fills `demo-app-member`.
- [x] **Fleet-standard chat** - skill-first preprompt (loads SKILL.md),
      personalities, example prompts, export/clear, Ollama/LM Studio/vLLM
      probe, model dropdown. `skill:` indicator in the controls bar.
- [x] **Local LLM / Ollama** - provider probe + model discovery in Settings
      and Chat, OpenAI-compatible chat completions.
- [x] **Basic webshop** - `/api/products` + `/api/orders` (SQLite), Shop grid,
      localStorage cart (zustand), checkout writes the order.
- [x] **Scheduler foundation** - APScheduler, `patrol` demo job every 5 min,
      `/api/jobs`, `/api/jobs/{id}/run`, ring-buffer logs.
- [x] **Logs + API Docs pages** - live ring buffer viewer, Swagger iframe.

## Robots & physical world

- [ ] **Boomy the safety patrol** (the classic). yahboom-mcp exposes the
      robot (camera + drive). Wire the built-in scheduler job `patrol` to a
      real patrol: every 5 min, drive Boomy a lap, snap a frame, push the
      image to the Logs ring buffer, and alert on anything weird (people in
      restricted zones, open doors). Dashboard gets a "Patrol" KPI card with
      the latest frame.
- [ ] **Roombas vs Boomy turf war**: dreame-mcp vacuums, yahboom patrols.
      Scheduler runs a nightly "who moved what" diff from their telemetry.
- [ ] **Guard dog mode**: when the webapp is idle at night, switch the patrol
      to aggressive frequency (30s interval) and fire a speech-mcp TTS alert
      through the speakers when the robot sees motion.
- [ ] **Robot vacation slideshow**: reuse the demo-capture tooling from
      meta-mcp to record Boomy's patrol laps and render them as a timelapse
      on the Dashboard.

## Fleet MCP hookups (the big one)

- [ ] **MCP client panel**: a new `/fleet` page listing every running fleet
      MCP server (probe the port registry from `mcp-central-docs/operations/
      WEBAPP_PORTS.md`), with a health dot per server and one-click "call a
      tool" playground against the streamable HTTP endpoints.
- [ ] **Morning digest renderer**: call aiwatcher-mcp `opencode_briefing`
      every morning via the scheduler and render the result into the Chat
      page as the first message of the day.
- [ ] **Fleet heartbeat wall**: monitoring-mcp telemetry on a wall-clock
      page - CPU/RAM/disk per repo, repo pulse from fleetwatcher-mcp, git
      dirty-state per repo from git-github-mcp.
- [ ] **Incident mode**: when the AI chat detects the word "down"/"broken",
      auto-fire a fleet-agent-mcp diagnostic run and dump the report into
      the Logs page.
- [ ] **Backup buddy**: multi-backup-mcp job status on the Jobs page next
      to the local scheduler jobs - one pane, all backups.
- [ ] **Learnbot tutors the app**: learnbot-mcp personas dropped into the
      chat personality selector (the local-LLM chat already has the
      personality dropdown - just add the server as a provider).
- [ ] **Members sync**: pull learnbot-mcp personas or aiwatcher subscribers
      into the roster on a schedule (the DB is ready).

## Scheduler expansions (already scaffolded!)

The APScheduler foundation is live: `/api/jobs`, `/api/jobs/{id}/run`,
ring-buffer logging. Tack-ons:

- [ ] Job definitions in a `jobs.yaml` the backend loads on boot (no code
      changes to add jobs).
- [ ] Cron UI: edit interval/expression from the Jobs page instead of code.
- [ ] Job history table (SQLite) instead of the in-memory dict, so runs
      survive restarts.
- [ ] Webhook sinks: each job can POST its result to a URL (slack-style,
      or aiwatcher-mcp fleet ingest).
- [ ] One-shot "run at" scheduling from the UI (delay button on Jobs page).
- [ ] The `patrol` job dispatching real robots (see Robots section).

## Webshop expansions

- [ ] Product images + a Product page (the seed data has 4 items, all text).
- [ ] Order history page (`/api/orders` GET + a My Orders table).
- [ ] Stock levels in SQLite + "sold out" states.
- [ ] Discount codes table.
- [ ] Fleet merch real products (the stickers will sell, trust me).

## AI / LLM expansions

- [ ] **RAG depot**: LanceDB ingestion of fleet docs (llms-full.txt files)
      with semantic search - the arxiv-mcp depot pattern, but for the fleet.
- [ ] **Voice patrol reports**: speech-mcp (fleet voice gateway, port 10909)
      reads the patrol log aloud each morning. The Web Speech hooks are
      already scaffolded as a fallback.
- [ ] **Auto-personality**: detect the user's mood from the first chat
      message via a local model and pre-select a personality (silly, useful).
- [ ] **Streaming chat** - the non-streaming path works; switch to NDJSON
      streaming per the fleet standard.

## Platform / packaging

- [ ] Tauri wrapper is scaffolded (`native/`) - wire the backend spawn +
      `backend-status` event + zoom hook per the fleet standard and ship an
      NSIS installer.
- [ ] `.mcpb` bundle so Claude Desktop can talk to this app's MCP endpoint.
- [ ] Playwright screenshot suite for the README (fleet `just screenshots`).
- [ ] PWA offline mode with the fleet docs mirrored in the cache.

## Absurd but technically real

- [ ] **Patrol diplomacy**: if the patrol camera sees a cat, the app TTSes
      "the cat is patrolling with us today" and logs it as a HIGH event.
- [ ] **Boss key**: Ctrl+Shift+B turns the whole dashboard into a fake
      spreadsheet so nobody knows you run a robot army.
- [ ] **Mood lighting**: flash the amber accent color from the dashboard
      based on the daily digest sentiment score.
- [ ] **Member of the week**: the roster page crowns a member weekly based
      on order count (SQL is trivial, the crown emoji is the hard part).

---

## How to run

```powershell
cd D:\Dev\repos\demo-app
uv sync
bun --prefix webapp install
.\start.ps1          # backend :11140, frontend :11141, opens browser
```

Backend: http://127.0.0.1:11140/docs | Frontend: http://127.0.0.1:11141
Scheduler enabled by default (ENABLE_SCHEDULER=1).
