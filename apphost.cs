#:sdk Aspire.AppHost.Sdk@13.1.0
#:package Aspire.Hosting@13.1.0
#:package Aspire.Hosting.Python@13.1.0
#:package Aspire.Hosting.JavaScript@13.1.0

var builder = DistributedApplication.CreateBuilder(args);

// Parameters can be overridden in apphost.run.json.
// NOTE: These paths are consumed by the `ai-processing` app, whose working directory is `./ai-processing`.
// So they must be relative to that directory (or be absolute paths).
var documentsPath = builder.AddParameter("documents-path", "../../PrismWeaveDocs/documents");
var chromaPersistDir = builder.AddParameter(
    "chroma-persist-dir",
    "../../PrismWeaveDocs/.prismweave/chroma_db"
);
var articleIndexPath = builder.AddParameter(
    "article-index-path",
    "../../PrismWeaveDocs/documents/.prismweave/index/articles.json"
);
var ollamaHost = builder.AddParameter("ollama-host", "http://localhost:11434");

var aiProcessing = builder
    .AddUvicornApp("ai-processing", "./ai-processing", "src.unified_app:app")
    .WithUv()
    // Fixed host port + provide the internal listen port via env var.
    // IMPORTANT: Use the name-based overload (named arg) to mutate the existing "http"
    // endpoint created by AddUvicornApp, rather than adding a second "http" endpoint.
    .WithEndpoint(
        endpointName: "http",
        e =>
        {
            e.Port = 4001;
            e.TargetPort = 4001;
            e.UriScheme = "http";
            e.Transport = "http";
            e.IsProxied = false;
            e.IsExternal = true;
        },
        createIfNotExists: true
    )
    .WithHttpHealthCheck("/health")
    .WithEnvironment("PYTHONUNBUFFERED", "1")
    .WithEnvironment("UVICORN_PORT", "4001")
    .WithEnvironment("LOG_LEVEL", "INFO")
    .WithEnvironment("OLLAMA_HOST", ollamaHost)
    .WithEnvironment("DOCUMENTS_PATH", documentsPath)
    .WithEnvironment("CHROMA_PERSIST_DIR", chromaPersistDir)
    .WithEnvironment("ARTICLE_INDEX_PATH", articleIndexPath);

// Standalone MCP server (FastMCP over SSE) as a separate Aspire process/resource.
// SSE endpoint is available at: {mcp-server base URL}/sse
var mcpServer = builder
    // NOTE: We intentionally run this as plain HTTP. Aspire's Python hosting can
    // inject a self-signed TLS cert for uvicorn, but VS Code's MCP SSE client does
    // not (currently) provide a reliable per-server way to disable cert validation.
    // Running HTTP here keeps local dev friction-free.
    .AddExecutable(
        "mcp-server",
        "./.venv/bin/python3",
        "./ai-processing",
        "-m",
        "uvicorn",
        "src.mcp_app:app",
        "--host",
        "127.0.0.1",
        "--port",
        "4005",
        "--reload"
    )
    .WithEndpoint(
        endpointName: "http",
        e =>
        {
            e.Port = 4005;
            e.TargetPort = 4005;
            e.UriScheme = "http";
            e.Transport = "http";
            e.IsProxied = false;
            e.IsExternal = true;
        },
        createIfNotExists: true
    )
    .WithHttpHealthCheck("/health")
    .WithEnvironment("PYTHONUNBUFFERED", "1")
    .WithEnvironment("UVICORN_PORT", "4005")
    .WithEnvironment("LOG_LEVEL", "INFO")
    .WithEnvironment("OLLAMA_HOST", ollamaHost)
    .WithEnvironment("DOCUMENTS_PATH", documentsPath)
    .WithEnvironment("CHROMA_PERSIST_DIR", chromaPersistDir)
    .WithEnvironment("ARTICLE_INDEX_PATH", articleIndexPath);

// Add an explicit dashboard URL that includes the SSE path.
// (Aspire endpoints are base addresses; paths like /sse are best represented as Resource URLs.)
mcpServer.WithUrlForEndpoint("http", _ => new() { Url = "/sse", DisplayText = "MCP SSE" });

// MCP Inspector (UI + proxy) managed by Aspire.
// The Inspector is a separate Node process; it is NOT hosted by FastMCP.
// Defaults are 6274 (UI) + 6277 (proxy); we pin them to avoid port drift.
const int mcpInspectorUiPort = 4009;
const int mcpInspectorProxyPort = 4010;
const string mcpInspectorAuthToken = "prismweave-dev-inspector-token";

var mcpInspector = builder
    .AddExecutable(
        "mcp-inspector",
        "npx",
        "./ai-processing",
        "-y",
        "@modelcontextprotocol/inspector"
    )
    .WithEnvironment("CLIENT_PORT", mcpInspectorUiPort.ToString())
    .WithEnvironment("SERVER_PORT", mcpInspectorProxyPort.ToString())
    .WithEnvironment("MCP_PROXY_AUTH_TOKEN", mcpInspectorAuthToken)
    .WithEndpoint(
        endpointName: "http",
        e =>
        {
            e.Port = mcpInspectorUiPort;
            e.TargetPort = mcpInspectorUiPort;
            e.UriScheme = "http";
            e.Transport = "http";
            e.IsProxied = false;
            e.IsExternal = true;
        },
        createIfNotExists: true
    );

// Dashboard convenience link: opens Inspector UI, pre-populated to connect to our SSE endpoint.
// (Token is fixed via MCP_PROXY_AUTH_TOKEN so the link stays stable.)
var mcpSseUrl = "http://127.0.0.1:4005/sse";
var encodedMcpSseUrl = Uri.EscapeDataString(mcpSseUrl);
var encodedAuthToken = Uri.EscapeDataString(mcpInspectorAuthToken);
mcpInspector.WithUrlForEndpoint(
    "http",
    _ =>
        new()
        {
            Url = $"/?transport=sse&serverUrl={encodedMcpSseUrl}&MCP_PROXY_AUTH_TOKEN={encodedAuthToken}",
            DisplayText = "MCP Inspector",
        }
);

var visualization = builder
    .AddViteApp("visualization", "./visualization")
    .WithNpm(installCommand: "ci", installArgs: ["--no-audit", "--no-fund"])
    .WithRunScript("dev")
    // Mutate the existing default "http" endpoint so Vite actually binds to a fixed port.
    .WithEndpoint(
        endpointName: "http",
        e =>
        {
            e.Port = 4002;
            e.TargetPort = 4002;
            e.UriScheme = "http";
            e.Transport = "http";
            e.IsProxied = false;
            e.IsExternal = true;
        },
        createIfNotExists: true
    )
    .WithEnvironment("PORT", "4002")
    .WithEnvironment("API_URL", aiProcessing.GetEndpoint("http"))
    .WithReference(aiProcessing)
    .WaitFor(aiProcessing);

var website = builder
    .AddNodeApp("website", "./website", "scripts/dev-server.mjs")
    .WithNpm(installCommand: "ci", installArgs: ["--no-audit", "--no-fund"])
    // Mutate the existing default "http" endpoint so the node dev server binds to a fixed port.
    .WithEndpoint(
        endpointName: "http",
        e =>
        {
            e.Port = 4003;
            e.TargetPort = 4003;
            e.UriScheme = "http";
            e.Transport = "http";
            e.IsProxied = false;
            e.IsExternal = true;
        },
        createIfNotExists: true
    )
    .WithEnvironment("PORT", "4003")
    .WithEnvironment("API_URL", aiProcessing.GetEndpoint("http"))
    .WithReference(aiProcessing)
    .WaitFor(aiProcessing);

builder.Build().Run();
