from flask import Flask, render_template
import fdb

app = Flask(__name__)
app.config['SECRET KEY'] = 'UP+'

host = 'localhost'
database = r'...' #definir o caminho do banco de dados
user = 'SYSDBA'
password = 'sysdba'
con = fdb.connect(host=host, database=database, user=user, password=password)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)