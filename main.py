from flask import Flask, render_template, request, flash, url_for, redirect, session
import fdb
from flask_bcrypt import generate_password_hash, check_password_hash
from fpdf import FPDF
from flask import send_file

app = Flask(__name__)
app.secret_key = 'GuiIsaLuDuda'

host = 'localhost'
database = r'C:\Users\Guilherme kawanami\Documents\GitHub\UP\BANCO.FDB' #definir o caminho do banco de dados
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
            flash('Usuário cadastrado com sucesso!', 'success')
            session['email_pendente'] = email
            return redirect(url_for('cadastroEmpresa')) 
        except Exception as e:
            con.rollback()
            flash(f'Erro ao cadastrar: {e}')
            return render_template('cadastro_pessoal.html')
        finally:
            cursor.close()

    return render_template('cadastro_pessoal.html')


@app.route('/cadastroEmpresa', methods=['GET', 'POST'])
def cadastroEmpresa():
    if request.method == 'POST':
        email = session.get('email_pendente', '')
        if not email:
            flash('Não foi possível identificar o usuário. Refaça o cadastro.')
            return redirect(url_for('cadastro'))
        
        nomeEmp  = request.form.get('nomeEmp')
        endereco = request.form.get('endereco')
        cnpj     = request.form.get('cnpj')
        tipo     = request.form.get('tipo')
        porte    = request.form.get('porte')
        valor    = request.form.get('valor')

        cursor = con.cursor()
        try:
            cursor.execute("""
                INSERT INTO EMPRESA (NOME, ENDERECO, CNPJ, TIPO, PORTE, VALOR_MAO, ID_USUARIO)
                SELECT ?, ?, ?, ?, ?, ?, u.ID_USUARIO
                FROM USUARIO u
                WHERE u.EMAIL = ?
            """, (nomeEmp, endereco, cnpj, tipo, porte, valor, email))

            con.commit()
            flash('Empresa cadastrada com sucesso!', 'success')

            session.pop('email_pendente', None)

            return redirect(url_for('login'))
        except Exception as e:
            con.rollback()
            flash(f'Erro ao cadastrar: {e}')
            return render_template('cadEmp.html')
        finally:
            cursor.close()

    return render_template('cadEmp.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        senha = request.form.get('senha', '')

        cursor = con.cursor()
        cursor.execute('SELECT u.ID_USUARIO, u.SENHA FROM USUARIO u WHERE u.EMAIL = ?', (email,))
        fetchone = cursor.fetchone()
        cursor.close()

        if not fetchone:
            flash('Email ou senha inválidos.')
            return render_template('login.html')

        id_usuario, senha_hash = fetchone

        if not check_password_hash(senha_hash, senha):
            flash('Email ou senha inválidos.')
            return render_template('login.html')

        session['id_usuario'] = id_usuario
        flash('Login realizado com sucesso!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if 'id_usuario' not in session:
        flash('Faça login para continuar.')
        return redirect(url_for('login'))

    cursor = con.cursor()
    cursor.execute('SELECT NOME FROM USUARIO WHERE ID_USUARIO = ?', (session['id_usuario'],))
    fetchone = cursor.fetchone()
    cursor.close()

    if not fetchone:
        session.clear()
        flash('Sessão inválida. Faça login novamente.')
        return redirect(url_for('login'))

    nome = fetchone[0]
    return render_template('dashboard.html', nome_usuario=nome)


@app.route("/config")
def config():
    return render_template('config.html')


@app.route('/logout')
def logout():
    session.pop('id_usuario', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)