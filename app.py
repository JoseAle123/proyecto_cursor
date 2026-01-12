from flask import Flask, render_template
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Backend no interactivo para servidor
import matplotlib.pyplot as plt
import io
import base64
import os

app = Flask(__name__)

# Configuración
CSV_FILE = 'ventas_farmacia.csv'
STATIC_FOLDER = 'static'
CHARTS_FOLDER = os.path.join(STATIC_FOLDER, 'charts')

# Crear carpetas si no existen
os.makedirs(STATIC_FOLDER, exist_ok=True)
os.makedirs(CHARTS_FOLDER, exist_ok=True)

def load_data():
    """Carga los datos del CSV"""
    df = pd.read_csv(CSV_FILE)
    df['ingreso'] = df['precio_unitario'] * df['cantidad']
    return df

def calculate_stats(df):
    """Calcula las estadísticas principales"""
    stats = {
        'ingreso_total': df['ingreso'].sum(),
        'producto_mas_vendido': df.groupby('producto')['cantidad'].sum().idxmax(),
        'cantidad_producto_mas_vendido': df.groupby('producto')['cantidad'].sum().max(),
        'ventas_por_categoria': df.groupby('categoria')['ingreso'].sum().to_dict(),
        'ventas_por_empleado': df.groupby('empleado')['ingreso'].sum().to_dict(),
        'cantidad_por_categoria': df.groupby('categoria')['cantidad'].sum().to_dict(),
        'cantidad_por_empleado': df.groupby('empleado')['cantidad'].sum().to_dict()
    }
    return stats

def create_chart(data, title, xlabel, ylabel, filename, color='steelblue'):
    """Crea un gráfico de barras y lo guarda como imagen"""
    plt.figure(figsize=(10, 6))
    plt.bar(data.keys(), data.values(), color=color)
    plt.title(title, fontsize=16, fontweight='bold')
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.grid(axis='y', alpha=0.3)
    
    # Guardar gráfico
    filepath = os.path.join(CHARTS_FOLDER, filename)
    plt.savefig(filepath, dpi=100, bbox_inches='tight')
    plt.close()
    
    return filepath

@app.route('/')
def index():
    """Página principal con análisis de ventas"""
    # Cargar datos
    df = load_data()
    
    # Calcular estadísticas
    stats = calculate_stats(df)
    
    # Generar gráficos
    chart_ventas_categoria = create_chart(
        stats['ventas_por_categoria'],
        'Ventas por Categoría',
        'Categoría',
        'Ingresos ($)',
        'ventas_categoria.png',
        color='steelblue'
    )
    
    chart_ventas_empleado = create_chart(
        stats['ventas_por_empleado'],
        'Ventas por Empleado',
        'Empleado',
        'Ingresos ($)',
        'ventas_empleado.png',
        color='coral'
    )
    
    chart_cantidad_categoria = create_chart(
        stats['cantidad_por_categoria'],
        'Cantidad Vendida por Categoría',
        'Categoría',
        'Cantidad',
        'cantidad_categoria.png',
        color='lightgreen'
    )
    
    chart_cantidad_empleado = create_chart(
        stats['cantidad_por_empleado'],
        'Cantidad Vendida por Empleado',
        'Empleado',
        'Cantidad',
        'cantidad_empleado.png',
        color='gold'
    )
    
    return render_template('index.html',
                         ingreso_total=stats['ingreso_total'],
                         producto_mas_vendido=stats['producto_mas_vendido'],
                         cantidad_producto_mas_vendido=stats['cantidad_producto_mas_vendido'],
                         ventas_por_categoria=stats['ventas_por_categoria'],
                         ventas_por_empleado=stats['ventas_por_empleado'],
                         chart_ventas_categoria='charts/ventas_categoria.png',
                         chart_ventas_empleado='charts/ventas_empleado.png',
                         chart_cantidad_categoria='charts/cantidad_categoria.png',
                         chart_cantidad_empleado='charts/cantidad_empleado.png')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
