from flask import Flask, render_template, request, flash, url_for, redirect, session
import fdb
from flask_bcrypt import generate_password_hash, check_password_hash
from fpdf import FPDF
from flask import send_file

app = Flask(__name__)
app.secret_key = 'GuiIsaLuDuda'

host = 'localhost'
database = r'C:\Users\Aluno\Desktop\UP\BANCO.FDB' #definir o caminho do banco de dados
user = 'SYSDBA'
password = 'sysdba'
con = fdb.connect(host=host, database=database, user=user, password=password)

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/cadastro', methods=['GET', 'POST'])


def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        sobrenome = request.form['sobrenome']
        email = request.form['email'].strip().lower()
        cpf = request.form['cpf']
        telefone = request.form['telefone']
        senha = request.form['senha']
        Csenha = request.form['Csenha']

        if senha != Csenha:
            flash('As senhas não coincidem!')
            return render_template('cadastro_pessoal.html')

        # Tamanho da senha
        if len(senha) < 8 or len(senha) > 12:
            flash('A senha deve ter entre 8 e 12 caracteres.', 'danger')
            return render_template('cadastro_pessoal.html')

        # Validação de complexidade
        maiuscula = False
        minuscula = False
        numero = False
        caracterpcd = False

        for s in senha:
            if s.isupper():
                maiuscula = True
            if s.islower():
                minuscula = True
            if s.isdigit():
                numero = True
            if not s.isalnum():
                caracterpcd = True

        if not (maiuscula and minuscula and numero and caracterpcd):
            flash(
                'A senha deve conter ao menos uma letra maiúscula, '
                'uma letra minúscula, um número e um caractere especial.',
                'danger'
            )
            return render_template('cadastro_pessoal.html')

        senha_cripto = generate_password_hash(senha).decode('utf-8')

        cursor = con.cursor()
        try:
            cursor.execute("SELECT EMAIL FROM USUARIO WHERE EMAIL = ?", (email,))
            if cursor.fetchone():
                flash('Email já cadastrado!')
                return render_template('cadastro_pessoal.html')

            cursor.execute(
                "INSERT INTO USUARIO (NOME, SOBRENOME, EMAIL, CPF, TELEFONE, SENHA) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (nome, sobrenome, email, cpf, telefone, senha_cripto)
            )
            con.commit()
            flash('Usuário cadastrado com sucesso!')
            return render_template('login.html')
        except Exception as e:
            con.rollback()
            flash(f'Erro ao cadastrar: {e}')
            return render_template('cadastro_pessoal.html')
        finally:
            cursor.close()

    return render_template('cadastro_pessoal.html')

if __name__ == '__main__':
    app.run(debug=True)