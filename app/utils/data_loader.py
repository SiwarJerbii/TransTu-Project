"""
Data Loader - Load and cache bus route data
"""
import json
from pathlib import Path
from typing import Dict, List, Optional

class DataLoader:
    """Singleton class to load and cache bus route data"""
    
    _instance = None
    _bus_data = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataLoader, cls).__new__(cls)
        return cls._instance
    
    def load_bus_data(self, file_path: str = None) -> Dict:
        """
        Load bus routes from JSON file (cached after first load)
        
        Args:
            file_path: Path to bus_routes.json (optional)
        
        Returns:
            Dict containing all bus route data
        """
        if self._bus_data is not None:
            return self._bus_data
        
        if file_path is None:
            # Default path relative to project root
            base_dir = Path(__file__).resolve().parent.parent.parent
            file_path = base_dir / 'data' / 'bus_routes.json'
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self._bus_data = json.load(f)
            
            print(f"✅ Loaded {len(self._bus_data['routes'])} bus routes")
            return self._bus_data
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Bus data file not found: {file_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in bus data file: {e}")
    
    def get_route_by_id(self, route_id: str) -> Optional[Dict]:
        """Get a specific route by ID"""
        if self._bus_data is None:
            self.load_bus_data()
        
        for route in self._bus_data['routes']:
            if route['id'] == route_id:
                return route
        return None
    
    def get_all_routes(self) -> List[Dict]:
        """Get all routes"""
        if self._bus_data is None:
            self.load_bus_data()
        return self._bus_data['routes']


# Create singleton instance
data_loader = DataLoader()