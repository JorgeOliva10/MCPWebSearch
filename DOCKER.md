# Docker Setup for MCPWebSearch

## Quick Start

### Build and run with Docker Compose:
```bash
docker-compose up -d
```

### Build manually:
```bash
docker build -t mcp-websearch .
```

### Run manually:
```bash
docker run -it --rm mcp-websearch
```

## Usage with Continue/Claude Desktop

Update your MCP configuration to use the Docker container:

```yaml
mcpServers:
  - name: "mcp-websearch"
    transport: stdio
    command: "docker"
    args:
      - "run"
      - "-i"
      - "--rm"
      - "mcp-websearch"
```

## Environment Variables

You can pass environment variables using docker-compose.yml or -e flag:
```bash
docker run -it --rm -e VAR_NAME=value mcp-websearch
```
