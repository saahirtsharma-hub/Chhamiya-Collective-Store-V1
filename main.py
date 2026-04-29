#!/usr/bin/env python3
"""
Chamyaia Collective - Flask Backend API
Handles jewelry items management and admin operations
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
from datetime import datetime
import uuid

app = Flask(__name__)
CORS(app)

# Database file for storing jewelry items
DATA_FILE = 'jewelry_data.json'

# Admin PIN (Change this to your desired PIN)
ADMIN_PIN = '716441'

# Initialize data file
def init_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w') as f:
            json.dump({'items': []}, f)

# Load data from file
def load_data():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading data: {e}")
        return {'items': []}

# Save data to file
def save_data(data):
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving data: {e}")
        return False

# ===========================
# API ROUTES
# ===========================

@app.route('/api/items', methods=['GET'])
def get_items():
    """Get all jewelry items"""
    data = load_data()
    return jsonify(data['items'])

@app.route('/api/items', methods=['POST'])
def add_item():
    """Add a new jewelry item (requires PIN verification)"""
    pin = request.headers.get('X-Admin-PIN')
    
    # Verify PIN
    if pin != ADMIN_PIN:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    
    # Validate required fields
    if not data.get('name') or not data.get('image'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Create new item
    new_item = {
        'id': str(uuid.uuid4()),
        'name': data.get('name'),
        'price': data.get('price', ''),
        'description': data.get('description', ''),
        'image': data.get('image'),
        'instagram': data.get('instagram', 'https://instagram.com/chamyaiacollective'),
        'category': data.get('category', 'Jewelry'),
        'created_at': datetime.now().isoformat()
    }
    
    # Save to database
    file_data = load_data()
    file_data['items'].append(new_item)
    
    if save_data(file_data):
        return jsonify(new_item), 201
    else:
        return jsonify({'error': 'Failed to save item'}), 500

@app.route('/api/items/<item_id>', methods=['DELETE'])
def delete_item(item_id):
    """Delete a jewelry item (requires PIN verification)"""
    pin = request.headers.get('X-Admin-PIN')
    
    # Verify PIN
    if pin != ADMIN_PIN:
        return jsonify({'error': 'Unauthorized'}), 401
    
    file_data = load_data()
    
    # Find and remove item
    file_data['items'] = [item for item in file_data['items'] if item['id'] != item_id]
    
    if save_data(file_data):
        return jsonify({'message': 'Item deleted successfully'}), 200
    else:
        return jsonify({'error': 'Failed to delete item'}), 500

@app.route('/api/items/<item_id>', methods=['PUT'])
def update_item(item_id):
    """Update a jewelry item (requires PIN verification)"""
    pin = request.headers.get('X-Admin-PIN')
    
    # Verify PIN
    if pin != ADMIN_PIN:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    file_data = load_data()
    
    # Find and update item
    for item in file_data['items']:
        if item['id'] == item_id:
            item.update({
                'name': data.get('name', item['name']),
                'price': data.get('price', item['price']),
                'description': data.get('description', item['description']),
                'image': data.get('image', item['image']),
                'instagram': data.get('instagram', item['instagram']),
                'category': data.get('category', item['category']),
                'updated_at': datetime.now().isoformat()
            })
            
            if save_data(file_data):
                return jsonify(item), 200
            else:
                return jsonify({'error': 'Failed to update item'}), 500
    
    return jsonify({'error': 'Item not found'}), 404

@app.route('/api/verify-pin', methods=['POST'])
def verify_pin():
    """Verify admin PIN"""
    data = request.json
    pin = data.get('pin')
    
    if pin == ADMIN_PIN:
        return jsonify({'valid': True}), 200
    else:
        return jsonify({'valid': False}), 401

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'service': 'Chamyaia Collective API'}), 200

# ===========================
# ERROR HANDLERS
# ===========================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Server error'}), 500

# ===========================
# STARTUP
# ===========================

if __name__ == '__main__':
    init_data()
    print("=" * 50)
    print("Chamyaia Collective - Admin Panel")
    print("=" * 50)
    print(f"API running on http://localhost:5000")
    print(f"Admin PIN: {ADMIN_PIN}")
    print(f"Data file: {DATA_FILE}")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)
