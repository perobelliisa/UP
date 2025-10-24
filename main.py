from flask import Flask, render_template, request, flash, url_for, redirect, session
import fdb
from flask_bcrypt import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'GuiIsaLuDuda'

host = 'localhost'
database = r'C:\Users\Guilherme kawanami\Documents\GitHub\UP\BANCO.FDB' #definir o caminho do banco de dados
user = 'SYSDBA'
password = 'sysdba'
con = fdb.connect(host=host, database=database, user=user, password=password)

def dados_usuario(id_usuario):
    cursor = con.cursor()
    try:
        cursor.execute('SELECT NOME FROM USUARIO WHERE ID_USUARIO = ?', (id_usuario,))
        usuario = cursor.fetchone()

        if not usuario:
            session.clear()
            flash('Sessão inválida. Faça login novamente.')
            return redirect(url_for('login'))

        nome_usuario = usuario[0]
        cursor.execute('SELECT NOME FROM EMPRESA WHERE ID_USUARIO = ?', (id_usuario,))
        empresa = cursor.fetchone()
        if not empresa:
            flash('Sessão inválida. Faça login novamente.')
            return redirect(url_for('login'))
        nome_empresa = empresa[0]
        return nome_usuario, nome_empresa
    except:
        session.clear()
        flash('Sessão inválida. Faça login novamente.')
        return redirect(url_for('login'))
    finally:
        cursor.close()

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/cadastro_pessoal', methods=['GET', 'POST'])
def cadastro_pessoal():
    # Se já estiver logado, impede novo cadastro
    if 'id_usuario' in session:
        flash('Faça logout para cadastrar outra conta.')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        nome = request.form.get('nome').strip()
        sobrenome = request.form.get('sobrenome').strip()
        email = request.form.get('email').strip().lower()
        cpf = request.form.get('cpf').strip()
        telefone = request.form.get('telefone').strip()
        senha = request.form.get('senha')

        senha_cripto = generate_password_hash(senha)

        cursor = con.cursor()
        try:
            cursor.execute('SELECT 1 FROM USUARIO WHERE EMAIL = ?', (email,))
            if cursor.fetchone():
                flash('Este e-mail já está cadastrado.')
                return render_template('cadastro_pessoal.html')

            cursor.execute('SELECT 1 FROM USUARIO WHERE CPF = ?', (cpf,))
            if cursor.fetchone():
                flash('Este CPF já está cadastrado.')
                return render_template('cadastro_pessoal.html')

            cursor.execute(
                '''
                INSERT INTO USUARIO (NOME, SOBRENOME, EMAIL, CPF, TELEFONE, SENHA)
                VALUES (?, ?, ?, ?, ?, ?)
                ''',
                (nome, sobrenome, email, cpf, telefone, senha_cripto)
            )
            con.commit()

            session['email_pendente'] = email
            flash('Usuário cadastrado com sucesso!', 'success')
            return redirect(url_for('cadastro_empresa'))
        except:
            flash(f'Ocorreu um erro ao cadastrar', 'error')
            return render_template('cadastro_pessoal.html')
        finally:
            cursor.close()
    return render_template('cadastro_pessoal.html')


@app.route('/cadastro_empresa', methods=['GET', 'POST'])
def cadastro_empresa():
    email = session.get('email_pendente')
    if not email:
        flash('Não foi possível identificar o usuário. Refaça o cadastro.')
        return redirect(url_for('cadastro_pessoal'))

    if request.method == 'POST':
        nome_empresa = request.form.get('nome_empresa').strip()
        endereco = request.form.get('endereco').strip()
        cnpj = request.form.get('cnpj').strip()
        tipo = request.form.get('tipo').strip()
        valor = request.form.get('valor').strip()

        cursor = con.cursor()
        try:
            cursor.execute("SELECT 1 FROM EMPRESA WHERE CNPJ = ?", (cnpj,))
            if cursor.fetchone():
                flash('CNPJ já cadastrado!')
                return render_template('cadastro_empresa.html')

            cursor.execute("SELECT ID_USUARIO FROM USUARIO WHERE EMAIL = ?", (email,))
            usuario = cursor.fetchone()
            if not usuario:
                flash('Usuário não encontrado. Refaça o cadastro.')
                return redirect(url_for('cadastro_pessoal'))

            id_usuario = usuario[0]

            cursor.execute(
                '''
                INSERT INTO EMPRESA (NOME, ENDERECO, CNPJ, TIPO, VALOR_MAO, ID_USUARIO)
                VALUES (?, ?, ?, ?, ?, ?)
                ''',
                (nome_empresa, endereco, cnpj, tipo, valor, id_usuario)
            )
            con.commit()

            session.pop('email_pendente', None)
            flash('Empresa cadastrada com sucesso!', 'success')
            return redirect(url_for('login'))
        except:
            flash(f'Erro ao cadastrar empresa', 'error')
            return render_template('cadastro_empresa.html')
        finally:
            cursor.close()
    return render_template('cadastro_empresa.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email').strip().lower()
        senha = request.form.get('senha')

        cursor = con.cursor()
        try:
            cursor.execute('SELECT ID_USUARIO, SENHA FROM USUARIO WHERE EMAIL = ?', (email,))
            usuario = cursor.fetchone()
            if not usuario:
                flash('Email ou senha inválidos.')
                return render_template('login.html')

            id_usuario, senha_hash = usuario

            if not check_password_hash(senha_hash, senha):
                flash('Email ou senha inválidos.')
                return render_template('login.html')

            cursor.execute('SELECT NOME FROM EMPRESA WHERE ID_USUARIO = ?', (id_usuario,))
            empresa = cursor.fetchone()
            if not empresa:
                flash('Termine o cadastro da sua empresa primeiro.')
                return redirect(url_for('cadastro_empresa'))

            session['id_usuario'] = id_usuario
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('dashboard'))

        finally:
            cursor.close()

    return render_template('login.html')



@app.route('/conta')
def conta():
    # Se o usuário estiver logado, vai para o dashboard, caso contrário, vai para login ao clicar em "Conta"
    if 'id_usuario' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'id_usuario' not in session:
        flash('Faça login para continuar.')
        return redirect(url_for('login'))
    id_usuario = session['id_usuario']
    nome_usuario, nome_empresa = dados_usuario(id_usuario)

    return render_template('dashboard.html', nome_usuario=nome_usuario, nome_empresa=nome_empresa, id_usuario=id_usuario)


@app.route("/config")
def config():
    if 'id_usuario' not in session:
        flash('Faça login para continuar.')
        return redirect(url_for('login'))

    id_usuario = session['id_usuario']

    nome_usuario, nome_empresa = dados_usuario(id_usuario)

    cursor = con.cursor()
    try:
        cursor.execute('SELECT NOME, TIPO FROM EMPRESA WHERE ID_USUARIO = ?', (session['id_usuario'],))        empresa = cursor.fetchone()
        if not empresa:
            flash("Empresa não encontrada.")
            return redirect(url_for('dashboard'))
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

    return render_template('config.html', nome_usuario=nome_usuario, nome_empresa=nome_empresa, tipo=tipo)
@app.route('/editar_usuario', methods=['GET', 'POST'])
def editar_usuario():
    if "id_usuario" not in session:
        flash("Você precisa estar logado para acessar essa página", "error")
        return redirect(url_for('login'))

    id_usuario = session['id_usuario']
    cursor = con.cursor()

    if request.method == 'POST':
        nome      = request.form['nome']
        sobrenome = request.form['sobrenome']
        email     = request.form['email']
        cpf       = request.form['cpf']
        telefone  = request.form['telefone']
        senha     = request.form['senha']

        nomeEmp     = request.form['nomeEmp']
        endereco  = request.form['endereco']
        cnpj      = request.form['cnpj']
        tipo      = request.form['tipo']
        valor     = request.form['valor']

        try:
            cursor.execute(
                "SELECT 1 FROM USUARIO WHERE EMAIL = ? AND ID_USUARIO != ?", (email, id_usuario)
            )
            if cursor.fetchone():
                flash('Email já cadastrado!')
                return render_template('editar_usuario.html', usuario=usuario, empresa=empresa)

            cursor.execute(
                "SELECT 1 FROM USUARIO WHERE CPF = ? AND ID_USUARIO != ?", (cpf, id_usuario)
            )
            if cursor.fetchone():
                flash('CPF já cadastrado!')
                return render_template('editar_usuario.html', usuario=usuario, empresa=empresa)

            if senha:
                senha_cripto = generate_password_hash(senha)
                cursor.execute("""
                    UPDATE USUARIO
                       SET NOME = ?, SOBRENOME = ?, EMAIL = ?, CPF = ?, TELEFONE = ?, SENHA = ?
                     WHERE ID_USUARIO = ?
                """, (nome, sobrenome, email, cpf, telefone, senha_cripto, id_usuario))
            else:
                cursor.execute("""
                    UPDATE USUARIO
                       SET NOME = ?, SOBRENOME = ?, EMAIL = ?, CPF = ?, TELEFONE = ?
                     WHERE ID_USUARIO = ?
                """, (nome, sobrenome, email, cpf, telefone, id_usuario))

            cursor.execute("""
                UPDATE EMPRESA
                   SET NOME = ?, ENDERECO = ?, CNPJ = ?, TIPO = ?, VALOR_MAO = ?
                 WHERE ID_USUARIO = ?
            """, (nomeEmp, endereco, cnpj, tipo, valor, id_usuario))

            con.commit()
            flash("Usuário atualizado com sucesso", "success")
            cursor.close()
            return redirect(url_for('dashboard'))

        except:
            flash(f"Erro ao atualizar:", "error")
            return redirect(url_for('editar_usuario'))

        finally:
            cursor.close()

    try:
        cursor.execute("""
                       SELECT NOME, SOBRENOME, EMAIL, CPF, TELEFONE, SENHA
                       FROM USUARIO
                       WHERE ID_USUARIO = ?
                       """, (id_usuario,))
        usuario = cursor.fetchone()

        if not usuario:
            cursor.close()
            flash("Usuário não foi encontrado")
            return redirect(url_for('dashboard'))

        cursor.execute("""
                       SELECT NOME, ENDERECO, CNPJ, TIPO, VALOR_MAO
                       FROM EMPRESA
                       WHERE ID_USUARIO = ?
                       """, (id_usuario,))

        empresa = cursor.fetchone()

    finally:
        cursor.close()

    return render_template('editar_usuario.html', usuario=usuario, empresa=empresa)

@app.route('/insumos')
def insumos():
    if "id_usuario" not in session:
        flash("Você precisa estar logado para acessar essa página", "error")
        return redirect(url_for('login'))

    id_usuario = session['id_usuario']

    cursor = con.cursor()
    try:
        cursor.execute("""
            SELECT ID_INSUMO
                 , NOME
                 , DESCRICAO
                 , (
                        SELECT FIRST 1 PRECO_COMPRA 
                        FROM HISTORICO_PRECO 
                        WHERE HISTORICO_PRECO.ID_INSUMO = INSUMO.ID_INSUMO 
                        ORDER BY DATA_MUDANCA DESC
                   )
                 , CASE UNIDADE_DE_MEDIDA
                       WHEN 1 THEN 'Quilo'
                       WHEN 2 THEN 'Grama'
                       WHEN 3 THEN 'Litro'
                       WHEN 4 THEN 'Mililitro'
                       WHEN 5 THEN 'Unidade'
                       ELSE ''
                   END AS DESCRICAO_UNIDADE
                 , PESO_UNIDADE 
            FROM INSUMO 
            WHERE ID_USUARIO = ?
        """, (id_usuario,))
        insumos = cursor.fetchall()
        nome_usuario, nome_empresa = dados_usuario(id_usuario)
    except:
        flash(f"Ocorreu um erro ao carregar os insumos", "error")
        return redirect(url_for('dashboard'))
    finally:
        cursor.close()

    return render_template('insumos.html', insumos=insumos, nome_usuario=nome_usuario, nome_empresa=nome_empresa)

@app.route('/cadastro_insumo', methods=['GET', 'POST'])
def cadastro_insumo():
    if "id_usuario" not in session:
        flash("Você precisa estar logado para acessar essa página", "error")
        return redirect(url_for('login'))

    id_usuario = session['id_usuario']

    if request.method == 'POST':
        nome = request.form['nomeInsumo'].strip().capitalize()
        descricao = request.form['descricao'].strip()
        peso_unidade = float(request.form['peso_unidade'])
        unidade_de_medida = int(request.form['unidade'])
        preco_compra = round(float(request.form.get('preco')), 2)

        cursor = con.cursor()
        try:
            cursor.execute(
                "SELECT 1 FROM INSUMO WHERE NOME = ? AND ID_USUARIO = ?",
                (nome, id_usuario)
            )
            if cursor.fetchone():
                flash('Insumo já cadastrado!')
                return render_template('cadastro_insumo.html')

            if unidade_de_medida == 1 or unidade_de_medida == 3:  # quilo ou litro
                quantidade = peso_unidade * 1000
            else:
                quantidade = peso_unidade
            preco_unidade = preco_compra / quantidade

            cursor.execute(
                "INSERT INTO INSUMO (NOME, DESCRICAO, PESO_UNIDADE, UNIDADE_DE_MEDIDA, ID_USUARIO) VALUES (?, ?, ?, ?, ?)",
                (nome, descricao, peso_unidade, unidade_de_medida, id_usuario)
            )
            con.commit()

            cursor.execute(
                "SELECT ID_INSUMO FROM INSUMO WHERE NOME = ? AND ID_USUARIO = ?",
                (nome, id_usuario)
            )

            id_insumo = cursor.fetchone()[0]

            cursor.execute(
                "INSERT INTO HISTORICO_PRECO (ID_INSUMO, PRECO_COMPRA, PRECO_UNIDADE) VALUES (?, ?, ?)",
                (id_insumo, preco_compra, preco_unidade)
            )
            cursor.execute(
                "INSERT INTO ESTOQUE (ID_INSUMO, QUANTIDADE) VALUES (?, ?)",
                (id_insumo, quantidade)
            )
            con.commit()

            flash('Insumo cadastrado com sucesso!', 'success')
            return redirect(url_for('insumos'))

        except:
            flash(f'Erro ao cadastrar esse insumo', 'error')
            return render_template('cadastro_insumo.html')
        finally:
            cursor.close()

    nome_usuario, nome_empresa = dados_usuario(id_usuario)
    return render_template('cadastro_insumo.html', nome_usuario=nome_usuario, nome_empresa=nome_empresa)

@app.route('/editar_insumo', methods=['GET', 'POST'])
def editar_insumo():
        if "id_usuario" not in session:
            flash("Você precisa estar logado para acessar essa página", "error")
            return redirect(url_for('login'))

        id_usuario = session['id_usuario']

        cursor = con.cursor()
        try:
            cursor.execute("""
                           SELECT ID_INSUMO,
                                  NOME,
                                  DESCRICAO,
                                  PESO_UNIDADE,
                                  (SELECT FIRST 1 PRECO_COMPRA
                           FROM HISTORICO_PRECO
                           WHERE HISTORICO_PRECO.ID_INSUMO = INSUMO.ID_INSUMO
                           ORDER BY DATA_MUDANCA DESC), UNIDADE_DE_MEDIDA
                           FROM INSUMO
                           WHERE ID_USUARIO = ?
                           """, (id_usuario,))
            insumo = cursor.fetchone()

            if not insumo:
                flash('Nenhum insumo encontrado.', 'error')
                return redirect(url_for('insumos'))

            if request.method == 'POST':
                nome = request.form['nomeInsumo'].strip()
                descricao = request.form['descricao'].strip()
                peso_unidade = float(request.form['peso_unidade'])
                unidade_de_medida = int(request.form['unidade'])
                preco_compra = float(request.form['preco'])

                cursor.execute(
                    "SELECT 1 FROM INSUMO WHERE UPPER(NOME) = UPPER(?) AND ID_USUARIO = ? AND ID_INSUMO <> ?",
                    (nome, id_usuario, insumo[0])
                )
                if cursor.fetchone():
                    flash('Insumo já cadastrado!')
                    return redirect(url_for('editar_insumo'))

                if unidade_de_medida == 1 or unidade_de_medida == 3:  # quilo ou litro
                    quantidade = peso_unidade * 1000
                else:
                    quantidade = peso_unidade
                preco_unidade = preco_compra / quantidade

                cursor.execute(
                    "SELECT FIRST 1 PRECO_COMPRA FROM HISTORICO_PRECO WHERE ID_INSUMO = ? ORDER BY DATA_MUDANCA DESC",
                    (insumo[0],)
                )
                preco_registrado = cursor.fetchone()

                preco_antigo = preco_registrado[0]

                if preco_antigo is None or preco_antigo != preco_compra:
                    cursor.execute(
                        "INSERT INTO HISTORICO_PRECO (ID_INSUMO, PRECO_COMPRA, PRECO_UNIDADE) VALUES (?, ?, ?)",
                        (insumo[0], preco_compra, preco_unidade)
                    )

                cursor.execute(
                    "UPDATE INSUMO SET NOME=?, DESCRICAO=?, PESO_UNIDADE=?, UNIDADE_DE_MEDIDA=? WHERE ID_INSUMO=? AND ID_USUARIO=?",
                    (nome, descricao, peso_unidade, unidade_de_medida, insumo[0], id_usuario)
                )

                cursor.execute(
                    "UPDATE ESTOQUE SET QUANTIDADE=? WHERE ID_INSUMO=?",
                    (quantidade, insumo[0])
                )
                con.commit()
                flash('Insumo atualizado com sucesso!', 'success')
                return redirect(url_for('insumos'))

            nome_usuario, nome_empresa = dados_usuario(id_usuario)
            return render_template('editar_insumo.html', insumo=insumo, nome_usuario=nome_usuario,
                                   nome_empresa=nome_empresa)
        except:
            flash(f'Erro ao atualizar o insumo', 'error')
            return redirect(url_for('editar_insumo'))
        finally:
            cursor.close()

@app.route('/historico_insumo/<int:id>/<int:insumo_id>')
def historico_insumo(id, insumo_id):
    if "id_usuario" not in session:
        flash("Voc\u01e6 precisa estar logado para acessar essa p\u01edgina", "error")
        return redirect(url_for('login'))

    cursor = con.cursor()
    try:
        cursor.execute(
            """
            SELECT ID_INSUMO, NOME, DESCRICAO, UNIDADE_DE_MEDIDA, PESO_UNIDADE
              FROM INSUMO
             WHERE ID_INSUMO = ? AND ID_USUARIO = ?
            """,
            (insumo_id, id)
        )
        insumo = cursor.fetchone()
        if not insumo:
            flash('Insumo n\u01dc o encontrado.', 'error')
            return redirect(url_for('insumos', id=id))

        cursor.execute(
            """
            SELECT PRECO_COMPRA, PRECO_UNIDADE, DATA_MUDANCA
              FROM HISTORICO_PRECO
             WHERE ID_INSUMO = ?
             ORDER BY DATA_MUDANCA DESC
            """,
            (insumo_id,)
        )
        historico = cursor.fetchall()
    finally:
        cursor.close()

    # Mapeia unidade para r\u00f3tulo amig\u00e1vel
    unidade = insumo[3]
    if unidade == 1:
        unidade_label = 'Grama (custo por g)'
    elif unidade == 2:
        unidade_label = 'Grama'
    elif unidade == 3:
        unidade_label = 'Mililitro (custo por ml)'
    elif unidade == 4:
        unidade_label = 'Mililitro'
    elif unidade == 5:
        unidade_label = 'Unidade'
    else:
        unidade_label = ''

    nome, nome_empresa = info(id)
    return render_template(
        'historico_Insumo.html',
        id=id,
        insumo_id=insumo_id,
        insumo=insumo,
        unidade_label=unidade_label,
        historico=historico,
        nome=nome,
        nome_empresa=nome_empresa
    )

@app.route('/deletar_insumo/<int:id_insumo>', methods=['POST'])
def deletar_insumo(id_insumo):
    if "id_usuario" not in session:
        flash("Você precisa estar logado para acessar essa página", "error")
        return redirect(url_for('login'))

    id_usuario = session['id_usuario']
    cursor = con.cursor()
    try:
        cursor.execute(
            "SELECT 1 FROM INSUMO WHERE ID_INSUMO = ? AND ID_USUARIO = ?",
            (id_insumo, id_usuario)
        )
        if not cursor.fetchone():
            flash('Insumo não encontrado.', 'error')
            return redirect(url_for('insumos'))

        cursor.execute("DELETE FROM ESTOQUE WHERE ID_INSUMO = ?", (id_insumo,))
        cursor.execute("DELETE FROM HISTORICO_PRECO WHERE ID_INSUMO = ?", (id_insumo,))

        cursor.execute(
            "DELETE FROM INSUMO WHERE ID_INSUMO = ? AND ID_USUARIO = ?",
            (id_insumo, id_usuario)
        )

        con.commit()
        flash('Insumo deletado com sucesso!', 'success')
    except Exception:
        flash(f'Erro ao deletar insumo', 'error')
    finally:
        cursor.close()
        return redirect(url_for('insumos'))
@app.route('/produtos')
def produtos():
    if "id_usuario" not in session:
        flash("Você precisa estar logado para acessar essa página", "error")
        return redirect(url_for('login'))

    id_usuario = session['id_usuario']
    nome_usuario, nome_empresa = dados_usuario(id_usuario)

    return render_template('produtos.html', nome_usuario=nome_usuario, nome_empresa=nome_empresa)

# PAREI AQUI
@app.route('/cad_produto/<int:id>', methods=['GET', 'POST'])
def cad_produto(id):
    if "id_usuario" not in session:
        flash("Você precisa estar logado para acessar essa página", "error")
        return redirect(url_for('login'))

    cursor = con.cursor()
    try:
        if request.method == 'POST':
            nome = request.form.get('nomeProduto')
            descricao = request.form.get('descricao')
            categoria = int(request.form.get('categoria'))
            tempoProducao = float(request.form.get('tempoProducao'))
            lucro = round(float(request.form.get('lucro')), 2)
            insumos_utilizados = request.form.getlist('insumos_utilizados')

            print(insumos_utilizados)

            if len(insumos_utilizados) < 1:
                flash("É necessário adicionar insumos", "error")
                return redirect(url_for('produtos', id=id))

            for i in insumos_utilizados:
                cursor.execute("SELECT QUANTIDADE FROM ESTOQUE WHERE ID_INSUMO = ?", (i[0],))
                quantidade = cursor.fetchone()
                print(quantidade)

        cursor.execute("SELECT ID_CATEGORIA_PRODUTOS, NOME FROM CATEGORIA_PRODUTOS WHERE ID_USUARIO = ?", (id,))
        categorias = cursor.fetchall()

        cursor.execute("SELECT ID_INSUMO, NOME FROM INSUMO WHERE ID_USUARIO = ?", (id,))
        insumos = cursor.fetchall()

        cursor.execute("SELECT VALOR_MAO FROM EMPRESA WHERE ID_USUARIO = ?", (id,))
        valor_mao = float(cursor.fetchone()[0])

        if 'insumos_utilizados' in session:
            insumos_utilizados = session.get('insumos_utilizados')
            session.pop('insumos_utilizados')
        else:
            insumos_utilizados = ''

        print('oi', insumos_utilizados)
    finally:
        cursor.close()

    nome, nome_empresa = info(id)

    return render_template('cadastro_produto.html',
                           id=id,
                           categorias=categorias,
                           insumos=insumos,
                           insumos_utilizados=insumos_utilizados,
                           valor_mao=valor_mao, nome=nome, nome_empresa=nome_empresa)

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

