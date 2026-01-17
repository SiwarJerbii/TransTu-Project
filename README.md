# TransTu Route Finder

A smart public transportation routing application for Greater Tunis. Find optimal bus routes between any two locations using geocoding APIs and multi-modal pathfinding algorithms. Built with Flask, Docker, and OpenStreetMap services.

**Course:** Web Services  
**Professor:** Dr. Montassar Ben Messaoud  
**Institution:** Tunis Business School (TBS)

---

## Features

TransTu offers direct route finding for buses without transfers, multi-stop routes with one transfer, and interactive map visualization powered by Leaflet. The app converts addresses to coordinates using Nominatim, ranks routes by travel time, transfers, or walking distance, and calculates real-time distances using the Haversine formula. It includes a responsive interface for desktop and mobile, a complete RESTful API, and comprehensive error handling.

---

## Tech Stack

The frontend uses HTML5, CSS3, and vanilla JavaScript. The backend runs on Flask with Python 3.8+. Maps are rendered with Leaflet.js and OpenStreetMap tiles, while geocoding relies on the Nominatim API. Data is stored in JSON format, and the application is containerized with Docker and Docker Compose. Testing uses Python's unittest framework.

---

## Installation

### Prerequisites

You'll need Python 3.8+, pip, and Git installed.

### Setup

Clone the repository and navigate into the project directory:

```bash
git clone <TransTu-Project>
cd TransTu-Project
```

Create and activate a virtual environment:

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure the environment:

```bash
cp .env.example .env
# Edit .env with your settings
```

Run the application:

```bash
python run.py
```

The application will be available at `http://localhost:5000`.

### Docker Setup

Build and run with Docker Compose:

```bash
docker-compose up --build
```

Or build and run manually:

```bash
docker build -t transtu-api .
docker run -p 5000:5000 transtu-api
```

---

## API Endpoints

### Health Check

```http
GET /health
```

Returns the API status, message, and version.

### Geocoding

```http
POST /api/geocode
Content-Type: application/json

{
  "address": "Avenue Habib Bourguiba, Tunis"
}
```

Accepts an address string and returns latitude/longitude coordinates.

### Direct Routes

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

Returns bus routes without transfers between two locations.

### Transfer Routes

```http
POST /api/routes/transfer
Content-Type: application/json

{
  "start": {
    "latitude": 36.8065,
    "longitude": 10.1815
  },
  "end": {
    "latitude": 36.7518,
    "longitude": 9.9800
  },
  "max_results": 10
}
```

Finds routes requiring one transfer between buses.

All endpoints return 400 for null, invalid, or out-of-range coordinates, and 200 with empty results when no routes are found.

---

## Project Structure

```
TransTu-Project/
├── app/
│   ├── routes/
│   │   ├── health.py
│   │   ├── geocoding.py
│   │   └── routing.py
│   ├── services/
│   │   ├── geocoding_service.py
│   │   ├── routing_service.py
│   │   ├── transfer_routing_service.py
│   │   └── distance_service.py
│   ├── models/
│   ├── utils/
│   │   └── data_loader.py
│   ├── templates/
│   │   └── index.html
│   ├── static/
│   └── __init__.py
├── data/
│   └── bus_routes.json
├── tests/
│   ├── debug_transfer.py
│   ├── find_working_test_route.py
│   └── test_transfer_routing.py
├── config.py
├── run.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## Data Pipeline

Data originates from Ministry of Transport Excel files, processed through a Python ETL pipeline using Pandas, and output as hierarchical JSON. The dataset covers 219 bus lines, 1,608 unique stops, and 406 total routes.

---

## How It Works

The route-finding algorithm begins with user input (address or GPS coordinates), geocodes addresses via Nominatim, then searches for either direct routes or transfer routes with intermediate transfer points. It validates coordinate ranges and data integrity, ranks results by the chosen criteria, and displays routes on an interactive map with turn-by-turn directions.

Distance calculations use the Haversine formula for walking distance, assume 80 meters per minute walking speed, estimate 3 minutes per bus stop, and cap walking distance at 500 meters between stops and destinations.

---

## Testing

### Manual Testing

```bash
# Test direct routes
curl -X POST http://localhost:5000/api/routes/direct \
  -H "Content-Type: application/json" \
  -d '{
    "start": {"latitude": 36.8065, "longitude": 10.1815},
    "end": {"latitude": 36.7518, "longitude": 9.9800}
  }'

# Test transfer routes
curl -X POST http://localhost:5000/api/routes/transfer \
  -H "Content-Type: application/json" \
  -d '{
    "start": {"latitude": 36.5528, "longitude": 9.9026},
    "end": {"latitude": 36.8008, "longitude": 10.1865},
    "max_results": 5
  }'

# Test geocoding
curl -X POST http://localhost:5000/api/geocode \
  -H "Content-Type: application/json" \
  -d '{"address": "Avenue Habib Bourguiba, Tunis"}'
```

### Automated Tests

```bash
python -m pytest tests/

# Run specific test
python tests/test_transfer_routing.py
```

---

## Deployment

### Production Setup

Install Gunicorn and run with multiple workers:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:create_app()
```

### Docker Deployment

```bash
docker build -t transtu-api:latest .
docker run -p 5000:5000 transtu-api:latest

# Or use Docker Compose
docker-compose up -d
```

---

## Configuration

Create a `.env` file with the following variables:

```
FLASK_ENV=development
FLASK_DEBUG=True
API_HOST=0.0.0.0
API_PORT=5000
NOMINATIM_USER_AGENT=TransTuRouteApp/1.0
MAX_WALKING_DISTANCE=500
WALKING_SPEED=80
```

---

## Project Status

All core features are complete: direct and transfer route finding, web UI with map, REST API endpoints, error handling, documentation, Docker support, and testing utilities.

---

## Future Enhancements

Potential additions include metro and light rail support, real-time bus tracking, accessibility features, multi-language support, mobile apps, advanced search filters, and user preferences with bookmarks.

---

## License

Academic project — Tunis Business School

---

**Author:** Siwar Jerbi  
**Supervisor:** Dr. Montassar Ben Messaoud  
Web Services Course — Tunis Business School