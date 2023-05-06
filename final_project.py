from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__)
app.debug = True
app.secret_key = os.urandom(24)
toolbar = DebugToolbarExtension(app)

def get_cost_matrix():
    cost_matrix = [[100, 75, 50, 100] for row in range(12)]
    return cost_matrix

def load_reservations():
    reservations = []
    if os.path.isfile('reservations.txt'):
        with open('reservations.txt', 'r') as file:
            for line in file:
                reservation = line.strip().split(',')
                reservations.append(reservation)
    return reservations

def save_reservation(reservation):
    with open('reservations.txt', 'a') as file:
        file.write(','.join(reservation) + '\n')

def calculate_total_sales(reservations):
    cost_matrix = get_cost_matrix()
    total_sales = 0
    for reservation in reservations:
        row = int(reservation[1]) - 1
        col = int(reservation[2]) - 1
        price = cost_matrix[row][col]
        total_sales += price
    return total_sales

def is_seat_available(row, col, reservations):
    for reservation in reservations:
        if reservation[1] == str(row) and reservation[2] == str(col):
            return False
    return True

def display_seating_chart():
    cols = 4
    rows = 12
    chart = [[f'Row {row}, Seat {seat}' for seat in range(1, cols + 1)] for row in range(1, rows + 1)]
    return chart

def generate_reservation_code():
    return str(os.urandom(8).hex())

def authenticated(user, pwd):
    with open('data/passcodes.txt','r') as pwds:
        credentials = [line.strip().split(', ') for line in pwds]
    return any( cred[0] == user and cred[1] == pwd for cred in credentials )

@app.route('/')
def main_menu():
    reservations = load_reservations()
    app.logger.debug(get_cost_matrix())
    
    return render_template('main_menu.html', chart=display_seating_chart(reservations))

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    return render_template('admin_login.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if authenticated(username, password):
            session['admin'] = True
            reservations = load_reservations()
            return redirect(url_for('admin_portal'))
        else:
            flash('Invalid username or password', 'error')
            return redirect(url_for('admin'))
    
    
@app.route('/reservation')
def reservation():
    return render_template('reservation_form.html')

@app.route('/admin_portal')
def admin_portal():
    if session['admin']:
        reservations = load_reservations()
        total_sales = calculate_total_sales(reservations)
        return render_template('admin_portal.html', chart=display_seating_chart(), total_sales=total_sales)
    else:
        return redirect(url_for('admin'))
    
@app.route('/reserve', methods=['POST'])
def reserve():
    fname = request.form.get('first_name')
    lname = request.form.get('last_name')
    row = request.form.get('seat_row')
    col = request.form.get('seat_col')
    return render_template('output.html', formdata = {'fname': fname, 'lname': lname, 'row': row, 'col': col})
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5002')
