from flask import Flask, jsonify, request
import json
import os

app = Flask(__name__)
JSON_FILE = 'sensores.json'

# Rangos válidos requeridos por la especificación
RANGOS = {
    'temperatura': (-10.0, 100.0),
    'presión': (0.0, 500.0),
    'velocidad': (0.0, 150.0)
}

def cargar_datos():
    """Carga los datos desde el archivo JSON."""
    if not os.path.exists(JSON_FILE):
        return []
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def guardar_datos(datos):
    """Guarda los datos en el archivo JSON actualizándolo en tiempo real."""
    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)

@app.route('/sensors/', methods=['GET'])
def get_sensors():
    """Devuelve todos los datos almacenados en el archivo JSON."""
    datos = cargar_datos()
    return jsonify(datos), 200

@app.route('/sensors/<int:sensor_id>', methods=['GET'])
def get_sensor_by_id(sensor_id):
    """Devuelve los registros asociados a un sensor específico por su ID."""
    datos = cargar_datos()
    filtrados = [s for s in datos if s.get('sensor_id') == sensor_id]
    if not filtrados:
        return jsonify({'error': 'Sensor no encontrado'}), 404
    return jsonify(filtrados), 200

@app.route('/sensors/', methods=['POST'])
def add_sensor():
    """Permite agregar un nuevo registro de sensor aplicando validaciones."""
    nuevo = request.get_json()
    
    # Validar presencia de campos requeridos
    campos_requeridos = ['sensor_id', 'type', 'value', 'timestamp']
    for campo in campos_requeridos:
        if campo not in nuevo:
            return jsonify({'error': f'Falta el campo requerido: {campo}'}), 400
            
    sensor_type = nuevo['type']
    valor = nuevo['value']
    
    # Validación 1: Tipo de sensor permitido
    if sensor_type not in RANGOS:
        return jsonify({'error': f'Tipo inválido. Debe ser uno de: {list(RANGOS.keys())}'}), 400
        
    # Validación 2: Rango de valores esperados
    min_val, max_val = RANGOS[sensor_type]
    if not (min_val <= valor <= max_val):
        return jsonify({'error': f'El valor {valor} está fuera del rango permitido para {sensor_type} [{min_val}, {max_val}]'}), 400
        
    datos = cargar_datos()
    datos.append(nuevo)
    guardar_datos(datos)
    
    return jsonify({'mensaje': 'Sensor agregado exitosamente', 'sensor': nuevo}), 201

@app.route('/sensors/<int:sensor_id>', methods=['PUT'])
def update_sensor(sensor_id):
    """Actualiza los datos de un sensor existente."""
    datos = cargar_datos()
    actualizaciones = request.get_json()
    
    encontrado = False
    for item in datos:
        if item.get('sensor_id') == sensor_id:
            if 'type' in actualizaciones:
                t = actualizaciones['type']
                if t not in RANGOS:
                    return jsonify({'error': f'Tipo inválido: {t}'}), 400
                item['type'] = t
            if 'value' in actualizaciones:
                v = actualizaciones['value']
                t_actual = item['type']
                min_val, max_val = RANGOS[t_actual]
                if not (min_val <= v <= max_val):
                    return jsonify({'error': f'Valor fuera de rango [{min_val}, {max_val}]'}), 400
                item['value'] = v
            if 'timestamp' in actualizaciones:
                item['timestamp'] = actualizaciones['timestamp']
            encontrado = True
            
    if not encontrado:
        return jsonify({'error': 'Sensor no encontrado'}), 404
        
    guardar_datos(datos)
    return jsonify({'mensaje': 'Sensor actualizado exitosamente'}), 200

@app.route('/sensors/<int:sensor_id>', methods=['DELETE'])
def delete_sensor(sensor_id):
    """Elimina los registros de un sensor del archivo JSON."""
    datos = cargar_datos()
    nuevos_datos = [s for s in datos if s.get('sensor_id') != sensor_id]
    
    if len(nuevos_datos) == len(datos):
        return jsonify({'error': 'Sensor no encontrado'}), 404
        
    guardar_datos(nuevos_datos)
    return jsonify({'mensaje': f'Sensor {sensor_id} eliminado exitosamente'}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)