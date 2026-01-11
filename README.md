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

### Geocoding
```http
POST /api/geocode
Content-Type: application/json

{
  "address": "Avenue Habib Bourguiba, Tunis"
}
```

### Find Nearest Stops
```http
POST /api/stops/nearest
Content-Type: application/json

{
  "latitude": 36.8065,
  "longitude": 10.1815,
  "max_distance": 500
}
```

### Compute Routes
```http
POST /api/routes/compute
Content-Type: application/json

{
  "from": "Avenue Habib Bourguiba, Tunis",
  "to": "Carthage, Tunisia"
}
```

## Project Structure
TransTu-Project/
├── app/                # Application code
│   ├── routes/        # API endpoints
│   ├── services/      # Business logic
│   ├── models/        # Data models
│   └── utils/         # Helper functions
├── data/              # Transit data (JSON)
├── scripts/           # Data processing scripts
├── tests/             # Unit tests
└── docs/              # Documentation

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