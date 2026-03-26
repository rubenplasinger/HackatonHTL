from flask import Flask, render_template
from Quizphase import quiz_bp
from Lernphase import lern_bp
from Charakter import char_bp

app = Flask(__name__)
app.secret_key = 'wanderung-secret-key-2024'

app.register_blueprint(quiz_bp)
app.register_blueprint(lern_bp)
app.register_blueprint(char_bp)

@app.route('/')
def index():
    return render_template('hackaton_startseite.html')

if __name__ == '__main__':
    app.run(debug=True)
