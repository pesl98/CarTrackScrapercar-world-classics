from flask import Flask, render_template, jsonify, request, send_file, make_response
from database import Database
from scraper import CarScraper
from multi_dealer_scraper import MultiDealerScraper
from scheduler import start_scheduler
import json
import csv
import io
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Initialize database and scrapers
db = Database()
scraper = CarScraper(db)  # Keep for backwards compatibility
multi_scraper = MultiDealerScraper(db)

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
    """Manually trigger a scrape from all dealers"""
    try:
        new_cars, updated_cars = multi_scraper.scrape_all_dealers()
        return jsonify({
            'success': True,
            'message': f'Multi-dealer scraping completed. Found {new_cars} new cars and updated {updated_cars} existing cars from all dealers.'
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

@app.route('/api/price-changes')
def get_price_changes():
    """Get recent price changes"""
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Get recent price changes with car details - only show meaningful changes
        cursor.execute('''
            SELECT 
                ph1.id,
                ph1.price,
                ph1.recorded_at,
                c.id as car_id,
                c.make,
                c.model,
                c.autotrack_id,
                c.current_price,
                c.is_sold,
                c.sold_date,
                ph2.price as previous_price
            FROM price_history ph1
            JOIN cars c ON ph1.car_id = c.id
            LEFT JOIN price_history ph2 ON ph1.car_id = ph2.car_id 
                AND ph2.recorded_at < ph1.recorded_at
                AND ph2.id = (
                    SELECT MAX(ph3.id) 
                    FROM price_history ph3 
                    WHERE ph3.car_id = ph1.car_id 
                    AND ph3.recorded_at < ph1.recorded_at
                )
            WHERE ph2.price IS NOT NULL 
                AND ABS(ph2.price - ph1.price) > 100
                AND ph1.price > 0 
                AND ph2.price > 0
            ORDER BY ph1.recorded_at DESC
            LIMIT 50
        ''')
        
        price_changes = []
        for row in cursor.fetchall():
            change_data = {
                'id': row[0],
                'price': row[1],
                'recorded_at': row[2],
                'car_id': row[3],
                'make': row[4],
                'model': row[5],
                'autotrack_id': row[6],
                'current_price': row[7],
                'is_sold': row[8],
                'sold_date': row[9],
                'previous_price': row[10]
            }
            
            # Calculate price difference
            if change_data['previous_price']:
                change_data['price_difference'] = change_data['price'] - change_data['previous_price']
                change_data['percentage_change'] = ((change_data['price'] - change_data['previous_price']) / change_data['previous_price']) * 100
            else:
                change_data['price_difference'] = 0
                change_data['percentage_change'] = 0
                
            price_changes.append(change_data)
        
        # Also get recently sold cars
        cursor.execute('''
            SELECT 
                c.id,
                c.make,
                c.model,
                c.autotrack_id,
                c.current_price,
                c.sold_date,
                CAST((julianday(c.sold_date) - julianday(c.first_seen)) AS INTEGER) as days_on_market
            FROM cars c
            WHERE c.is_sold = 1 AND c.sold_date IS NOT NULL
            ORDER BY c.sold_date DESC
            LIMIT 20
        ''')
        
        sold_cars = []
        for row in cursor.fetchall():
            sold_cars.append({
                'id': row[0],
                'make': row[1],
                'model': row[2],
                'autotrack_id': row[3],
                'current_price': row[4],
                'sold_date': row[5],
                'days_on_market': row[6]
            })
        
        conn.close()
        return jsonify({
            'price_changes': price_changes,
            'sold_cars': sold_cars
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export/csv')
def export_cars_csv():
    """Export all cars to CSV file"""
    try:
        # Get all cars from database
        cars = db.get_cars_with_filters(page=1, per_page=10000, search='', status='all')
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'ID', 'Make', 'Model', 'Year', 'Mileage', 'Fuel Type', 
            'Current Price', 'First Seen', 'Last Seen', 'Is Sold', 
            'Sold Date', 'Days on Market', 'Source URL', 'Description'
        ])
        
        # Write car data
        for car in cars['cars']:
            writer.writerow([
                car['id'],
                car['make'],
                car['model'],
                car['year'] or '',
                car['mileage'] or '',
                car['fuel_type'] or '',
                car['current_price'],
                car['first_seen'],
                car['last_seen'],
                'Yes' if car['is_sold'] else 'No',
                car['sold_date'] or '',
                car['days_on_market'] or '',
                car.get('source_url', ''),
                car['description'] or ''
            ])
        
        # Create response
        output.seek(0)
        
        # Generate filename with current date
        filename = f"car_tracker_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename={filename}'
        
        return response
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
    start_scheduler(multi_scraper)
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)
