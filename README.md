# Infotainment Accessibility Evaluator

A comprehensive, multi-agent accessibility evaluation system for infotainment UIs that automatically detects WCAG 2.2 compliance issues and provides automated fixes.

## Features

- **Multi-Agent Analysis**: Specialized agents for contrast, seizure safety, ARIA, language, and more
- **Automated Patching**: Generate and apply fixes automatically in a sandbox environment
- **WCAG 2.2 Compliance**: Full support for the latest accessibility guidelines
- **Real-time Progress**: Live updates during analysis with WebSocket support
- **Multiple Export Formats**: HTML, PDF, CSV, and JSON reports
- **Interactive UI**: Modern React frontend with TailwindCSS
- **Docker Support**: Easy deployment with Docker Compose

## Quick Start

### Prerequisites

- Node.js 18+ and npm
- Python 3.11+
- Docker and Docker Compose (optional)

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd infotainment-a11y-evaluator
   ```

2. **Set up the backend**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Set up the frontend**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Docker Deployment

1. **Copy environment file**
   ```bash
   cp env.example .env
   ```

2. **Start all services**
   ```bash
   docker-compose up -d
   ```

3. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000

## Architecture

### Backend (FastAPI)

- **Main Application**: `backend/main.py`
- **Routers**: API endpoints in `backend/routers/`
- **Services**: Core business logic in `backend/services/`
- **Models**: Pydantic schemas in `backend/models/`
- **Utils**: Utility functions in `backend/utils/`

### Frontend (React + Vite)

- **Pages**: Main application pages in `frontend/src/pages/`
- **Components**: Reusable UI components in `frontend/src/components/`
- **Store**: Zustand state management in `frontend/src/store/`
- **API**: API client in `frontend/src/api/`

### Special Agents

1. **ContrastAgent**: Color contrast analysis
2. **SeizureSafeAgent**: Flashing content detection
3. **LanguageAgent**: Language attribute validation
4. **ARIAAgent**: ARIA role and attribute checking
5. **StateExplorerAgent**: UI state exploration
6. **TriageAgent**: Finding normalization and scoring
7. **TokenHarmonizerAgent**: Design token recommendations

## API Endpoints

### Upload & Analysis
- `POST /api/upload` - Upload ZIP file
- `GET /api/analyze` - Pre-scan analysis
- `POST /api/plan` - Generate execution plan
- `POST /api/run` - Execute agents

### Results & Clustering
- `POST /api/cluster` - Cluster findings
- `GET /api/results` - Get analysis results

### Patching & Sandbox
- `POST /api/patch` - Generate patches
- `POST /api/apply` - Apply patches
- `POST /api/recheck` - Recheck in sandbox

### Reports
- `GET /api/report` - Generate reports (HTML, PDF, CSV, JSON)

### Progress
- `WS /api/progress` - Real-time progress updates

## Configuration

### Environment Variables

See `env.example` for all available configuration options.

### Key Settings

- `LLM_PROVIDER`: Enable LLM integration (none, openai, anthropic, deepseek)
- `MAX_FILE_SIZE`: Maximum upload size (default: 50MB)
- `MAX_CONCURRENT_AGENTS`: Parallel agent execution limit
- `ENABLE_SANDBOX`: Enable patch testing environment

## Usage

### 1. Upload Your Code

Upload a ZIP file containing your infotainment UI code (HTML, QML, XML, CSS, JS, images).

### 2. Analysis Process

The system automatically:
1. Extracts and indexes your code
2. Runs pre-scan analysis
3. Generates an execution plan
4. Executes specialized agents
5. Clusters findings by root cause

### 3. Review Results

- View clustered findings with severity levels
- Filter by agent, confidence, or status
- Examine individual findings with evidence
- View suggested fixes and patches

### 4. Apply Fixes

- Review generated patches
- Apply fixes in sandbox environment
- Re-run analysis to verify fixes
- Export fixed code

### 5. Generate Reports

Export comprehensive reports in multiple formats:
- **HTML**: Interactive web report
- **PDF**: Print-ready document
- **CSV**: Data analysis format
- **JSON**: Machine-readable format

## Development

### Backend Development

```bash
cd backend
pip install -r requirements.txt
pytest  # Run tests
ruff check .  # Lint code
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev  # Start dev server
npm run build  # Build for production
npm run test  # Run tests
npm run lint  # Lint code
```

### Adding New Agents

1. Create agent class in `backend/services/agents/special/`
2. Implement required methods
3. Register in `backend/services/agents/super_agent.py`
4. Add to agent options in frontend

## Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Integration Tests
```bash
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions and support:
- Create an issue on GitHub
- Check the documentation at `/docs`
- Review the API documentation at `/api/docs`

## Roadmap

- [ ] Additional WCAG 2.2 criteria support
- [ ] Machine learning-based issue detection
- [ ] Integration with popular design tools
- [ ] CI/CD pipeline integration
- [ ] Advanced reporting features
- [ ] Multi-language support
