#!/usr/bin/env python3
"""
Debug script to check price changes in the database
"""
import sqlite3
from datetime import datetime

def debug_price_changes():
    """Debug the price changes functionality"""
    conn = sqlite3.connect('car_tracker.db')
    conn.row_factory = sqlite3.Row
    
    print("=== Price Changes Debug ===")
    
    # Check total price history records
    cursor = conn.execute("SELECT COUNT(*) as total FROM price_history")
    total_price_history = cursor.fetchone()[0]
    print(f"Total price history records: {total_price_history}")
    
    # Check cars with multiple price records
    cursor = conn.execute("""
        SELECT car_id, COUNT(*) as record_count 
        FROM price_history 
        GROUP BY car_id 
        HAVING COUNT(*) > 1
        ORDER BY record_count DESC
        LIMIT 10
    """)
    
    cars_with_multiple_prices = cursor.fetchall()
    print(f"\nCars with multiple price records: {len(cars_with_multiple_prices)}")
    
    for row in cars_with_multiple_prices:
        print(f"  Car ID {row['car_id']}: {row['record_count']} price records")
    
    # Check the actual price change query from the app
    cursor = conn.execute('''
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
            AND ph2.price != ph1.price 
            AND ph1.price > 0 
            AND ph2.price > 0
        ORDER BY ph1.recorded_at DESC
        LIMIT 10
    ''')
    
    actual_price_changes = cursor.fetchall()
    print(f"\nActual price changes found: {len(actual_price_changes)}")
    
    for row in actual_price_changes:
        print(f"  {row['make']} {row['model']} ({row['autotrack_id']}): {row['previous_price']} -> {row['price']}")
    
    # Check what the dashboard stats query returns
    cursor = conn.execute('''
        SELECT 
            COUNT(*) as total_cars,
            SUM(CASE WHEN is_sold = 0 THEN 1 ELSE 0 END) as active_cars,
            SUM(CASE WHEN is_sold = 1 THEN 1 ELSE 0 END) as sold_cars,
            AVG(CASE WHEN days_on_market IS NOT NULL THEN days_on_market END) as avg_days,
            AVG(current_price) as avg_price
        FROM cars
    ''')
    
    stats = cursor.fetchone()
    print(f"\nDashboard stats:")
    print(f"  Total cars: {stats['total_cars']}")
    print(f"  Active cars: {stats['active_cars']}")
    print(f"  Sold cars: {stats['sold_cars']}")
    
    # Check recent price changes count (what might be showing 42)
    cursor = conn.execute('''
        SELECT COUNT(*) as recent_changes
        FROM price_history ph1
        WHERE ph1.recorded_at >= datetime('now', '-7 days')
    ''')
    
    recent_count = cursor.fetchone()[0]
    print(f"\nRecent price records (last 7 days): {recent_count}")
    
    # Check if there are any price differences at all
    cursor = conn.execute('''
        SELECT 
            ph1.car_id,
            ph1.price as current_price,
            ph2.price as previous_price,
            ph1.recorded_at
        FROM price_history ph1
        JOIN price_history ph2 ON ph1.car_id = ph2.car_id 
            AND ph2.id < ph1.id
        WHERE ph1.price != ph2.price
        LIMIT 5
    ''')
    
    any_differences = cursor.fetchall()
    print(f"\nAny price differences found: {len(any_differences)}")
    
    for row in any_differences:
        print(f"  Car {row['car_id']}: {row['previous_price']} -> {row['current_price']} at {row['recorded_at']}")
    
    conn.close()

if __name__ == "__main__":
    debug_price_changes()