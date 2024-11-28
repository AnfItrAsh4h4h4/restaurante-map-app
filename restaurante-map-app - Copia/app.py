from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import statistics

app = Flask(__name__)
app.secret_key = 'your_secret_key'
CORS(app)

# Configuração do Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Dados fictícios para usuários e restaurantes
users = {
    "user1": {"password": "password1", "favorites": []},
    "user2": {"password": "password2", "favorites": []}
}

restaurants = [
    {"name": "Nonna Augusta Trattoria - Asa Norte", "cuisine": "Italiana", "latitude": -15.74726, "longitude": -47.88314, "rating": 5, "reviews": {}},
    {"name": "Piselli Brasília", "cuisine": "Italiana", "latitude": -15.83, "longitude": -47.9498, "rating": 4.9, "reviews": {}},
    {"name": "Rubaiyat Brasília", "cuisine": "Brasileira", "latitude": -15.82663, "longitude": -47.88718, "rating": 4.2, "reviews": {}},
]

# Classe para gerenciar usuários no Flask-Login
class User(UserMixin):
    def __init__(self, username):
        self.id = username
        self.favorites = users[username]["favorites"]

@login_manager.user_loader
def load_user(user_id):
    if user_id in users:
        return User(user_id)
    return None

# Rotas da aplicação
@app.route('/')
@login_required
def index():
    return render_template('index.html', restaurants=restaurants, user=current_user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username in users and users[username]['password'] == password:
            user = User(username)
            login_user(user)
            return redirect(url_for('index'))
        else:
            return "Usuário ou senha inválidos", 401
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/api/restaurants', methods=['GET'])
@login_required
def get_restaurants():
    # Calcula a avaliação média para cada restaurante
    for restaurant in restaurants:
        if restaurant["reviews"]:
            restaurant["rating"] = round(statistics.mean(restaurant["reviews"].values()), 2)
    return jsonify(restaurants)

@app.route('/api/reviews', methods=['POST'])
@login_required
def add_review():
    data = request.get_json()
    restaurant_name = data.get("name")
    review = data.get("review")
    user = current_user.id

    # Busca o restaurante pelo nome
    for restaurant in restaurants:
        if restaurant["name"] == restaurant_name:
            # Verifica se o usuário já avaliou
            if user in restaurant["reviews"]:
                restaurant["reviews"][user] = review
                return jsonify({"message": "Sua avaliação foi atualizada com sucesso!"})
            else:
                # Salva a nova avaliação
                restaurant["reviews"][user] = review
                return jsonify({"message": "Avaliação salva com sucesso!"})

    return jsonify({"error": "Restaurante não encontrado"}), 404


if __name__ == '__main__':
    app.run(debug=True)
