# Google's MCP Toolbox for Databases, serving the Aria Home Cloud SQL toolset.
# No application code — the tools are declared in tools.yaml.
FROM us-central1-docker.pkg.dev/database-toolbox/toolbox/toolbox:latest

COPY tools.yaml /app/tools.yaml
WORKDIR /app

# Cloud Run provides PORT; Toolbox serves MCP at /mcp.
ENV PORT=8080
CMD ["--tools-file", "/app/tools.yaml", "--address", "0.0.0.0", "--port", "8080"]
