from flask import Flask, render_template, jsonify, request
from database import Database
from scraper import CarScraper
from scheduler import start_scheduler
import json
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Initialize database and scraper
db = Database()
scraper = CarScraper(db)

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/cars')
def get_cars():
    """API endpoint to get all cars with pagination and filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    status = request.args.get('status', 'all')  # all, active, sold
    
    cars = db.get_cars_with_filters(page, per_page, search, status)
    return jsonify(cars)

@app.route('/api/car/<int:car_id>')
def get_car_detail(car_id):
    """Get detailed information about a specific car"""
    car = db.get_car_by_id(car_id)
    if not car:
        return jsonify({'error': 'Car not found'}), 404
    
    price_history = db.get_price_history(car_id)
    return jsonify({
        'car': car,
        'price_history': price_history
    })

@app.route('/api/stats')
def get_stats():
    """Get dashboard statistics"""
    stats = db.get_dashboard_stats()
    return jsonify(stats)

@app.route('/api/scrape', methods=['POST'])
def manual_scrape():
    """Manually trigger a scrape"""
    try:
        result = scraper.scrape_cars()
        return jsonify({
            'success': True,
            'message': f'Scraped {result["new_cars"]} new cars, updated {result["updated_cars"]} existing cars'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/car/<int:car_id>')
def car_detail(car_id):
    """Car detail page"""
    return render_template('car_detail.html', car_id=car_id)

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Initialize database
    db.init_db()
    
    # Start the scheduler for automated scraping
    start_scheduler(scraper)
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)
