from flask import Flask, render_template, request, flash, url_for, redirect, session
import fdb
from flask_bcrypt import generate_password_hash, check_password_hash
from fpdf import FPDF
from flask import send_file

app = Flask(__name__)
app.secret_key = 'GuiIsaLuDuda'

host = 'localhost'
database = r'C:\Users\Aluno\Desktop\UP1\BANCO.FDB' #definir o caminho do banco de dados
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
            cursor.execute("SELECT CPF FROM USUARIO WHERE CPF = ?", (cpf,))
            if cursor.fetchone():
                flash('CPF já cadastrado!')
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
    if 'id_usuario' in session:
        flash('Faça logout para cadastrar outra conta.')
        return redirect(url_for('dashboard'))
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
            cursor.execute("SELECT CNPJ FROM EMPRESA WHERE CNPJ = ?", (cnpj,))
            if cursor.fetchone():
                flash('CNPJ já cadastrado!')
                return render_template('cadastro_empresa.html')

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
            return render_template('cadEmp.html')
        finally:
            cursor.close()
    if 'id_usuario' in session:
        flash('Faça logout para cadastrar outra conta.')
        return redirect(url_for('dashboard'))
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
        id = fetchone[0]
        cursor.close()

        if not fetchone:
            flash('Email ou senha inválidos.')
            return render_template('login.html')

        id_usuario, senha_hash = fetchone

        if not check_password_hash(senha_hash, senha):
            flash('Email ou senha inválidos.')
            return render_template('login.html')
        cursor = con.cursor()
        cursor.execute('SELECT NOME FROM EMPRESA WHERE ID_USUARIO = ?', (id,))
        empresa = cursor.fetchone()
        cursor.close()
        if empresa == None:
            flash('Termine o cadastro da sua empresa primeiro.')
            return render_template('cadEmp.html', id=id)
        session['id_usuario'] = id_usuario
        flash('Login realizado com sucesso!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('login.html')



@app.route('/conta')
def conta():
    # Redireciona o usuário para o local correto ao clicar em "Conta"
    if 'id_usuario' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'id_usuario' not in session:
        flash('Faça login para continuar.')
        return redirect(url_for('login'))
    id = session['id_usuario']
    cursor = con.cursor()
    cursor.execute('SELECT NOME FROM USUARIO WHERE ID_USUARIO = ?', (id,))
    fetchone = cursor.fetchone()
    cursor.close()

    if not fetchone:
        session.clear()
        flash('Sessão inválida. Faça login novamente.')
        return redirect(url_for('login'))

    nome = fetchone[0]
    cursor = con.cursor()
    cursor.execute('SELECT NOME FROM EMPRESA WHERE ID_USUARIO = ?', (id,))
    empresa = cursor.fetchone()
    print(empresa)
    cursor.close()
    return render_template('dashboard.html', nome=nome, empresa=empresa, id=id)


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

    # --- BUSCA USUÁRIO (retorna TUPLA) ---
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

    # --- BUSCA EMPRESA (TUPLA ou placeholder) ---
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
        senha     = request.form['senha']    

        nomeE     = request.form['nomeEmp']
        endereco  = request.form['endereco']
        cnpj      = request.form['cnpj']
        tipo      = request.form['tipo']
        porte     = request.form['porte']
        valor     = request.form['valor']

        try:
            cursor.execute("SELECT EMAIL FROM USUARIO WHERE EMAIL = ? and id_usuario <> ? ", (email,id))
            if cursor.fetchone():
                flash('Email já cadastrado!')
                return render_template('editar_Usuario.html', id=id, usuario=usuario, empresa=empresa)
            cursor.execute("SELECT CPF FROM USUARIO WHERE CPF = ? and id_usuario <> ? ", (cpf,id))
            if cursor.fetchone():
                flash('CPF já cadastrado!')
                return render_template('editar_Usuario.html', id=id, usuario=usuario, empresa=empresa)

            if senha:
                senha_cripto = generate_password_hash(senha)
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

            # --- EMPRESA ---
            cursor.execute("""
                UPDATE EMPRESA
                   SET NOME = ?, ENDERECO = ?, CNPJ = ?, TIPO = ?, PORTE = ?, VALOR_MAO = ?
                 WHERE ID_USUARIO = ?
            """, (nomeE, endereco, cnpj, tipo, porte, valor, id))

            con.commit()
            flash("Usuário atualizado com sucesso", "success")
            cursor.close()
            return redirect(url_for('dashboard'))

        except Exception as e:
            con.rollback()
            cursor.close()
            flash(f"Erro ao atualizar: {e}", "error")
            return redirect(url_for('editar', id=id))

    cursor.close()
    # GET: envia as TUPLAS para pré-preencher (use índices no template)
    return render_template('editar_Usuario.html', id=id, usuario=usuario, empresa=empresa)

@app.route('/insumos/<int:id>')
def insumos(id):
    if "id_usuario" not in session:
        flash("Você precisa estar logado para acessar essa página", "error")
        return redirect(url_for('login'))

    cursor = con.cursor()
    cursor.execute("""SELECT ID_INSUMO
     , NOME
     , DESCRICAO
     , (
            SELECT FIRST 1 PRECO_COMPRA 
                      FROM HISTORICO_PRECO 
                      WHERE HISTORICO_PRECO.ID_INSUMO = INSUMO.ID_INSUMO 
                      ORDER BY DATA_MUDANCA DESC)
     , CASE UNIDADE_DE_MEDIDA
         WHEN 1 THEN 'Quilo'
         WHEN 2 THEN 'Grama'
         WHEN 3 THEN 'Litro'
         WHEN 4 THEN 'Mililitro'
         WHEN 5 THEN 'Unidade'
        ELSE ''
       END AS DESCRICAO_UNIDADE
     , PESO_UNIDADE 
     FROM INSUMO WHERE ID_USUARIO = ?""", (id,))
    insumos = cursor.fetchall()
    cursor.execute('SELECT NOME FROM USUARIO WHERE ID_USUARIO = ?', (id,))
    fetchone = cursor.fetchone()
    if not fetchone:
        session.clear()
        flash('Sessão inválida. Faça login novamente.')
        return redirect(url_for('login'))
    nome = fetchone[0]
    cursor.execute('SELECT NOME FROM EMPRESA WHERE ID_USUARIO = ?', (id,))
    empresa = cursor.fetchone()
    cursor.close()
    return render_template('insumos.html', id=id, insumos=insumos, nome=nome, empresa=empresa)

@app.route('/cad_insumo/<int:id>', methods=['GET', 'POST'])
def cad_insumo(id):
    if "id_usuario" not in session:
        flash("Você precisa estar logado para acessar essa página", "error")
        return redirect(url_for('login'))
    if request.method == 'POST':
        nome = request.form['nomeInsumo'].capitalize()
        descricao = request.form['descricao']
        peso_unidade = float(request.form['peso_unidade'])
        unidade_de_medida = int(request.form['unidade'])
        preco_compra = round(float(request.form.get('preco')), 2)

        cursor = con.cursor()
        try:
            cursor.execute("SELECT NOME FROM INSUMO WHERE NOME = ? AND ID_USUARIO = ?", (nome, id,))
            if cursor.fetchone():
                flash('Insumo já cadastrado!')
                return render_template('cad_Insumo.html', id=id)
            if unidade_de_medida == 1 or unidade_de_medida == 3:
                quantidade = float(peso_unidade * 1000)
                preco_unidade = float(preco_compra / quantidade)
            else:
                quantidade = float(peso_unidade)
                preco_unidade = float(preco_compra / quantidade)


            cursor.execute(
                """INSERT INTO INSUMO
                   (NOME, DESCRICAO, PESO_UNIDADE, UNIDADE_DE_MEDIDA, ID_USUARIO)
                   VALUES (?, ?, ?, ?, ?)""",
                (nome, descricao, peso_unidade, unidade_de_medida, id)
            )
            con.commit()

            cursor.execute("SELECT ID_INSUMO FROM INSUMO WHERE NOME = ? AND ID_USUARIO = ?", (nome, id,))
            id_insumo = cursor.fetchone()[0]
            cursor.execute(
                """INSERT INTO HISTORICO_PRECO
                       (ID_INSUMO, PRECO_COMPRA, PRECO_UNIDADE)
                       VALUES (?, ?, ?)""",
                    (id_insumo, preco_compra, preco_unidade)
            )
            con.commit()

            cursor.execute(
                """INSERT INTO ESTOQUE
                       (ID_INSUMO, QUANTIDADE)
                   VALUES (?, ?)""",
                (id_insumo, quantidade)
            )
            con.commit()

            flash('Insumo cadastrado com sucesso!', 'success')
            return redirect(url_for('insumos', id=id))
        except Exception as e:
            con.rollback()
            flash(f'Erro ao cadastrar: {e}')
            return render_template('cad_Insumo.html', id=id)
        finally:
            cursor.close()
    return render_template('cad_Insumo.html', id=id)


@app.route('/editar_insumo/<int:id>/<int:insumo_id>', methods=['GET', 'POST'])
def editar_insumo(id, insumo_id):
    if "id_usuario" not in session:
        flash("Você precisa estar logado para acessar essa página", "error")
        return redirect(url_for('login'))

    cursor = con.cursor()
    try:
        cursor.execute(
            """
            SELECT ID_INSUMO, NOME, DESCRICAO, PESO_UNIDADE, (SELECT FIRST 1 PRECO_COMPRA 
                      FROM HISTORICO_PRECO 
                      WHERE HISTORICO_PRECO.ID_INSUMO = INSUMO.ID_INSUMO 
                      ORDER BY DATA_MUDANCA DESC), UNIDADE_DE_MEDIDA
              FROM INSUMO
             WHERE ID_INSUMO = ? AND ID_USUARIO = ?
            """,
            (insumo_id, id)
        )
        insumo = cursor.fetchone()

        if not insumo:
            flash('Insumo não encontrado.', 'error')
            return redirect(url_for('insumos', id=id))

        if request.method == 'POST':
            nome = request.form.get('nomeInsumo')
            descricao = request.form.get('descricao')
            peso_unidade = float(request.form.get('peso_unidade'))
            unidade_de_medida = int(request.form.get('unidade'))
            preco_compra = round(float(request.form.get('preco')), 2)

            try:
                if unidade_de_medida == 1 or unidade_de_medida == 3:
                    quantidade = float(peso_unidade * 1000)
                    preco_unidade = float(preco_compra / quantidade)
                else:
                    quantidade = float(peso_unidade)
                    preco_unidade = float(preco_compra) / quantidade

                cursor.execute(
                    """SELECT FIRST 1 PRECO_COMPRA 
                      FROM HISTORICO_PRECO 
                      WHERE ID_INSUMO = ? 
                      ORDER BY DATA_MUDANCA DESC                    
                    """,
                    (insumo_id,)
                )
                preco_compra_antigo = cursor.fetchone()

                if preco_compra_antigo != preco_compra or preco_compra_antigo == None:
                    cursor.execute(
                        """INSERT INTO HISTORICO_PRECO
                               (ID_INSUMO, PRECO_COMPRA, PRECO_UNIDADE)
                           VALUES (?, ?, ?)""",
                        (insumo_id, preco_compra, preco_unidade)
                    )
                    con.commit()
                cursor.execute(
                    """
                    UPDATE INSUMO
                       SET NOME = ?, DESCRICAO = ?, PESO_UNIDADE = ?, UNIDADE_DE_MEDIDA = ?
                     WHERE ID_INSUMO = ? AND ID_USUARIO = ?
                    """,
                    (nome, descricao, peso_unidade, unidade_de_medida, insumo_id, id)
                )

                con.commit()

                cursor.execute(
                    """
                    UPDATE ESTOQUE
                    SET QUANTIDADE = ?
                    WHERE ID_INSUMO = ?
                    """,
                    (quantidade, insumo_id)
                )
                con.commit()
                flash('Insumo atualizado com sucesso!', 'success')
                return redirect(url_for('insumos', id=id))
            except Exception as e:
                con.rollback()
                flash(f'Erro ao atualizar insumo: {e}', 'error')
                return redirect(url_for('editar_insumo', id=id, insumo_id=insumo_id))
            finally:
                cursor.close()
        return render_template('editar_Insumo.html', id=id, insumo_id=insumo_id, insumo=insumo)
    finally:
        cursor.close()


@app.route('/produtos/<int:id>')
def produtos(id):
    if "id_usuario" not in session:
        flash("Você precisa estar logado para acessar essa página", "error")
        return redirect(url_for('login'))
    return render_template('produtos.html', id=id)


@app.route('/cad_produto/<int:id>')
def cad_produto(id):
    if "id_usuario" not in session:
        flash("Você precisa estar logado para acessar essa página", "error")
        return redirect(url_for('login'))
    cursor = con.cursor()
    try:
        cursor.execute("SELECT ID_CATEGORIA_PRODUTOS, NOME FROM CATEGORIA_PRODUTOS WHERE ID_USUARIO = ?", (id,))
        categorias = cursor.fetchall()
        cursor.execute("""SELECT ID_INSUMO, NOME
        FROM INSUMO WHERE ID_USUARIO = ?""", (id,))
        insumos = cursor.fetchall()
        cursor.execute("""SELECT VALOR_MAO FROM EMPRESA WHERE ID_USUARIO = ?""", (id,))
        valor_mao = float(cursor.fetchone()[0])
        if 'insumos_utilizados' in session:
            insumos_utilizados = session['insumos_utilizados']
            session.pop('insumos_utilizados')
        else:
            insumos_utilizados = []
    finally:
        cursor.close()
        return render_template('cad_Produto.html', id=id, categorias=categorias, insumos=insumos, insumos_utilizados=insumos_utilizados, valor_mao=valor_mao)
@app.route('/cad_categoria/<int:id>', methods=['POST'])
def cad_categoria(id):
    if request.method == 'POST':
        nome = request.form['nomeCategoria'].capitalize()
        cursor = con.cursor()
        try:
            cursor.execute("SELECT NOME FROM CATEGORIA_PRODUTOS WHERE NOME = ? AND ID_USUARIO = ?", (nome, id,))
            if cursor.fetchone():
                flash('Categoria já cadastrado!')
                return redirect(url_for('cad_produto', id=id))
            cursor.execute(
                "INSERT INTO CATEGORIA_PRODUTOS (NOME, ID_USUARIO) "
                "VALUES (?, ?)",
                (nome, id,)
            )
            con.commit()
            flash('Categoria cadastrado com sucesso!', 'success')
            return redirect(url_for('cad_produto', id=id))
        except Exception as e:
            con.rollback()
            flash(f'Erro ao cadastrar: {e}')
            return redirect(url_for('cad_produto', id=id))
        finally:
            cursor.close()

@app.route('/adicionar_insumo/<int:id>', methods=['POST'])
def adicionar_insumo(id):
    if request.method == 'POST':
        id_insumos_utilizados = request.form.getlist('insumos_utilizados')
        insumos_utilizados = []

        cursor = con.cursor()
        for i in id_insumos_utilizados:
            quantidade = float(request.form.get(f'quantidade_{i}'))
            unidade_de_medida = int(request.form.get(f'unidade_de_medida_{i}'))
            cursor.execute('SELECT NOME FROM INSUMO WHERE ID_INSUMO = ?', (i,))
            nome = cursor.fetchone()[0]
            cursor.execute('SELECT PRECO_UNIDADE FROM HISTORICO_PRECO WHERE ID_INSUMO = ? ORDER BY DATA_MUDANCA DESC', (i,))
            preco_unidade = float(cursor.fetchone()[0])
            if unidade_de_medida == 1 or unidade_de_medida == 3:
                quantidade_convertida = quantidade * 1000
            else:
                quantidade_convertida = quantidade
            preco_total = float(preco_unidade * quantidade_convertida)
            insumos_utilizados.append({
                'id': int(i),
                'nome': nome,
                'quantidade': quantidade_convertida,
                'unidade_de_medida': int(unidade_de_medida),
                'preco_total': preco_total
            })
        cursor.close()
        session['insumos_utilizados'] = insumos_utilizados
        return redirect(url_for('cad_produto', id=id))
@app.route('/logout')
def logout():
    session.pop('id_usuario', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
