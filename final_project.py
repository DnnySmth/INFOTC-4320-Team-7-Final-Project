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
    reservations = load_reservations()
    with open('data/reservations.txt', 'a') as file:
        file.write(', '.join(reservation) + '\n')

def calculate_total_sales(reservations):
    cost_matrix = get_cost_matrix()
    total_sales = 0
    for reservation in reservations:
        row = int(reservation[1])
        col = int(reservation[2])
        price = cost_matrix[row][col]
        total_sales += price
    return total_sales

def is_seat_available(row, col):
    reservations = load_reservations()
    for reservation in reservations:
        res_name ,res_row, res_seat, res_id = reservation
        if int(res_row) == row and int(res_seat) == col:
            return False
    return True

def does_reservation_exist(code):
    reservations = load_reservations()
    for reservation in reservations:
        res_name, res_row, res_seat, res_code = reservation
        if code == res_code.strip():
            return True
    return False

def display_seating_chart():
    chart = []
    for row in range(12):
        seat_row = []
        for seat in range(4):
            seat_label = f'Row {row + 1}, Seat {seat + 1}'
            if is_seat_available(row, seat):
                seat_label += ' (Open)'
            else:
                seat_label += ' (Taken)'
            seat_row.append(seat_label)
        chart.append(seat_row)
    return chart

def authenticated(user, pwd):
    with open('data/passcodes.txt','r') as pwds:
        credentials = [line.strip().split(', ') for line in pwds]
    return any( cred[0] == user and cred[1] == pwd for cred in credentials )

def generate_reservation_code(name):
    infotech = list("INFOTC4320")
    reservation_code = ""
    for i in range(max(len(name),len(infotech))):
        if(i < len(name)):
            reservation_code += name[i]
        if(i < len(infotech)):
            reservation_code += infotech[i]
    return reservation_code

@app.route('/')
def main_menu():   
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
            return redirect(url_for('admin_portal'))
        else:
            session['admin'] = False
            flash('Invalid username or password', 'error')
            return redirect(url_for('admin'))

@app.route('/admin_portal')
def admin_portal():
    if session['admin']:
        reservations = load_reservations()
        total_sales = calculate_total_sales(reservations)
        return render_template('admin_portal.html', chart=display_seating_chart(), total_sales=total_sales)
    else:
        return redirect(url_for('admin'))
    
@app.route('/reservation')
def reservation():
    reservations = load_reservations()
    return render_template('reservation_form.html', chart=display_seating_chart())
    
@app.route('/reserve', methods=['GET', 'POST'])
def reserve():
    fname = request.form.get('first_name')
    lname = request.form.get('last_name')
    row = int(request.form.get('seat_row'))
    col = int(request.form.get('seat_col'))
    res_code = generate_reservation_code(fname)
    reservation = [fname, str(row-1), str(col-1), res_code]
    if is_seat_available(row-1, col-1) and not does_reservation_exist(res_code):
        save_reservation(reservation)
        return render_template('reservation_created.html', resdata = {'fname': fname, 'lname': lname, 'row': row, 'col': col, 'res_code': res_code})
    else:
        flash(f'Reservation { res_code } already exists.', 'error')
        return redirect(url_for('reservation'))
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5002')
