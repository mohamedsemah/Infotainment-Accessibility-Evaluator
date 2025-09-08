from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
import os
from contextlib import asynccontextmanager

from routers import upload, analyze, plan, run, cluster, patch, report, progress, recheck
from services.llm.provider_base import LLMProvider
from services.llm.openai_provider import OpenAIProvider
from services.llm.anthropic_provider import AnthropicProvider
from services.llm.deepseek_provider import DeepSeekProvider
from utils.config import get_settings

settings = get_settings()

# Global LLM provider instance
llm_provider: LLMProvider = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global llm_provider
    
    # Startup
    print("Starting Infotainment Accessibility Evaluator...")
    
    # Database layer removed - using in-memory storage
    print("Using in-memory storage")
    
    # Initialize LLM provider
    if settings.LLM_PROVIDER != "none":
        if settings.LLM_PROVIDER == "openai":
            llm_provider = OpenAIProvider(
                api_key=settings.OPENAI_API_KEY,
                model=settings.OPENAI_MODEL
            )
        elif settings.LLM_PROVIDER == "anthropic":
            llm_provider = AnthropicProvider(
                api_key=settings.ANTHROPIC_API_KEY,
                model=settings.ANTHROPIC_MODEL
            )
        elif settings.LLM_PROVIDER == "deepseek":
            llm_provider = DeepSeekProvider(
                api_key=settings.DEEPSEEK_API_KEY,
                model=settings.DEEPSEEK_MODEL
            )
    
    print(f"LLM Provider: {settings.LLM_PROVIDER}")
    print("Application started successfully!")
    
    yield
    
    # Shutdown
    print("Shutting down application...")

# Create FastAPI application
app = FastAPI(
    title="Infotainment Accessibility Evaluator",
    description="A comprehensive multi-agent accessibility evaluation system for infotainment UIs",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "0.0.0.0"]
)

# Mount static files
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(analyze.router, prefix="/api", tags=["analyze"])
app.include_router(plan.router, prefix="/api", tags=["plan"])
app.include_router(run.router, prefix="/api", tags=["run"])
app.include_router(cluster.router, prefix="/api", tags=["cluster"])
app.include_router(patch.router, prefix="/api", tags=["patch"])
app.include_router(report.router, prefix="/api", tags=["report"])
app.include_router(progress.router, prefix="/api", tags=["progress"])
app.include_router(recheck.router, prefix="/api", tags=["recheck"])

@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with basic information"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Infotainment Accessibility Evaluator</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 800px; margin: 0 auto; }
            .header { text-align: center; margin-bottom: 40px; }
            .endpoints { background: #f5f5f5; padding: 20px; border-radius: 8px; }
            .endpoint { margin: 10px 0; }
            .method { display: inline-block; width: 80px; font-weight: bold; }
            .get { color: #28a745; }
            .post { color: #007bff; }
            .ws { color: #6f42c1; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚗 Infotainment Accessibility Evaluator</h1>
                <p>A comprehensive multi-agent accessibility evaluation system for infotainment UIs</p>
            </div>
            
            <div class="endpoints">
                <h2>API Endpoints</h2>
                <div class="endpoint">
                    <span class="method post">POST</span> /api/upload - Upload ZIP file
                </div>
                <div class="endpoint">
                    <span class="method get">GET</span> /api/analyze - Pre-scan analysis
                </div>
                <div class="endpoint">
                    <span class="method post">POST</span> /api/plan - Generate execution plan
                </div>
                <div class="endpoint">
                    <span class="method post">POST</span> /api/run - Execute agents
                </div>
                <div class="endpoint">
                    <span class="method post">POST</span> /api/cluster - Cluster findings
                </div>
                <div class="endpoint">
                    <span class="method post">POST</span> /api/patch - Generate patches
                </div>
                <div class="endpoint">
                    <span class="method get">GET</span> /api/report - Generate reports
                </div>
                <div class="endpoint">
                    <span class="method ws">WS</span> /api/progress - Real-time progress
                </div>
            </div>
            
            <p style="text-align: center; margin-top: 40px;">
                <a href="/docs">📚 API Documentation</a> | 
                <a href="/redoc">📖 ReDoc</a>
            </p>
        </div>
    </body>
    </html>
    """

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "llm_provider": settings.LLM_PROVIDER,
        "environment": settings.ENVIRONMENT
    }

@app.get("/api/status")
async def api_status():
    """API status endpoint"""
    return {
        "api_version": "1.0.0",
        "status": "operational",
        "features": {
            "upload": True,
            "analysis": True,
            "agents": True,
            "clustering": True,
            "patching": True,
            "sandbox": settings.ENABLE_SANDBOX,
            "llm": settings.LLM_PROVIDER != "none"
        },
        "limits": {
            "max_file_size": settings.MAX_FILE_SIZE,
            "max_concurrent_agents": settings.MAX_CONCURRENT_AGENTS,
            "analysis_timeout": settings.ANALYSIS_TIMEOUT
        }
    }

def get_llm_provider() -> LLMProvider:
    """Get the global LLM provider instance"""
    return llm_provider

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=settings.BACKEND_RELOAD,
        workers=settings.BACKEND_WORKERS
    )