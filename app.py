from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, obter_conexao
import smtplib
import email.message

app = Flask(__name__)
app.config['SECRET_KEY'] = 'SUPERSECRETO'

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        user = User.get_by_email(email)

        if user and check_password_hash(user.senha, senha):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Email ou senha incorretos', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        idade = request.form['idade']

        conn = obter_conexao()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tb_usuarios WHERE usr_email = %s", (email,))
        existing_user = cursor.fetchone()
        cursor.close()
        conn.close()

        if existing_user:
            flash('Esse email já está cadastrado!', 'error')
            return redirect(url_for('register'))

        senha_hashed = generate_password_hash(senha)
        
        conn = obter_conexao()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tb_usuarios (usr_email, usr_senha, usr_nome, usr_idade) VALUES (%s, %s, %s, %s)",
                       (email, senha_hashed, nome, idade))
        conn.commit()
        cursor.close()
        conn.close()

        enviar_email_confirmacao(email)
        flash('Usuário registrado com sucesso!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/eventos', methods=['GET', 'POST'])
@login_required
def eventos():
    if request.method == 'POST':
        nome = request.form['nome']
        data = request.form['data']
        premio = request.form['premio']
        adicionar_evento(nome, data, premio)
        flash('Evento cadastrado com sucesso!', 'success')
        return redirect(url_for('eventos'))

    eventos = buscar_eventos()
    return render_template('eventos.html', eventos=eventos)

@app.route('/remover_evento/<int:eve_id>', methods=['POST'])
@login_required
def remover_evento(eve_id):
    excluir_evento(eve_id)
    flash('Evento removido com sucesso!', 'success')
    return redirect(url_for('eventos'))

def adicionar_evento(nome, data, premio):
    conexao = obter_conexao()
    cursor = conexao.cursor()
    cursor.execute("INSERT INTO tb_eventos (eve_nome, eve_data, eve_premio) VALUES (%s, %s, %s)", (nome, data, premio))
    conexao.commit()
    conexao.close()

def buscar_eventos():
    conexao = obter_conexao()
    cursor = conexao.cursor()
    cursor.execute("SELECT * FROM tb_eventos")
    resultados = cursor.fetchall()
    conexao.close()
    return resultados

def excluir_evento(eve_id):
    conexao = obter_conexao()
    cursor = conexao.cursor()
    cursor.execute("DELETE FROM tb_eventos WHERE eve_id = %s", (eve_id,))
    conexao.commit()
    conexao.close()

@app.route('/corridas', methods=['GET', 'POST'])
@login_required
def corridas():
    if request.method == 'POST':
        data = request.form['data']
        tempo = request.form['tempo']
        evento_id = request.form['evento_id']
        distancia = request.form['distancia']
        adicionar_corrida(data, tempo, evento_id, distancia)
        flash('Corrida cadastrada com sucesso!', 'success')
        return redirect(url_for('corridas'))

    eventos = buscar_eventos() 
    corridas = buscar_corridas() 
    return render_template('corridas.html', corridas=corridas, eventos=eventos)

@app.route('/remover_corrida/<int:cor_id>', methods=['POST'])
@login_required
def remover_corrida(cor_id):
    excluir_corrida(cor_id)
    flash('Corrida removida com sucesso!', 'success')
    return redirect(url_for('corridas'))

def adicionar_corrida(data, tempo, evento_id, distancia):
    conexao = obter_conexao()
    cursor = conexao.cursor()
    cursor.execute("INSERT INTO tb_corridas (cor_data, cor_tempo, cor_eve_id, cor_distancia) VALUES (%s, %s, %s, %s)", (data, tempo, evento_id, distancia))
    conexao.commit()
    conexao.close()


def buscar_corridas():
    conexao = obter_conexao()
    cursor = conexao.cursor()
    cursor.execute("""
        SELECT c.cor_id, c.cor_data, c.cor_tempo, c.cor_distancia, c.cor_eve_id, e.eve_nome 
        FROM tb_corridas c 
        JOIN tb_eventos e ON c.cor_eve_id = e.eve_id
    """)
    resultados = cursor.fetchall()
    conexao.close()
    return resultados

def excluir_corrida(cor_id):
    conexao = obter_conexao()
    cursor = conexao.cursor()
    cursor.execute("DELETE FROM tb_corridas WHERE cor_id = %s", (cor_id,))
    conexao.commit()
    conexao.close()


def enviar_email_confirmacao(destinatario):
    corpo_email = "Seu email foi cadastrado com sucesso!"

    msg = email.message.Message()
    msg['Subject'] = "Email cadastrado!!"
    msg['From'] = '777xotes.oficial@gmail.com'
    msg['To'] = destinatario
    password = 'ibudxbjgtobyixbm' 
    msg.add_header('Content-Type', 'text/html')
    msg.set_payload(corpo_email )

    s = smtplib.SMTP('smtp.gmail.com: 587')
    s.starttls()
    s.login(msg['From'], password)
    s.sendmail(msg['From'], [msg['To']], msg.as_string().encode('utf-8'))
    print('Email enviado')


if __name__ == '__main__':
    app.run(debug=True)
