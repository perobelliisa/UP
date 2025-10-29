from flask import Flask, render_template, request, flash, url_for, redirect, session
import fdb
from flask_bcrypt import generate_password_hash, check_password_hash
from fpdf import FPDF
from flask import send_file

app = Flask(__name__)
app.secret_key = 'GuiIsaLuDuda'

host = 'localhost'
database = r'C:\Users\Guilherme kawanami\OneDrive\Desktop\UP1.1\UP1.1\BANCO.FDB' #definir o caminho do banco de dados
user = 'SYSDBA'
password = 'sysdba'
con = fdb.connect(host=host, database=database, user=user, password=password)

def info(id):
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
    cursor.close()
    return nome, empresa

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

    nome, nome_empresa = info(id)

    return render_template('dashboard.html', nome=nome, nome_empresa=nome_empresa, id=id)


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
        cursor.execute('SELECT NOME, TIPO FROM EMPRESA WHERE ID_USUARIO = ?', (session['id_usuario'],))

        empresa = cursor.fetchone()
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

    nome, nome_empresa = info(id)

    return render_template('insumos.html', id=id, insumos=insumos, nome=nome, nome_empresa=nome_empresa)

@app.route('/cad_insumo/<int:id>', methods=['GET', 'POST'])
def cad_insumo(id):
    if "id_usuario" not in session:
        flash("Você precisa estar logado para acessar essa página", "error")
        return redirect(url_for('login'))
    if request.method == 'POST':
        nome = request.form['nomeInsumo'].strip().capitalize()
        descricao = request.form['descricao'].strip()
        try:
            peso_unidade = float(request.form['peso_unidade'])
        except Exception:
            flash('Quantidade inválida.')
            return render_template('cad_Insumo.html', id=id)
        try:
            unidade_de_medida = int(request.form['unidade'])
        except Exception:
            flash('Unidade de medida inválida.')
            return render_template('cad_Insumo.html', id=id)
        try:
            preco_compra = round(float(request.form.get('preco')), 2)
        except Exception:
            flash('Preço de compra inválido.')
            return render_template('cad_Insumo.html', id=id)

        # Validações de regra de negócio
        if not nome:
            flash('Nome do insumo é obrigatório.')
            return render_template('cad_Insumo.html', id=id)
        if unidade_de_medida not in (1, 2, 3, 4, 5):
            flash('Unidade de medida inválida.')
            return render_template('cad_Insumo.html', id=id)
        if peso_unidade <= 0:
            flash('A quantidade deve ser maior que zero.')
            return render_template('cad_Insumo.html', id=id)
        if preco_compra <= 0:
            flash('O preço de compra deve ser maior que zero.')
            return render_template('cad_Insumo.html', id=id)

        cursor = con.cursor()
        try:
            cursor.execute("SELECT 1 FROM INSUMO WHERE UPPER(NOME) = UPPER(?) AND ID_USUARIO = ?", (nome, id,))
            if cursor.fetchone():
                flash('Insumo já cadastrado!')
                return render_template('cad_Insumo.html', id=id)
            if unidade_de_medida == 1 or unidade_de_medida == 3:
                quantidade = float(peso_unidade * 1000)
                preco_unidade = float(preco_compra / quantidade)
            else:
                quantidade = float(peso_unidade)
                preco_unidade = float(preco_compra / quantidade)

            if preco_unidade <= 0:
                flash('O custo unitário deve ser maior que zero.')
                return render_template('cad_Insumo.html', id=id)


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
    nome, nome_empresa = info(id)

    return render_template('cad_Insumo.html', id=id, nome=nome, nome_empresa=nome_empresa)


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
            nome = (request.form.get('nomeInsumo') or '').strip()
            descricao = (request.form.get('descricao') or '').strip()
            try:
                # Checagem case-insensitive de nome duplicado por usuário (exclui o próprio)
                cursor.execute(
                    "SELECT 1 FROM INSUMO WHERE UPPER(NOME) = UPPER(?) AND ID_USUARIO = ? AND ID_INSUMO <> ?",
                    (nome, id, insumo_id)
                )
                if cursor.fetchone():
                    flash('Insumo já cadastrado!')
                    return redirect(url_for('editar_insumo', id=id, insumo_id=insumo_id))
                peso_unidade = float(request.form.get('peso_unidade'))
            except Exception:
                flash('Quantidade inválida.')
                return redirect(url_for('editar_insumo', id=id, insumo_id=insumo_id))
            try:
                unidade_de_medida = int(request.form.get('unidade'))
            except Exception:
                flash('Unidade de medida inválida.')
                return redirect(url_for('editar_insumo', id=id, insumo_id=insumo_id))
            try:
                preco_compra = round(float(request.form.get('preco')), 2)
            except Exception:
                flash('Preço de compra inválido.')
                return redirect(url_for('editar_insumo', id=id, insumo_id=insumo_id))

            if not nome:
                flash('Nome do insumo é obrigatório.')
                return redirect(url_for('editar_insumo', id=id, insumo_id=insumo_id))
            if unidade_de_medida not in (1, 2, 3, 4, 5):
                flash('Unidade de medida inválida.')
                return redirect(url_for('editar_insumo', id=id, insumo_id=insumo_id))
            if peso_unidade <= 0:
                flash('A quantidade deve ser maior que zero.')
                return redirect(url_for('editar_insumo', id=id, insumo_id=insumo_id))
            if preco_compra <= 0:
                flash('O preço de compra deve ser maior que zero.')
                return redirect(url_for('editar_insumo', id=id, insumo_id=insumo_id))

            try:
                if unidade_de_medida == 1 or unidade_de_medida == 3:
                    quantidade = float(peso_unidade * 1000)
                    preco_unidade = float(preco_compra / quantidade)
                else:
                    quantidade = float(peso_unidade)
                    preco_unidade = float(preco_compra) / quantidade

                if preco_unidade <= 0:
                    flash('O custo unitário deve ser maior que zero.')
                    return redirect(url_for('editar_insumo', id=id, insumo_id=insumo_id))

                cursor.execute(
                    """SELECT FIRST 1 PRECO_COMPRA 
                      FROM HISTORICO_PRECO 
                      WHERE ID_INSUMO = ? 
                      ORDER BY DATA_MUDANCA DESC                    
                    """,
                    (insumo_id,)
                )
                preco = cursor.fetchone()
                preco_compra_antigo = None

                if preco:
                    preco_compra_antigo = round(float(preco[0]), 2)

                if preco_compra_antigo is None or preco_compra_antigo != preco_compra:
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
        nome, nome_empresa = info(id)
        return render_template('editar_Insumo.html', id=id, insumo_id=insumo_id, insumo=insumo, nome=nome, nome_empresa=nome_empresa)
    finally:
        cursor.close()


@app.route('/historico_insumo/<int:id>/<int:insumo_id>')
def historico_insumo(id, insumo_id):
    if "id_usuario" not in session:
        flash("Você precisa estar logado para acessar essa página", "error")
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

@app.route('/deletar_insumo/<int:id>/<int:insumo_id>', methods=['POST'])
def deletar_insumo(id, insumo_id):
    if "id_usuario" not in session:
        flash("Você precisa estar logado para acessar essa página", "error")
        return redirect(url_for('login'))

    cursor = con.cursor()
    try:
        cursor.execute(
            """
            SELECT 1 FROM INSUMO WHERE ID_INSUMO = ? AND ID_USUARIO = ?
            """,
            (insumo_id, id)
        )
        if not cursor.fetchone():
            flash('Insumo não encontrado.', 'error')
            return redirect(url_for('insumos', id=id))

        cursor.execute(
            """
            SELECT 1
            FROM PRODUTO_INSUMO pi
            JOIN PRODUTO p ON p.ID_PRODUTO = pi.ID_PRODUTO
            WHERE pi.ID_INSUMO = ? AND p.ID_USUARIO = ?
            """,
            (insumo_id, id)
        )
        if cursor.fetchone():
            flash('Não é possível excluir um insumo utilizado em produtos ativos.', 'error')
            return redirect(url_for('insumos', id=id))

        cursor.execute("DELETE FROM ESTOQUE WHERE ID_INSUMO = ?", (insumo_id,))
        cursor.execute("DELETE FROM HISTORICO_PRECO WHERE ID_INSUMO = ?", (insumo_id,))
        con.commit()

        cursor.execute(
            "DELETE FROM INSUMO WHERE ID_INSUMO = ? AND ID_USUARIO = ?",
            (insumo_id, id)
        )
        con.commit()

        flash('Insumo deletado com sucesso!', 'success')
    except Exception as e:
        con.rollback()
        flash(f'Erro ao deletar insumo: {e}', 'error')
    finally:
        cursor.close()
    return redirect(url_for('insumos', id=id))

@app.route('/produtos/<int:id>')
def produtos(id):
    if "id_usuario" not in session:
        flash("Você precisa estar logado para acessar essa página", "error")
        return redirect(url_for('login'))
    nome, nome_empresa = info(id)

    cursor = con.cursor()
    try:
        cursor.execute(
            """
            SELECT
                p.ID_PRODUTO,
                p.NOME,
                COALESCE(c.NOME, 'Sem categoria') AS NOME_CATEGORIA,
                p.VALOR_TOTAL_CUSTO,
                p.VALOR_TOTAL_FINAL
            FROM PRODUTO p
            LEFT JOIN CATEGORIA_PRODUTOS c
                ON c.ID_CATEGORIA_PRODUTOS = p.ID_CATEGORIA
            WHERE p.ID_USUARIO = ?
            ORDER BY p.NOME
            """,
            (id,)
        )

        produtos = []
        for produto in cursor.fetchall():
            
            custo_val = produto[3]
            preco_val = produto[4]
            
            if custo_val is None:
                custo_val = 0.0
            if preco_val is None:
                preco_val = 0.0
                
            custo = float(custo_val)
            preco = float(preco_val)

            produtos.append({
                'id': produto[0],
                'nome': produto[1],
                'categoria': produto[2] or 'Sem categoria',
                'custo': custo,
                'preco': preco,
                'lucro': preco - custo
            })
    finally:
        cursor.close()

    return render_template('produtos.html',
                           id=id,
                           nome=nome,
                           nome_empresa=nome_empresa,
                           produtos=produtos)


@app.route('/cad_produto/<int:id>', methods=['GET', 'POST'])
def cad_produto(id):
    if "id_usuario" not in session:
        flash("Você precisa estar logado para acessar essa página", "error")
        return redirect(url_for('login'))

    cursor = con.cursor()
    try:
        if request.method == 'POST':
            # Pega os dados do formulário
            nome = request.form.get('nomeProduto', '').strip().capitalize()
            descricao = request.form.get('descricao', '').strip()
            categoria = int(request.form.get('categoria', 0))
            rendimento = int(request.form.get('rendimento', 1))
            # Tempo produção convertido para inteiro (de float para compatibilidade com banco)
            tempo_producao = int(float(request.form.get('tempoProducao', 0)))
            lucro_percentual = float(request.form.get('lucro', 0))

            # Pega os insumos da sessão
            insumos_utilizados = session.get('insumos_utilizados', [])

            # Validações básicas
            if not nome:
                flash('Nome do produto é obrigatório.', 'error')
                return redirect(url_for('cad_produto', id=id))

            if len(insumos_utilizados) < 1:
                flash("É necessário adicionar pelo menos um insumo", "error")
                return redirect(url_for('cad_produto', id=id))

            if tempo_producao <= 0:
                flash('Tempo de produção deve ser maior que zero.', 'error')
                return redirect(url_for('cad_produto', id=id))

            if rendimento <= 0:
                flash('Rendimento deve ser maior que zero.', 'error')
                return redirect(url_for('cad_produto', id=id))

            try:
                # Verifica se já existe produto com esse nome para o usuário
                cursor.execute(
                    "SELECT 1 FROM PRODUTO WHERE UPPER(NOME) = UPPER(?) AND ID_USUARIO = ?",
                    (nome, id)
                )
                if cursor.fetchone():
                    flash('Produto já cadastrado!', 'error')
                    return redirect(url_for('cad_produto', id=id))

                # Calcula o custo total dos insumos
                custo_insumos = sum(float(insumo['preco_total']) for insumo in insumos_utilizados)

                # Busca o valor da mão de obra
                cursor.execute("SELECT VALOR_MAO FROM EMPRESA WHERE ID_USUARIO = ?", (id,))
                valor_mao_obra = float(cursor.fetchone()[0])

                # Calcula custo de mão de obra
                custo_mao_obra = valor_mao_obra * tempo_producao

                # Calcula custo total e preço de venda
                custo_total = custo_insumos + custo_mao_obra
                preco_venda = custo_total * (1 + (lucro_percentual / 100))

                # 1. Insere o produto
                if categoria == 0:
                    cursor.execute(
                        """INSERT INTO PRODUTO
                           (NOME, DESCRICAO, RENDIMENTO, TEMPO_PRODUCAO,
                            VALOR_TOTAL_CUSTO, VALOR_TOTAL_FINAL, VALOR_PERC_LUCRO, ID_USUARIO)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                        (nome, descricao, rendimento, tempo_producao,
                         custo_total, preco_venda, lucro_percentual, id)
                    )
                else:
                    cursor.execute(
                        """INSERT INTO PRODUTO
                           (NOME, DESCRICAO, ID_CATEGORIA, RENDIMENTO, TEMPO_PRODUCAO,
                            VALOR_TOTAL_CUSTO, VALOR_TOTAL_FINAL, VALOR_PERC_LUCRO, ID_USUARIO)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        (nome, descricao, categoria, rendimento, tempo_producao,
                         custo_total, preco_venda, lucro_percentual, id)
                    )

                con.commit()

                # 2. Busca o ID do produto recém inserido
                cursor.execute(
                    """SELECT FIRST 1 ID_PRODUTO
                       FROM PRODUTO
                       WHERE NOME = ? AND ID_USUARIO = ?
                       ORDER BY ID_PRODUTO DESC""",
                    (nome, id)
                )
                id_produto = cursor.fetchone()[0]

                # 3. Insere os relacionamentos na tabela PRODUTO_INSUMO
                for insumo in insumos_utilizados:
                    cursor.execute(
                        """INSERT INTO PRODUTO_INSUMO
                               (ID_PRODUTO, ID_INSUMO, QUANTIDADE, VALOR_CUSTO)
                           VALUES (?, ?, ?, ?)""",
                        (
                            int(id_produto),
                            int(insumo['id']),
                            float(insumo['quantidade']),
                            float(insumo['preco_total'])
                        )
                    )

                con.commit()

                # Limpa os insumos da sessão
                session.pop('insumos_utilizados', None)

                flash('Produto cadastrado com sucesso!', 'success')
                return redirect(url_for('produtos', id=id))

            except Exception as e:
                con.rollback()
                flash(f'Erro ao cadastrar produto: {e}', 'error')
                return redirect(url_for('cad_produto', id=id))

        # GET - Carrega os dados para o formulário
        cursor.execute(
            "SELECT ID_CATEGORIA_PRODUTOS, NOME FROM CATEGORIA_PRODUTOS WHERE ID_USUARIO = ?",
            (id,)
        )
        categorias = cursor.fetchall()

        cursor.execute("SELECT ID_INSUMO, NOME FROM INSUMO WHERE ID_USUARIO = ?", (id,))
        insumos = cursor.fetchall()

        cursor.execute("SELECT VALOR_MAO FROM EMPRESA WHERE ID_USUARIO = ?", (id,))
        valor_mao_result = cursor.fetchone()
        valor_mao = float(valor_mao_result[0]) if valor_mao_result else 0.0

        # Pega os insumos da sessão se existirem
        insumos_utilizados = session.get('insumos_utilizados', [])

    finally:
        cursor.close()

    nome, nome_empresa = info(id)

    return render_template('cad_Produto.html',
                           id=id,
                           categorias=categorias,
                           insumos=insumos,
                           insumos_utilizados=insumos_utilizados,
                           valor_mao=valor_mao,
                           nome=nome,
                           nome_empresa=nome_empresa)

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

