# TransTu Route Finder - Setup Guide

## Project Overview

TransTu is a smart public transportation routing application for Greater Tunis that finds optimal bus routes between two locations using geocoding APIs and multi-modal pathfinding algorithms. Built with Flask and Docker, it provides both direct routes and transfer routes with an interactive map interface powered by Leaflet.js.

---

## Prerequisites

### Required Software
- **Python** 3.8 or higher
- **Git** for version control
- **pip** (comes with Python)
- **Docker** and **Docker Compose** (optional, for containerized deployment)

### Recommended Tools & Extensions
- **Visual Studio Code** with the following extensions:
  - Python (by Microsoft)
  - GitHub Copilot (for AI-assisted development)
  - REST Client (for testing API endpoints)
  - Live Server (for testing static files)
- **Postman** or **Insomnia** for API testing
- **Node.js** (optional, if you want to use npm-based tools)

### Recommended Operating System
- Windows 10/11
- macOS 10.14+
- Linux (Ubuntu 18.04+)

---

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/SiwarJerbii/TransTu-Project.git
cd TransTu-Project
```

### 2. Create a Virtual Environment

#### Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

#### macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs all required packages:
- Flask (web framework)
- Requests (HTTP library)
- Pandas (data processing)
- Python-dotenv (environment variables)

---

## Configuration

### Environment Variables

Create a `.env` file in the project root directory with the following settings:

```env
FLASK_ENV=development
FLASK_DEBUG=True
API_HOST=0.0.0.0
API_PORT=5000
NOMINATIM_USER_AGENT=TransTuRouteApp/1.0
MAX_WALKING_DISTANCE=500
WALKING_SPEED=80
```

**Configuration Details:**
- `FLASK_ENV`: Set to `production` for production deployment
- `FLASK_DEBUG`: Enable auto-reload during development
- `API_HOST`: Server binding address
- `API_PORT`: Server port (default 5000)
- `NOMINATIM_USER_AGENT`: User agent for Nominatim geocoding API
- `MAX_WALKING_DISTANCE`: Maximum walking distance between stops (meters)
- `WALKING_SPEED`: Walking speed assumption (meters per minute)

### Optional: Create `.env.example`

```bash
cp .env.example .env
```

Then edit `.env` with your specific settings.

---

## Running the Project

### Local Development

```bash
python run.py
```

The application will start at `http://localhost:5000`

### Using Docker Compose

```bash
docker-compose up --build
```

This will:
- Build the Docker image
- Start the container
- Expose the app on `http://localhost:5000`

### Using Docker (Manual)

```bash
docker build -t transtu-api .
docker run -p 5000:5000 transtu-api
```

### Production Deployment with Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

---

## Testing the API

### Using cURL

**Health Check:**
```bash
curl http://localhost:5000/health
```

**Geocode an Address:**
```bash
curl -X POST http://localhost:5000/api/geocode \
  -H "Content-Type: application/json" \
  -d '{"address": "Avenue Habib Bourguiba, Tunis"}'
```

**Find Direct Routes:**
```bash
curl -X POST http://localhost:5000/api/routes/direct \
  -H "Content-Type: application/json" \
  -d '{
    "start": {"latitude": 36.8065, "longitude": 10.1815},
    "end": {"latitude": 36.7518, "longitude": 9.9800}
  }'
```

**Find Transfer Routes:**
```bash
curl -X POST http://localhost:5000/api/routes/transfer \
  -H "Content-Type: application/json" \
  -d '{
    "start": {"latitude": 36.5528, "longitude": 9.9026},
    "end": {"latitude": 36.8008, "longitude": 10.1865},
    "max_results": 5
  }'
```

### Using REST Client (VS Code)

Create a file named `test.http` and use the REST Client extension to test endpoints interactively.

---

## Project Structure

```
TransTu-Project/
├── app/
│   ├── routes/              # API endpoint handlers
│   ├── services/            # Business logic
│   ├── utils/               # Helper functions
│   ├── templates/           # HTML templates
│   ├── static/              # CSS, JS, images
│   └── __init__.py
├── data/
│   └── bus_routes.json      # Bus route data
├── tests/                   # Test files
├── config.py                # Configuration
├── run.py                   # Application entry point
├── requirements.txt         # Python dependencies
├── Dockerfile               # Docker configuration
├── docker-compose.yml       # Docker Compose configuration
└── README.md                # Project documentation
```

---

## Using GitHub Copilot in Development

### GitHub Copilot Integration

GitHub Copilot enhances the development workflow for this project:

#### Key Features:
- **Code Completion**: Copilot suggests complete functions and API handlers
- **Documentation**: Automatically generates docstrings for functions
- **Debugging**: Helps identify issues and suggest fixes
- **Testing**: Assists in writing unit tests for services

#### Tips for Using Copilot:
1. **When working on services**: Start typing a function name and let Copilot complete the implementation
2. **For API routes**: Describe the route handler in comments, then let Copilot generate the endpoint
3. **Testing**: Write test descriptions in comments and Copilot will generate test cases
4. **Refactoring**: Ask Copilot to improve code quality or simplify complex functions

#### Example Usage:
```python
# Type a comment describing what you want
# def calculate_route_time(start_stop, end_stop, walking_distance):
# Copilot will suggest the implementation
```

#### Productivity Shortcuts:
- Press `Ctrl+Shift+A` (or `Cmd+Shift+A` on Mac) to open Copilot chat
- Use inline suggestions with `Tab` to accept completions
- Press `Alt+\` to trigger inline Copilot suggestions

---

## Troubleshooting

### Common Issues

**Issue**: Port 5000 already in use
```bash
# Kill process on port 5000
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:5000 | xargs kill -9
```

**Issue**: Virtual environment not activating
- Ensure you're in the project root directory
- Check that the venv folder exists
- Try deleting venv and creating a new one

**Issue**: Dependencies not installing
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

**Issue**: API returning empty results
- Check that coordinates are within Greater Tunis bounds (lat: 36.4-37.1, lon: 9.5-10.6)
- Verify bus_routes.json data file exists in the `data/` folder
- Check MAX_WALKING_DISTANCE configuration

---

## Next Steps

1. Read the [README.md](README.md) for detailed feature documentation
2. Explore the API endpoints using the REST Client
3. Check out the `tests/` folder for example queries
4. Review `app/services/` for understanding the route-finding logic

---

## Support & Resources

- **GitHub Issues**: Report bugs or request features
- **Documentation**: See README.md for comprehensive API documentation
- **API Tests**: Check `tests/` directory for working examples
- **Nominatim API Docs**: https://nominatim.org/

---

**Last Updated**: January 17, 2026  
**Project Repository**: https://github.com/SiwarJerbii/TransTu-Project
