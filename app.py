import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from wms import adicionar_etiqueta, atualizar_localizacao, consultar_localizacao, gerar_relatorio_excel
from datetime import datetime, time
from io import BytesIO

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'fallback_secret_key')

@app.route('/')
def index():
    areas = ["Sorter", "Bolsão A", "Bolsão B", "Bolsão C", "Label B", "PS", "Bolsão Expedição", "Expedição"]
    hoje = datetime.now().date()
    data_inicial = datetime.combine(hoje, time.min).strftime('%Y-%m-%d %H:%M')
    data_final = datetime.combine(hoje, time.max).strftime('%Y-%m-%d %H:%M')
    return render_template('index.html', areas=areas, data_inicial=data_inicial, data_final=data_final)

@app.route('/adicionar', methods=['POST'])
def adicionar():
    id_etiqueta = request.form['id_etiqueta']
    area_inicial = request.form['area_inicial']
    try:
        adicionar_etiqueta(id_etiqueta, area_inicial)
        flash(f'Etiqueta {id_etiqueta} adicionada na área {area_inicial}. Data de criação registrada.')
    except ValueError as e:
        flash(str(e))
    return redirect(url_for('index'))

@app.route('/atualizar', methods=['POST'])
def atualizar():
    id_etiqueta = request.form['id_etiqueta']
    nova_area = request.form['nova_area']
    try:
        atualizar_localizacao(id_etiqueta, nova_area)
        flash(f'Etiqueta {id_etiqueta} atualizada para a área {nova_area}.')
    except ValueError as e:
        flash(str(e))
    return redirect(url_for('index'))

@app.route('/buscar', methods=['POST'])
def buscar():
    id_etiqueta = request.form['id_etiqueta_busca']
    try:
        info = consultar_localizacao(id_etiqueta)
        return render_template('index.html', areas=["Sorter", "Bolsão A", "Bolsão B", "Bolsão C", "Label B", "PS", "Bolsão Expedição", "Expedição"], etiqueta=id_etiqueta, area=info["area"], data_hora=info["data_hora"])
    except ValueError as e:
        flash(str(e))
        return redirect(url_for('index'))

@app.route('/gerar_relatorio', methods=['POST'])
def gerar_relatorio():
    data_inicio = request.form['data_inicio']
    data_fim = request.form['data_fim']
    try:
        data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d %H:%M')
        data_fim = datetime.strptime(data_fim, '%Y-%m-%d %H:%M')
        
        excel_file = gerar_relatorio_excel(data_inicio, data_fim)
        
        return send_file(
            excel_file,
            as_attachment=True,
            download_name=f"relatorio_{data_inicio.strftime('%Y%m%d_%H%M')}_{data_fim.strftime('%Y%m%d_%H%M')}.xlsx",
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except ValueError as e:
        flash(str(e))
        return redirect(url_for('index'))
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))