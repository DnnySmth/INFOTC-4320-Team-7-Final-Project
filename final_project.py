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
    if os.path.isfile('data/reservations.txt'):
        with open('data/reservations.txt', 'r') as file:
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
        row = int(reservation[1])
        col = int(reservation[2])
        price = cost_matrix[row][col]
        total_sales += price
    return total_sales

def is_seat_available(row, col, reservations):
    for reservation in reservations:
        res_name ,res_row, res_seat, res_id = reservation
        if int(res_row) == row and int(res_seat) == col:
            return False
    return True

def display_seating_chart(reservations):
    chart = []
    for row in range(12):
        seat_row = []
        for seat in range(4):
            seat_label = f'Row {row + 1}, Seat {seat + 1}'
            if is_seat_available(row, seat, reservations):
                seat_label += ' (Open)'
            else:
                seat_label += ' (Taken)'
            seat_row.append(seat_label)
        chart.append(seat_row)
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
    app.logger.debug(is_seat_available(3,0,reservations))
    
    return render_template('main_menu.html')

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
        app.logger.debug(reservations)
        total_sales = calculate_total_sales(reservations)
        return render_template('admin_portal.html', chart=display_seating_chart(reservations), total_sales=total_sales)
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
