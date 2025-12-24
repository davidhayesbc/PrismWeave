#:sdk Aspire.AppHost.Sdk@13.1.0
#:package Aspire.Hosting.Python@13.1.0
#:package Aspire.Hosting.JavaScript@13.1.0

var builder = DistributedApplication.CreateBuilder(args);

// Parameters can be overridden in apphost.run.json.
// NOTE: These paths are consumed by the `ai-processing` app, whose working directory is `./ai-processing`.
// So they must be relative to that directory (or be absolute paths).
var documentsPath = builder.AddParameter("documents-path", "../../PrismWeaveDocs/documents");
var chromaPersistDir = builder.AddParameter("chroma-persist-dir", "../../PrismWeaveDocs/.prismweave/chroma_db");
var articleIndexPath = builder.AddParameter(
    "article-index-path",
    "../../PrismWeaveDocs/documents/.prismweave/index/articles.json"
);
var ollamaHost = builder.AddParameter("ollama-host", "http://localhost:11434");

var aiProcessing = builder
    .AddUvicornApp("ai-processing", "./ai-processing", "src.unified_app:app")
    .WithUv()
    .WithHttpHealthCheck("/health")
    .WithEnvironment("PYTHONUNBUFFERED", "1")
    .WithEnvironment("LOG_LEVEL", "INFO")
    .WithEnvironment("OLLAMA_HOST", ollamaHost)
    .WithEnvironment("DOCUMENTS_PATH", documentsPath)
    .WithEnvironment("CHROMA_PERSIST_DIR", chromaPersistDir)
    .WithEnvironment("ARTICLE_INDEX_PATH", articleIndexPath);

var visualization = builder
    .AddViteApp("visualization", "./visualization")
    .WithNpm(installCommand: "ci", installArgs: ["--no-audit", "--no-fund"])
    .WithRunScript("dev")
    .WithExternalHttpEndpoints()
    .WithEnvironment("API_URL", aiProcessing.GetEndpoint("http"))
    .WithReference(aiProcessing)
    .WaitFor(aiProcessing);

var website = builder
    .AddNodeApp("website", "./website", "scripts/dev-server.mjs")
    .WithNpm(installCommand: "ci", installArgs: ["--no-audit", "--no-fund"])
    .WithArgs("--port", "3002")
    .WithExternalHttpEndpoints()
    .WithEnvironment("API_URL", aiProcessing.GetEndpoint("http"))
    .WithReference(aiProcessing)
    .WaitFor(aiProcessing);

builder.Build().Run();
