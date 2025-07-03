from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'capture_moments_secret_key_2024'

# Database setup
def init_db():
    conn = sqlite3.connect('capture_moments.db')
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  email TEXT UNIQUE NOT NULL,
                  phone TEXT NOT NULL,
                  user_type TEXT NOT NULL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Bookings table
    c.execute('''CREATE TABLE IF NOT EXISTS bookings
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  photographer_name TEXT NOT NULL,
                  event_type TEXT NOT NULL,
                  event_date DATE NOT NULL,
                  location TEXT NOT NULL,
                  package_type TEXT NOT NULL,
                  total_cost INTEGER NOT NULL,
                  status TEXT DEFAULT 'pending',
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')
    
    # Portfolio table
    c.execute('''CREATE TABLE IF NOT EXISTS portfolio
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  photographer_name TEXT NOT NULL,
                  image_url TEXT NOT NULL,
                  category TEXT NOT NULL,
                  description TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    conn.commit()
    conn.close()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/portfolio')
def portfolio():
    conn = sqlite3.connect('capture_moments.db')
    c = conn.cursor()
    c.execute('SELECT * FROM portfolio ORDER BY created_at DESC')
    portfolio_items = c.fetchall()
    conn.close()
    return render_template('portfolio.html', portfolio_items=portfolio_items)

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        event_type = request.form['event_type']
        event_date = request.form['event_date']
        location = request.form['location']
        package_type = request.form['package_type']
        photographer = request.form['photographer']
        
        # Calculate cost based on package
        package_costs = {
            'basic': 15000,
            'standard': 25000,
            'premium': 40000,
            'luxury': 60000
        }
        total_cost = package_costs.get(package_type, 15000)
        
        conn = sqlite3.connect('capture_moments.db')
        c = conn.cursor()
        
        # Insert user if not exists
        c.execute('INSERT OR IGNORE INTO users (name, email, phone, user_type) VALUES (?, ?, ?, ?)',
                  (name, email, phone, 'client'))
        
        # Get user ID
        c.execute('SELECT id FROM users WHERE email = ?', (email,))
        user_id = c.fetchone()[0]
        
        # Insert booking
        c.execute('''INSERT INTO bookings 
                     (user_id, photographer_name, event_type, event_date, location, package_type, total_cost)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (user_id, photographer, event_type, event_date, location, package_type, total_cost))
        
        conn.commit()
        conn.close()
        
        flash('Booking submitted successfully! We will contact you soon.', 'success')
        return redirect(url_for('booking'))
    
    return render_template('booking.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/photographer-register', methods=['GET', 'POST'])
def photographer_register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        experience = request.form['experience']
        specialization = request.form['specialization']
        
        conn = sqlite3.connect('capture_moments.db')
        c = conn.cursor()
        c.execute('INSERT OR IGNORE INTO users (name, email, phone, user_type) VALUES (?, ?, ?, ?)',
                  (name, email, phone, 'photographer'))
        conn.commit()
        conn.close()
        
        flash('Registration successful! We will review your application.', 'success')
        return redirect(url_for('home'))
    
    return render_template('photographer_register.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)