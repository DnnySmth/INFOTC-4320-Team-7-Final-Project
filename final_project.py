from flask import Flask, render_template, request, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

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

def display_seating_chart(reservations):
    cost_matrix = get_cost_matrix()
    chart = '<table>'
    for row in range(1, 13):
        chart += '<tr>'
        for col in range(1, 5):
            if is_seat_available(row, col, reservations):
                chart += f'<td><a href="/reserve?row={row}&col={col}">R{row}C{col}</a></td>'
            else:
                chart += f'<td>R{row}C{col}</td>'
        chart += '</tr>'
    chart += '</table>'
    return chart

def generate_reservation_code():
    return str(os.urandom(8).hex())

@app.route('/')
def main_menu():
    reservations = load_reservations()
    return render_template('main_menu.html', chart=display_seating_chart(reservations))

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'password':
            session['admin'] = True
            reservations = load_reservations()
            return redirect(url_for('admin_portal'))
    return render_template('admin_login.html')

@app.route('/admin_portal')
def admin_portal():
    if 'admin' in session and session['admin']:
        reservations = load_reservations()
        total_sales = calculate_total_sales(reservations)
        return render_template('admin_portal.html', chart=display_seating_chart(reservations), total_sales=total_sales)
    else:
        return redirect(url_for('admin_login'))
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5002')
