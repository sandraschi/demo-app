# demo-app Skill

This server exposes FastMCP tools for the demo-app webapp.

## Tools

- `app_info` - server metadata, version, tool count
- `example_op` - portmanteau example: hello, echo

## Usage

Call `app_info()` first to discover the server state, then use
`example_op(operation=..., name=...)` for demonstration.