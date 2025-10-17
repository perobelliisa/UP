from flask import Flask, render_template, request, flash, url_for, redirect, session
import fdb
from flask_bcrypt import generate_password_hash, check_password_hash
from fpdf import FPDF
from flask import send_file

app = Flask(__name__)
app.secret_key = 'GuiIsaLuDuda'

host = 'localhost'
database = r'C:\Users\luisa\OneDrive\Documentos\GitHub\UP\BANCO.FDB' #definir o caminho do banco de dados
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
    email = session.get('email_pendente', '')
    if request.method == 'POST':
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
    if 'email_pendente' not in session:
        flash('Não foi possível identificar o usuário. Faça o login ou se cadastre.')
        return redirect(url_for('login'))
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

        if 'email_pendente' in session:
            flash('Termine o cadastro da sua empresa primeiro.')
            return redirect(url_for('cadastroEmpresa'))
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
    cursor = con.cursor()
    cursor.execute('SELECT NOME FROM EMPRESA WHERE ID_USUARIO = ?', (session['id_usuario'],))
    empresa = cursor.fetchone()
    print(empresa)
    cursor.close()
    return render_template('dashboard.html', nome=nome, empresa=empresa)


@app.route("/config")
def config():
    if 'id_usuario' not in session:
        flash('Faça login para continuar.')
        return redirect(url_for('login'))
    id = session.get('id_usuario', '')
    print(id)
    try:
        cursor = con.cursor()
        cursor.execute('SELECT NOME, SOBRENOME, EMAIL, TELEFONE, ID_USUARIO FROM USUARIO WHERE ID_USUARIO = ?', (session['id_usuario'],))
        usuario = cursor.fetchone()
        print(usuario)
        cursor.execute('SELECT NOME, TIPO FROM EMPRESA WHERE ID_USUARIO = ?', (session['id_usuario'],))

        empresa = cursor.fetchone()
        print(empresa)
        if empresa[1] == 1:
            tipo = "Confeitaria"
        elif empresa[1] == 2:
            tipo = "Padaria"
        elif empresa[1] == 3:
            tipo = "Hort Fruit"
        elif empresa[1] == 4:
            tipo = "Lanchonete"
        else:
            tipo = "Outros"
    finally:
        cursor.close()
    return render_template('config.html', usuario=usuario, empresa=empresa, tipo=tipo)

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    if "id_usuario" not in session:
        flash("Você precisa estar logado para acessar essa página", "error")
        return redirect(url_for('login'))

    cursor = con.cursor()

    cursor.execute("""
        SELECT u.ID_USUARIO, u.NOME, u.SOBRENOME, u.EMAIL, u.CPF, u.TELEFONE, u.SENHA
        FROM USUARIO u
        WHERE u.ID_USUARIO = ?
    """, (id,))
    usuario = cursor.fetchone()

    if not usuario:
        cursor.close()
        flash("Usuário não foi encontrado")
        return redirect(url_for('index'))

    cursor.execute("""
        SELECT NOME, ENDERECO, CNPJ, TIPO, PORTE, VALOR_MAO
        FROM EMPRESA
        WHERE ID_USUARIO = ?
    """, (id,))
    empresa = cursor.fetchone()
    if not empresa:
        # mesma ordem do SELECT acima
        empresa = ("", "", "", "", "", "")

    if request.method == 'POST':
        nome      = request.form['nome']
        sobrenome = request.form['sobrenome']
        email     = request.form['email']
        cpf       = request.form['cpf']
        telefone  = request.form['telefone']
        senha     = request.form['senha']     # pode vir vazio

        nomeE     = request.form['nomeEmp']
        endereco  = request.form['endereco']
        cnpj      = request.form['cnpj']
        tipo      = request.form['tipo']
        porte     = request.form['porte']
        valor     = request.form['valor']

        try:
            if senha:
                senha_cripto = generate_password_hash(senha)  # já retorna str
                cursor.execute("""
                    UPDATE USUARIO
                       SET NOME = ?, SOBRENOME = ?, EMAIL = ?, CPF = ?, TELEFONE = ?, SENHA = ?
                     WHERE ID_USUARIO = ?
                """, (nome, sobrenome, email, cpf, telefone, senha_cripto, id))
            else:
                cursor.execute("""
                    UPDATE USUARIO
                       SET NOME = ?, SOBRENOME = ?, EMAIL = ?, CPF = ?, TELEFONE = ?
                     WHERE ID_USUARIO = ?
                """, (nome, sobrenome, email, cpf, telefone, id))

            cursor.execute("""
                UPDATE EMPRESA
                   SET NOME = ?, ENDERECO = ?, CNPJ = ?, TIPO = ?, PORTE = ?, VALOR_MAO = ?
                 WHERE ID_USUARIO = ?
            """, (nomeE, endereco, cnpj, tipo, porte, valor, id))

            con.commit()
            flash("Usuário atualizado com sucesso")
            cursor.close()
            return redirect(url_for('dashboard'))

        except Exception as e:
            con.rollback()
            cursor.close()
            flash(f"Erro ao atualizar: {e}", "error")
            return redirect(url_for('editar', id=id))

    cursor.close()
    return render_template('editar_Usuario.html', id=id, usuario=usuario, empresa=empresa)
@app.route('/logout')
def logout():
    session.pop('id_usuario', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)