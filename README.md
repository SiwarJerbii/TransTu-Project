# TransTu-Project
TransTu Route Finder - A smart public transportation routing application for Greater Tunis.  Find optimal bus routes between any two locations using geocoding APIs and multi-modal pathfinding algorithms.  Built with Flask, Docker, and OpenStreetMap services.

**Course:** Web Services  
**Professor:** Dr. Montassar Ben Messaoud  
**Institution:** Tunis Business School (TBS)

## Features

- Multimodal route planning (Bus)
- GPS-based location detection
- Interactive map visualization
- Optimized route ranking by travel time
- Real-time distance calculations

## 🛠️ Tech Stack
- **Backend:** Flask (Python)
- **APIs:** Nominatim (Geocoding), OSRM (Routing)
- **Data:** JSON (Ministry of Transport data)
- **Container:** Docker
- **Testing:** Insomnia

## 📦 Installation

### Prerequisites
- Python 3.8+
- pip
- Git

### Setup

1. **Clone the repository**
```bash
   git clone <TransTu-Project>
   cd TransTu-Project
```

2. **Create virtual environment**
```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Mac/Linux
   source venv/bin/activate
```

3. **Install dependencies**
```bash
   pip install -r requirements.txt
```

4. **Configure environment**
```bash
   cp .env.example .env
   # Edit .env with your settings
```

5. **Run the application**
```bash
   python run.py
```
   API will be available at: `http://localhost:5000`

## Docker Setup
```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build manually
docker build -t transtu-api .
docker run -p 5000:5000 transtu-api
```

## API Endpoints

### Health Check
```http
GET /health
```
Check if the API is running and responding.

**Response:**
```json
{
  "status": "ok",
  "message": "TransTu API is running",
  "version": "1.0.0"
}
```

### Geocoding
```http
POST /api/geocode
Content-Type: application/json

{
  "address": "Avenue Habib Bourguiba, Tunis"
}
```
Convert address strings to geographic coordinates (latitude, longitude).

**Response:**
```json
{
  "success": true,
  "address": "Avenue Habib Bourguiba, Tunis",
  "latitude": 36.8065,
  "longitude": 10.1815
}
```

### Compute Routes
```http
POST /api/routes/direct
Content-Type: application/json

{
  "start": {
    "latitude": 36.8065,
    "longitude": 10.1815
  },
  "end": {
    "latitude": 36.7518,
    "longitude": 9.9800
  }
}
```
Find direct bus routes between two geographic locations without transfers.

**Response:**
```json
{
  "success": true,
  "start_location": {
    "latitude": 36.8065,
    "longitude": 10.1815
  },
  "end_location": {
    "latitude": 36.7518,
    "longitude": 9.9800
  },
  "routes_found": 2,
  "routes": [...],
  "valid_routes_only": [...]
}
```

**Error Handling:**
- Returns 400 if coordinates are null/None
- Returns 400 if coordinates are invalid format or out of range
- Returns 200 with empty routes if no direct routes found

## Project Structure
```
TransTu-Project/
├── app/
│   ├── routes/
│   │   ├── health.py          # Health check endpoint
│   │   ├── geocoding.py        # Geocoding API endpoint
│   │   └── routing.py          # Direct route finding endpoint
│   ├── services/
│   │   ├── geocoding_service.py    # Address to coordinates
│   │   ├── routing_service.py      # Route finding logic
│   │   └── distance_service.py     # Distance calculations
│   ├── models/
│   ├── utils/
│   │   └── data_loader.py     # Bus routes data loader
│   ├── templates/             # HTML templates
│   │   └── index.html
│   ├── static/                # Static files (CSS, JS, images)
│   └── __init__.py            # App factory
├── data/
│   └── bus_routes.json        # Transit data (406 bus routes)
├── tests/
│   └── test_routing.py        # Route finding tests
├── config.py                  # Configuration settings
├── run.py                     # Application entry point
├── requirements.txt
├── Dockerfile
└── docker-compose.yml

```

## 📈 Data Pipeline
1. **Source:** Ministry of Transport Excel files
2. **Processing:** Python ETL pipeline (Pandas)
3. **Output:** Hierarchical JSON format
4. **Coverage:** 219 bus lines, 1,608 unique stops

## 🤝 Contributing

This is an academic project for Web Services course.

## 📄 License

Academic project - Tunis Business School

## 👤 Author

Siwar Jerbi
Web Services Course - TBS  
Supervised by: Dr. Montassar Ben Messaoud