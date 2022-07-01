from flask import Flask
from flask import render_template, request, redirect
from flaskext.mysql import MySQL
import requests
import json

app= Flask(__name__)

mysql = MySQL()
app.config['MYSQL_DATABASE_HOST']='localhost'
app.config['MYSQL_DATABASE_USER']='root'
app.config['MYSQL_DATABASE_PASSWORD']=''
app.config['MYSQL_DATABASE_DB']='importacao'
mysql.init_app(app)

@app.route('/')
def index():

    sql = "SELECT * from `simulacao`;"
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql)

    simulacao = cursor.fetchall()
    print(simulacao)

    conn.commit()
    
    return render_template('sistema/index.html', simulacao = simulacao)

@app.route('/criar')
def method_name():
    
    return render_template ('sistema/criar.html')


@app.route('/store', methods=['POST'])
def storage():
     
    ## Cotação do dólar - API

    cotacoes = requests.get('http://economia.awesomeapi.com.br/json/last/USD-BRL,EUR-BRL,BTC-BRL')
    cotacoes = cotacoes.json()

    cotacao_dolar = cotacoes['USDBRL']['bid']

    dolar = float(cotacao_dolar)

#--------------------------------------------------------------------------------------------------------
    ## A) Dados referentes da  operação

    _dataoper = request.form['txtdataoper']
    _ncm = request.form['txtncm'] 
    _invoice = request.form['txtinvoice'] 
    _descricao = request.form['txtdescricao']  

    valorprod = request.form['txtvalorprod']
    _valorprod = float(valorprod) * dolar

    valorfreteint = request.form['txtvalorfreteint']
    _valorfreteint = float(valorfreteint) * dolar

    valorseguroint = request.form['txtvalorseguroint']
    _valorseguroint = float(valorseguroint) * dolar

    valorthc = request.form['txtvalorthc']
    _valorthc = float(valorthc) * dolar

    _valoradn = (_valorprod + _valorfreteint + _valorseguroint + _valorthc)

  
#--------------------------------------------------------------------------------------------------------
    #  B) Alíquotas - tributos federais e estaduais

    aliqii = request.form['txtaliqii']
    _aliqii = float(aliqii)

    aliqipi = request.form['txtaliqipi'] 
    _aliqipi = float(aliqipi)

    aliqpis = request.form['txtaliqpis'] 
    _aliqpis = float(aliqpis)
    
    aliqcofins = request.form['txtaliqcofins'] 
    _aliqcofins = float(aliqcofins)
    
    aliqicms = request.form['txtaliqicms']
    _aliqicms = float(aliqicms) 

    # Cálculos das alíquotas

    _valorii = _valoradn * (_aliqii / 100)
    _valoripi = (_valoradn + _valorii) * (_aliqipi / 100)

    _valorpis = _valoradn * (_aliqpis / 100)
    _valorcofins = _valoradn * (_aliqcofins / 100)

    _valoricms = ((_valoradn + _valoripi + _valorpis + _valorcofins) / (1 - ((_aliqicms)/100))) * (_aliqicms/100)
    _valorimpgeral = _valorii + _valoripi + _valorpis + _valorcofins + _valoricms

#--------------------------------------------------------------------------------------------------------
    #  C) Despesas Aduaneiras

    txlicenca =  request.form['txlicenca']
    _txlicenca = float(txlicenca)

    txsiscomex =  request.form['txsiscomex']
    _txsiscomex = float(txsiscomex)

    txbl =  request.form['txbl']
    _txbl = float(txbl)

    txdespadn =  request.form['txdespadn']
    _txdespadn = float(txdespadn) 

    txafrmm =  request.form['txafrmm']
    _txafrmm = float(txafrmm)

    txtransfcont =  request.form['txtransfcont']
    _txtransfcont = float(txtransfcont)

    txdevolcont =  request.form['txdevolcont']
    _txdevolcont = float(txdevolcont)

    txtsegrporto =  request.form['txtsegrporto']
    _txtsegrporto = float(txtsegrporto)


    txarm =  request.form['txarm']
    _txarm = float(txarm)

    txmov =  request.form['txmov']
    _txmov = float(txmov)


    txdesova =  request.form['txdesova']
    _txdesova = float(txdesova)

    txcarreg =  request.form['txcarreg']
    _txcarreg = float(txcarreg)

    txentrega =  request.form['txentrega']
    _txentrega = float(txentrega)

    _valortotaltx = (_txlicenca + _txsiscomex + _txbl + _txdespadn + _txafrmm + _txtransfcont + _txdevolcont + _txtsegrporto + _txarm + _txmov + _txdesova + _txcarreg + _txentrega)

#--------------------------------------------------------------------------------------------------------
    #  Valor Total Geral e Índices

    _valortotalgeral = _valoradn + _valorimpgeral + _valortotaltx

    # Índices

    _indvaloradn = ( _valoradn / _valortotalgeral) * 100
    
    _indvalortotaltx = ( _valortotaltx / _valortotalgeral ) * 100

    _indvalorimpgeral = ( _valorimpgeral / _valortotalgeral ) * 100
    


    sql ="INSERT INTO `simulacao` (`id`, `dataoper`, `ncm`, `invoice`, `descricao`, `valorprod`, `valorfreteint`, `valorseguroint`, `valorthc`, `valoradn`, `aliqii`, `aliqipi`, `aliqpis`, `aliqcofins`, `aliqicms`, `valorii`, `valoripi`, `valorpis`, `valorcofins`, `valoricms`, `valorimpgeral`, `txlicenca`, `txsiscomex`, `txbl`, `txdespadn`, `txafrmm`, `txtransfcont`, `txdevolcont`, `txtsegrporto`, `txarm`, `txmov`, `txdesova`, `txcarreg`, `txentrega`, `valortotaltx`, `valortotalgeral`, `indvaloradn`, `indvalortotaltx`, `indvalorimpgeral`) VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
    
    dados = (_dataoper ,  _ncm ,  _invoice ,  _descricao ,  _valorprod ,  _valorfreteint ,  _valorseguroint ,  _valorthc ,  _valoradn ,  _aliqii ,  _aliqipi ,  _aliqpis ,  _aliqcofins ,  _aliqicms ,  _valorii ,  _valoripi ,  _valorpis ,  _valorcofins ,  _valoricms ,  _valorimpgeral ,  _txlicenca ,  _txsiscomex ,  _txbl ,  _txdespadn ,  _txafrmm ,  _txtransfcont ,  _txdevolcont ,  _txtsegrporto ,  _txarm ,  _txmov ,  _txdesova ,  _txcarreg ,  _txentrega ,  _valortotaltx ,  _valortotalgeral ,  _indvaloradn ,  _indvalortotaltx ,  _indvalorimpgeral )
    
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql,dados)
    conn.commit() 

    return redirect('/')

@app.route('/apagar/<int:id>')
def apagar(id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM simulacao WHERE id =%s",(id))
    conn.commit()
    return redirect('/')




@app.route('/editar/<int:id>')
def editar(id):
    

    conn = mysql.connect()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM simulacao WHERE id=%s", (id))

    simulacao = cursor.fetchall()
    print(simulacao)

    conn.commit()    
    
    
    return render_template('sistema/editar.html', simulacao = simulacao)


@app.route('/atualizar', methods = ['POST'])
def atualizar():


 ## Cotação do dólar - API

    cotacoes = requests.get('http://economia.awesomeapi.com.br/json/last/USD-BRL,EUR-BRL,BTC-BRL')
    cotacoes = cotacoes.json()

    cotacao_dolar = cotacoes['USDBRL']['bid']

    dolar = float(cotacao_dolar)


    _id = request.form['txtid']
    _dataoper = request.form['txtdataoper']
    _ncm = request.form['txtncm'] 
    _invoice = request.form['txtinvoice'] 
    _descricao = request.form['txtdescricao']  

    valorprod = request.form['txtvalorprod']
    _valorprod = float(valorprod) * dolar

    valorfreteint = request.form['txtvalorfreteint']
    _valorfreteint = float(valorfreteint) * dolar

    valorseguroint = request.form['txtvalorseguroint']
    _valorseguroint = float(valorseguroint) * dolar

    valorthc = request.form['txtvalorthc']
    _valorthc = float(valorthc) * dolar

    _valoradn = (_valorprod + _valorfreteint + _valorseguroint + _valorthc)

  
#--------------------------------------------------------------------------------------------------------
    #  B) Alíquotas - tributos federais e estaduais

    aliqii = request.form['txtaliqii']
    _aliqii = float(aliqii)

    aliqipi = request.form['txtaliqipi'] 
    _aliqipi = float(aliqipi)

    aliqpis = request.form['txtaliqpis'] 
    _aliqpis = float(aliqpis)
    
    aliqcofins = request.form['txtaliqcofins'] 
    _aliqcofins = float(aliqcofins)
    
    aliqicms = request.form['txtaliqicms']
    _aliqicms = float(aliqicms) 

    # Cálculos das alíquotas

    _valorii = _valoradn * (_aliqii / 100)
    _valoripi = (_valoradn + _valorii) * (_aliqipi / 100)

    _valorpis = _valoradn * (_aliqpis / 100)
    _valorcofins = _valoradn * (_aliqcofins / 100)

    _valoricms = ((_valoradn + _valoripi + _valorpis + _valorcofins) / (1 - ((_aliqicms)/100))) * (_aliqicms/100)
    _valorimpgeral = _valorii + _valoripi + _valorpis + _valorcofins + _valoricms

#--------------------------------------------------------------------------------------------------------
    #  C) Despesas Aduaneiras

    txlicenca =  request.form['txlicenca']
    _txlicenca = float(txlicenca)

    txsiscomex =  request.form['txsiscomex']
    _txsiscomex = float(txsiscomex)

    txbl =  request.form['txbl']
    _txbl = float(txbl)

    txdespadn =  request.form['txdespadn']
    _txdespadn = float(txdespadn) 

    txafrmm =  request.form['txafrmm']
    _txafrmm = float(txafrmm)

    txtransfcont =  request.form['txtransfcont']
    _txtransfcont = float(txtransfcont)

    txdevolcont =  request.form['txdevolcont']
    _txdevolcont = float(txdevolcont)

    txtsegrporto =  request.form['txtsegrporto']
    _txtsegrporto = float(txtsegrporto)


    txarm =  request.form['txarm']
    _txarm = float(txarm)

    txmov =  request.form['txmov']
    _txmov = float(txmov)


    txdesova =  request.form['txdesova']
    _txdesova = float(txdesova)

    txcarreg =  request.form['txcarreg']
    _txcarreg = float(txcarreg)

    txentrega =  request.form['txentrega']
    _txentrega = float(txentrega)

    _valortotaltx = (_txlicenca + _txsiscomex + _txbl + _txdespadn + _txafrmm + _txtransfcont + _txdevolcont + _txtsegrporto + _txarm + _txmov + _txdesova + _txcarreg + _txentrega)

#--------------------------------------------------------------------------------------------------------
    #  Valor Total Geral e Índices

    _valortotalgeral = _valoradn + _valorimpgeral + _valortotaltx

    # Índices

    _indvaloradn = ( _valoradn / _valortotalgeral) * 100
    
    _indvalortotaltx = ( _valortotaltx / _valortotalgeral ) * 100

    _indvalorimpgeral = ( _valorimpgeral / _valortotalgeral ) * 100



    sql ="UPDATE `simulacao` SET dataoper = %s, ncm = %s, invoice= %s, descricao= %s, valorprod= %s, valorfreteint = %s, valorseguroint= %s, valorthc= %s, valoradn= %s, aliqii= %s, aliqipi= %s, aliqpis= %s, aliqcofins= %s, aliqicms= %s, valorii= %s, valoripi= %s, valorpis= %s, valorcofins= %s, valoricms= %s, valorimpgeral= %s, txlicenca= %s, txsiscomex= %s, txbl= %s, txdespadn= %s, txafrmm= %s, txtransfcont= %s, txdevolcont= %s, txtsegrporto= %s, txarm= %s, txmov= %s, txdesova= %s, txcarreg= %s, txentrega= %s, valortotaltx= %s, valortotalgeral= %s, indvaloradn= %s, indvalortotaltx= %s, indvalorimpgeral= %s WHERE id= %s;"
    
    dados = (_dataoper ,  _ncm ,  _invoice ,  _descricao ,  _valorprod ,  _valorfreteint ,  _valorseguroint ,  _valorthc ,  _valoradn ,  _aliqii ,  _aliqipi ,  _aliqpis ,  _aliqcofins ,  _aliqicms ,  _valorii ,  _valoripi ,  _valorpis ,  _valorcofins ,  _valoricms ,  _valorimpgeral ,  _txlicenca ,  _txsiscomex ,  _txbl ,  _txdespadn ,  _txafrmm ,  _txtransfcont ,  _txdevolcont ,  _txtsegrporto ,  _txarm ,  _txmov ,  _txdesova ,  _txcarreg ,  _txentrega ,  _valortotaltx ,  _valortotalgeral ,  _indvaloradn ,  _indvalortotaltx ,  _indvalorimpgeral, _id )
    
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql,dados)
    conn.commit() 

    #return render_template ('/')
    
    return redirect('/')

@app.route('/vermais/<int:id>')
def vermais(id):

    conn = mysql.connect()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM simulacao WHERE id=%s", (id))

    simulacao = cursor.fetchall()
    print(simulacao)

    conn.commit()    
    
    
    return render_template('sistema/vermais.html', simulacao = simulacao)




if __name__ == '__main__':
    app.run(debug=True)

    
