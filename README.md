# Infotainment Accessibility Evaluator

A production-ready web tool that analyzes infotainment UI code for WCAG 2.2 compliance using a sophisticated 4-stage LLM pipeline.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   LLM-1         │    │   LLM-2         │    │   LLM-3         │    │   LLM-4         │
│   Discovery     │───▶│   Metrics       │───▶│   Validation    │───▶│   Fixes         │
│   Claude Opus   │    │   DeepSeek V3   │    │   Grok-4        │    │   GPT-5         │
│   4.1           │    │                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │                       │
         ▼                       ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           React Frontend (Vite + Tailwind + shadcn/ui)             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                │
│  │ Discovery   │  │ Metrics     │  │ Validation  │  │ Fixes       │                │
│  │ Results     │  │ Results     │  │ Results     │  │ Results     │                │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘                │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for development)
- Python 3.9+ (for development)

### 1. Clone and Setup

```bash
git clone <repository-url>
cd infotainment-accessibility-evaluator
make setup
```

### 2. Configure API Keys

Edit `.env` file and add your API keys:

```bash
# LLM API Keys
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
DEEPSEEK_API_KEY=your_deepseek_key_here
XAI_API_KEY=your_xai_key_here

# Development Mode (set to true to use mocked responses)
MOCK_MODE=false
```

### 3. Run the Application

#### Development Mode
```bash
make dev
```

#### Docker Mode
```bash
make up
```

The application will be available at:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000

## 📋 Usage

### 1. Upload Files
- Drag and drop your infotainment UI files (HTML, CSS, JS, TS, QML, XML)
- Supported formats: HTML, CSS, JavaScript, TypeScript, JSX, TSX, QML, XML

### 2. Run Analysis
- Click "Run Premium Pipeline" to execute the 4-stage analysis
- Monitor progress through the stepper interface

### 3. Review Results
- **Discovery Tab**: View discovered accessibility issues
- **Metrics Tab**: See computed WCAG measurements
- **Validation Tab**: Review pass/fail decisions with reasoning
- **Fixes Tab**: Examine fix suggestions with unified diff patches

### 4. Export Reports
- Download PDF reports with comprehensive findings
- Export ZIP archives with patched files

## 🔧 API Examples

### Run Pipeline
```bash
curl -X POST http://localhost:8000/pipeline/run \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-session-123",
    "model_map": {
      "llm1": "claude-opus-4-1-20250805",
      "llm2": "deepseek-chat", 
      "llm3": "grok-4",
      "llm4": "gpt-5"
    },
    "files": [
      {
        "path": "index.html",
        "content": "<html><body><img src=\"test.jpg\"></body></html>"
      }
    ]
  }'
```

### Health Check
```bash
curl http://localhost:8000/healthz
```

## 🧪 Testing

### Run All Tests
```bash
make test
```

### Run Specific Test Suites
```bash
# Backend tests
cd backend && python -m pytest app/tests/ -v

# Frontend tests (if available)
cd frontend && npm test
```

### Test with Sample Files
The project includes sample UI files in `backend/app/tests/fixtures/sample_ui/` that demonstrate common accessibility issues:

- **Missing alt text** (WCAG 1.1.1)
- **Insufficient contrast** (WCAG 1.4.3) 
- **Small touch targets** (WCAG 2.5.5)

## 🏗️ Development

### Project Structure
```
infotainment-accessibility-evaluator/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── models.py            # Pydantic models
│   │   ├── orchestrator.py      # 4-stage pipeline orchestrator
│   │   ├── providers/           # LLM client implementations
│   │   ├── utils/               # Deterministic utilities
│   │   ├── config/              # WCAG thresholds and model configs
│   │   └── tests/               # Test suites
│   └── pyproject.toml           # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── pages/               # Page components
│   │   ├── api/                 # API client
│   │   └── styles/              # Tailwind CSS
│   └── package.json             # Node.js dependencies
├── docker-compose.yml           # Container orchestration
├── Makefile                     # Development commands
└── README.md                    # This file
```

### Key Components

#### Backend
- **Orchestrator**: Coordinates the 4-stage pipeline
- **Providers**: LLM client implementations with retry logic
- **Utils**: Deterministic calculations (contrast, target sizes)
- **Models**: Strict Pydantic schemas for type safety

#### Frontend
- **Upload Page**: Drag-and-drop file interface
- **Results Page**: 4-tab results viewer with stepper
- **Components**: Reusable UI components with shadcn/ui
- **API Client**: Axios-based HTTP client with error handling

## 🔒 Security & Safety

### JSON-Only Responses
All LLM calls enforce JSON-only responses with retry logic for parse failures.

### Low Temperature Settings
- LLM-1 (Claude): temperature=0.1
- LLM-2 (DeepSeek): temperature=0.0  
- LLM-3 (Grok-4): temperature=0.0
- LLM-4 (GPT-5): temperature=0.2

### Deterministic Fallbacks
Critical calculations (contrast ratios, target sizes) are computed deterministically when possible, with LLM fallback only for complex cases.

### Mock Mode
Set `MOCK_MODE=true` in `.env` to run without API keys using simulated responses.

## 📊 WCAG 2.2 Rules Supported

| Rule ID | Description | Metric | Threshold |
|---------|-------------|--------|-----------|
| 1.1.1 | Non-text content | alt_text_present | true |
| 1.3.1 | Programmatic structure | programmatic_structure | true |
| 1.4.3 | Contrast (minimum) | contrast_ratio | 4.5 (normal), 3.0 (large) |
| 1.4.6 | Contrast (enhanced) | contrast_ratio | 7.0 (normal), 4.5 (large) |
| 2.1.1 | Keyboard accessible | keyboard_accessible | true |
| 2.4.7 | Focus indicator | focus_indicator_visibility | true |
| 2.5.5 | Target size | target_size_min_px | 44px |
| 3.1.1 | Language identified | language_identified | true |
| 4.1.2 | Name, role, value | name_role_value | true |

## 🚀 Deployment

### Production Docker
```bash
make deploy
```

### Environment Variables
```bash
# Required for production
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
DEEPSEEK_API_KEY=your_key
XAI_API_KEY=your_key

# Optional
APP_HOST=0.0.0.0
APP_PORT=8000
LOG_LEVEL=INFO
MOCK_MODE=false
```

## 🐛 Troubleshooting

### Common Issues

1. **API Key Errors**: Ensure all required API keys are set in `.env`
2. **Port Conflicts**: Change ports in `docker-compose.yml` if needed
3. **Memory Issues**: Increase Docker memory limits for large files
4. **Network Issues**: Check firewall settings for API access

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
make dev
```

### Health Checks
```bash
make health
```

## 📈 Performance

### Benchmarks
- **Small files** (< 1KB): ~2-5 seconds
- **Medium files** (1-10KB): ~5-15 seconds  
- **Large files** (10-100KB): ~15-60 seconds

### Optimization Tips
- Use mock mode for development
- Chunk large files automatically
- Cache results for repeated analysis
- Use deterministic calculations when possible

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite: `make test`
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- WCAG 2.2 guidelines from W3C
- LLM providers: OpenAI, Anthropic, DeepSeek, XAI
- UI components from shadcn/ui
- Icons from Lucide React

---

**Quick Start Commands:**
```bash
# Development
make dev

# Docker
make up

# Testing
make test

# Sample curl request
curl -X POST http://localhost:8000/pipeline/run \
  -H "Content-Type: application/json" \
  -d '{"session_id":"test","model_map":{"llm1":"claude-opus-4-1-20250805","llm2":"deepseek-chat","llm3":"grok-4","llm4":"gpt-5"},"files":[{"path":"test.html","content":"<img src=\"test.jpg\">"}]}'

# Toggle mock mode
echo "MOCK_MODE=true" >> .env
```
