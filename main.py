from flask import Flask, request, jsonify, make_response, request, render_template, session
from flask_sqlalchemy import SQLAlchemy
import jwt
from datetime import datetime, timedelta
from functools import wraps
from psycopg2 import connect
from flask_cors import CORS, cross_origin
import json
import numpy as np
from scipy.linalg import inv
import sys

app = Flask(__name__)

print(sys.version)
@app.route('/')
def index():
    return jsonify({"Choo Choo": "Welcome to your Flask app 🚅"})

@app.route('/public')
def public():
    return 'For Public'

@app.route('/api/pdop', methods=['GET'])
def calculate_pdop():
    # Balizas
    B1 = np.array([0, 0, 3.05])
    B2 = np.array([0.51, 0, 2.95])
    B3 = np.array([-0.52, 0.1, 2.98])
    B4 = np.array([0, 0.50, 3.02])
    B5 = np.array([-0.02, -0.48, 3])
    Bs = [B1, B2, B3, B4, B5]

    # Posiciones rejilla 2D (Vectores 1x7)
    ex = np.arange(0, 3.5, 0.5)
    ey = np.arange(0, 3.5, 0.5)

    # Parametro altura receptor (por defecto 50 cm)
    pz = 0.5

    # Desviación típica del ruido Gaussiano de las medidas (distancias) en metros
    desv = 0.01

    PDOP = np.zeros((len(ex), len(ey)))

    for i in range(len(ex)):
        for j in range(len(ey)):
            J = []
            for B in Bs:
                d = np.sqrt((ex[i] - B[0])**2 + (ey[j] - B[1])**2 + (pz - B[2])**2)
                J.append([(ex[i] - B[0]) / d, (ey[j] - B[1]) / d, (pz - B[2]) / d])
            J = np.array(J)
            
            # Matriz de covarianza de los errores en posición
            COV_X = desv**2 * inv(J.T @ J)
            
            # Extraemos las varianzas asociadas a cada una de las coordenadas
            varx = COV_X[0, 0]
            vary = COV_X[1, 1]
            varz = COV_X[2, 2]
            
            PDOP[i, j] = np.sqrt(varx + vary + varz) / desv

    # Creamos rejilla
    X, Y = np.meshgrid(ex, ey)

    return jsonify({'pdop': PDOP.tolist(), 'ex': ex.tolist(), 'ey': ey.tolist()})

if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
