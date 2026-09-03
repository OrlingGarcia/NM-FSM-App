import random
from flask import Flask, request, flash, url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.sqlite3'
app.config['SECRET_KEY'] = "random string"
db = SQLAlchemy(app)

class Students(db.Model):
    id = db.Column('student_id', db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    city = db.Column(db.String(50))
    addr = db.Column(db.String(200))
    pin = db.Column(db.String(10))
    phone = db.Column(db.String(20))

    def __init__(self, name, city, addr, pin, phone=None):
        self.name = name
        self.city = city
        self.addr = addr
        self.pin = pin
        self.phone = phone

@app.route('/')
def show_all():
    return render_template('show_all.html', students=Students.query.all())

@app.route('/new', methods=['GET', 'POST'])
def new():
    if request.method == 'POST':
        if not request.form.get('name') or not request.form.get('city') or not request.form.get('addr'):
            flash('Please enter all the fields', 'error')
        else:
            student = Students(
                name=request.form['name'],
                city=request.form['city'],
                addr=request.form['addr'],
                pin=request.form.get('pin', ''),
                phone=request.form.get('phone', '')
            )
            db.session.add(student)
            db.session.commit()
            flash('Record was successfully added')
            return redirect(url_for('show_all'))
    return render_template('new.html')

def init_db():
    with app.app_context():
        db.create_all()
        # Verify if 'phone' column exists in SQLite table; add it if missing
        with db.engine.connect() as conn:
            columns = [row[1] for row in conn.execute(db.text("PRAGMA table_info(students)")).fetchall()]
            if 'phone' not in columns:
                conn.execute(db.text("ALTER TABLE students ADD COLUMN phone VARCHAR(20)"))
                conn.commit()

        # Preserve existing students by filling empty phone numbers with random numbers
        existing_without_phone = Students.query.filter(
            (Students.phone == None) | (Students.phone == '')
        ).all()
        if existing_without_phone:
            for student in existing_without_phone:
                student.phone = f"{random.randint(200, 999)}-{random.randint(200, 999)}-{random.randint(1000, 9999)}"
            db.session.commit()

init_db()

if __name__ == '__main__':
    app.run(debug=True)

