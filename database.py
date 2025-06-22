import sqlite3
import json
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path='car_tracker.db'):
        self.db_path = db_path
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Cars table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cars (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                autotrack_id TEXT NOT NULL,
                dealer_name TEXT NOT NULL,
                make TEXT NOT NULL,
                model TEXT NOT NULL,
                year INTEGER,
                mileage INTEGER,
                fuel_type TEXT,
                description TEXT,
                image_url TEXT,
                source_url TEXT,
                current_price INTEGER NOT NULL,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_sold BOOLEAN DEFAULT FALSE,
                sold_date TIMESTAMP NULL,
                UNIQUE(autotrack_id, dealer_name)
            )
        ''')
        
        # Price history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                car_id INTEGER NOT NULL,
                price INTEGER NOT NULL,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (car_id) REFERENCES cars (id)
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_cars_autotrack_id ON cars(autotrack_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_cars_is_sold ON cars(is_sold)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_price_history_car_id ON price_history(car_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_price_history_recorded_at ON price_history(recorded_at)')
        
        conn.commit()
        conn.close()
        
        logger.info("Database initialized successfully")
    
    def add_car(self, car_data):
        """Add a new car to the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO cars (autotrack_id, make, model, year, mileage, fuel_type, 
                                description, image_url, current_price)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                car_data['autotrack_id'],
                car_data['make'],
                car_data['model'],
                car_data['year'],
                car_data['mileage'],
                car_data['fuel_type'],
                car_data['description'],
                car_data['image_url'],
                car_data['price']
            ))
            
            car_id = cursor.lastrowid
            
            # Add initial price to price history
            cursor.execute('''
                INSERT INTO price_history (car_id, price)
                VALUES (?, ?)
            ''', (car_id, car_data['price']))
            
            conn.commit()
            logger.info(f"Added new car with ID {car_id}")
            return car_id
            
        except sqlite3.IntegrityError as e:
            logger.error(f"Car with AutoTrack ID {car_data['autotrack_id']} already exists")
            raise
        finally:
            conn.close()
    
    def get_car_by_autotrack_id(self, autotrack_id):
        """Get car by AutoTrack ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM cars WHERE autotrack_id = ?', (autotrack_id,))
        car = cursor.fetchone()
        
        conn.close()
        return dict(car) if car else None
    
    def get_car_by_id(self, car_id):
        """Get car by internal ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT *, 
                   (julianday('now') - julianday(first_seen)) as days_on_market
            FROM cars 
            WHERE id = ?
        ''', (car_id,))
        car = cursor.fetchone()
        
        conn.close()
        return dict(car) if car else None
    
    def update_car_price(self, car_id, new_price):
        """Update car price and add to price history"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE cars 
            SET current_price = ?, last_seen = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (new_price, car_id))
        
        cursor.execute('''
            INSERT INTO price_history (car_id, price)
            VALUES (?, ?)
        ''', (car_id, new_price))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Updated price for car ID {car_id} to {new_price}")
    
    def update_car_last_seen(self, car_id):
        """Update last seen timestamp"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE cars 
            SET last_seen = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (car_id,))
        
        conn.commit()
        conn.close()
    
    def mark_cars_as_sold(self, current_autotrack_ids):
        """Mark cars as sold if they're not in current listings"""
        if not current_autotrack_ids:
            return
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create placeholder string for IN clause
        placeholders = ','.join('?' for _ in current_autotrack_ids)
        
        cursor.execute(f'''
            UPDATE cars 
            SET is_sold = TRUE, sold_date = CURRENT_TIMESTAMP
            WHERE autotrack_id NOT IN ({placeholders}) 
            AND is_sold = FALSE
            AND last_seen < datetime('now', '-2 days')
        ''', current_autotrack_ids)
        
        sold_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        if sold_count > 0:
            logger.info(f"Marked {sold_count} cars as sold")
    
    def get_cars_with_filters(self, page=1, per_page=20, search='', status='all'):
        """Get cars with pagination and filtering"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        offset = (page - 1) * per_page
        
        # Build WHERE clause
        where_conditions = []
        params = []
        
        if search:
            where_conditions.append("(make LIKE ? OR model LIKE ? OR description LIKE ?)")
            search_param = f"%{search}%"
            params.extend([search_param, search_param, search_param])
        
        if status == 'active':
            where_conditions.append("is_sold = FALSE")
        elif status == 'sold':
            where_conditions.append("is_sold = TRUE")
        
        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
        
        # Get total count
        cursor.execute(f'''
            SELECT COUNT(*) as total
            FROM cars
            WHERE {where_clause}
        ''', params)
        total = cursor.fetchone()['total']
        
        # Get cars
        cursor.execute(f'''
            SELECT *,
                   (julianday('now') - julianday(first_seen)) as days_on_market,
                   CASE 
                       WHEN is_sold THEN 'Sold'
                       ELSE 'Active'
                   END as status
            FROM cars
            WHERE {where_clause}
            ORDER BY first_seen DESC
            LIMIT ? OFFSET ?
        ''', params + [per_page, offset])
        
        cars = [dict(car) for car in cursor.fetchall()]
        conn.close()
        
        return {
            'cars': cars,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page
        }
    
    def get_price_history(self, car_id):
        """Get price history for a car"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT price, recorded_at
            FROM price_history
            WHERE car_id = ?
            ORDER BY recorded_at ASC
        ''', (car_id,))
        
        history = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return history
    
    def get_dashboard_stats(self):
        """Get dashboard statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Total cars
        cursor.execute('SELECT COUNT(*) as total FROM cars')
        total_cars = cursor.fetchone()['total']
        
        # Active cars
        cursor.execute('SELECT COUNT(*) as active FROM cars WHERE is_sold = FALSE')
        active_cars = cursor.fetchone()['active']
        
        # Sold cars
        cursor.execute('SELECT COUNT(*) as sold FROM cars WHERE is_sold = TRUE')
        sold_cars = cursor.fetchone()['sold']
        
        # Average days on market
        cursor.execute('''
            SELECT AVG(julianday('now') - julianday(first_seen)) as avg_days
            FROM cars WHERE is_sold = FALSE
        ''')
        avg_days_result = cursor.fetchone()
        avg_days_on_market = round(avg_days_result['avg_days'] or 0, 1)
        
        # Price changes in last 7 days
        cursor.execute('''
            SELECT COUNT(*) as price_changes
            FROM price_history
            WHERE recorded_at > datetime('now', '-7 days')
        ''')
        recent_price_changes = cursor.fetchone()['price_changes']
        
        # Average price
        cursor.execute('''
            SELECT AVG(current_price) as avg_price
            FROM cars WHERE is_sold = FALSE AND current_price > 0
        ''')
        avg_price_result = cursor.fetchone()
        avg_price = round(avg_price_result['avg_price'] or 0)
        
        conn.close()
        
        return {
            'total_cars': total_cars,
            'active_cars': active_cars,
            'sold_cars': sold_cars,
            'avg_days_on_market': avg_days_on_market,
            'recent_price_changes': recent_price_changes,
            'avg_price': avg_price
        }
