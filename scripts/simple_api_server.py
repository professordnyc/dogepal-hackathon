"""Simple HTTP server to serve spending and recommendation data from SQLite."""
import json
import sqlite3
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from datetime import datetime, date

# Database path
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dogepal.db')

class JSONEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle dates and other special types."""
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)

def dict_factory(cursor, row):
    """Convert SQLite row to dictionary."""
    d = {}
    for idx, col in enumerate(cursor.description):
        value = row[idx]
        # Handle JSON fields
        if col[0] == 'metadata' and value:
            try:
                d[col[0]] = json.loads(value)
            except:
                d[col[0]] = value
        else:
            d[col[0]] = value
    return d

class SimpleAPIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for simple API."""
    
    def _set_headers(self, status_code=200, content_type='application/json'):
        """Set response headers."""
        self.send_response(status_code)
        self.send_header('Content-Type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')  # Enable CORS
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS preflight."""
        self._set_headers()
    
    def do_GET(self):
        """Handle GET requests."""
        try:
            # Parse URL and query parameters
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            query_params = parse_qs(parsed_url.query)
            
            # Connect to database
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = dict_factory
            cursor = conn.cursor()
            
            # Handle different endpoints
            if path == '/api/v1/spending':
                # Get spending data with optional filters
                limit = int(query_params.get('limit', ['100'])[0])
                skip = int(query_params.get('skip', ['0'])[0])
                
                query = "SELECT * FROM spending"
                
                # Add filters if provided
                conditions = []
                params = []
                
                if 'category' in query_params:
                    conditions.append("category = ?")
                    params.append(query_params['category'][0])
                
                if 'department' in query_params:
                    conditions.append("department = ?")
                    params.append(query_params['department'][0])
                
                if 'min_amount' in query_params:
                    conditions.append("amount >= ?")
                    params.append(float(query_params['min_amount'][0]))
                
                if 'max_amount' in query_params:
                    conditions.append("amount <= ?")
                    params.append(float(query_params['max_amount'][0]))
                
                if conditions:
                    query += " WHERE " + " AND ".join(conditions)
                
                # Add pagination
                query += f" ORDER BY spending_date DESC LIMIT {limit} OFFSET {skip}"
                
                cursor.execute(query, params)
                data = cursor.fetchall()
                
                # Send response
                self._set_headers()
                self.wfile.write(json.dumps(data, cls=JSONEncoder).encode())
            
            elif path.startswith('/api/v1/spending/'):
                # Get specific spending record by ID
                spending_id = path.split('/')[-1]
                cursor.execute("SELECT * FROM spending WHERE transaction_id = ?", (spending_id,))
                data = cursor.fetchone()
                
                if data:
                    self._set_headers()
                    self.wfile.write(json.dumps(data, cls=JSONEncoder).encode())
                else:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({"detail": "Spending record not found"}).encode())
            
            elif path == '/api/v1/recommendations':
                # Get recommendations with optional filters
                limit = int(query_params.get('limit', ['100'])[0])
                skip = int(query_params.get('skip', ['0'])[0])
                
                query = "SELECT * FROM recommendation"
                
                # Add filters if provided
                conditions = []
                params = []
                
                if 'transaction_id' in query_params:
                    conditions.append("transaction_id = ?")
                    params.append(query_params['transaction_id'][0])
                
                if 'recommendation_type' in query_params:
                    conditions.append("recommendation_type = ?")
                    params.append(query_params['recommendation_type'][0])
                
                if conditions:
                    query += " WHERE " + " AND ".join(conditions)
                
                # Add pagination
                query += f" ORDER BY created_at DESC LIMIT {limit} OFFSET {skip}"
                
                cursor.execute(query, params)
                data = cursor.fetchall()
                
                # Send response
                self._set_headers()
                self.wfile.write(json.dumps(data, cls=JSONEncoder).encode())
            
            elif path.startswith('/api/v1/recommendations/'):
                # Get specific recommendation by ID
                rec_id = path.split('/')[-1]
                cursor.execute("SELECT * FROM recommendation WHERE id = ?", (rec_id,))
                data = cursor.fetchone()
                
                if data:
                    self._set_headers()
                    self.wfile.write(json.dumps(data, cls=JSONEncoder).encode())
                else:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({"detail": "Recommendation not found"}).encode())
            
            else:
                # Unknown endpoint
                self._set_headers(404)
                self.wfile.write(json.dumps({"detail": "Endpoint not found"}).encode())
            
            # Close database connection
            conn.close()
        
        except Exception as e:
            # Handle errors
            self._set_headers(500)
            self.wfile.write(json.dumps({"detail": f"Server error: {str(e)}"}).encode())

def run_server(port=8080):
    """Run the HTTP server."""
    server_address = ('', port)
    httpd = HTTPServer(server_address, SimpleAPIHandler)
    print(f"🚀 Starting simple API server on port {port}...")
    print(f"📊 API endpoints available:")
    print(f"  - GET http://localhost:{port}/api/v1/spending")
    print(f"  - GET http://localhost:{port}/api/v1/spending/<transaction_id>")
    print(f"  - GET http://localhost:{port}/api/v1/recommendations")
    print(f"  - GET http://localhost:{port}/api/v1/recommendations/<id>")
    print("\n⚠️ Press Ctrl+C to stop the server")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")

if __name__ == "__main__":
    run_server()
