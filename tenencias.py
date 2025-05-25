import SHDA
import pandas as pd
import numpy as np
import time
import sys
import json
import ast
import os

from PyQt5.QtWidgets import (QApplication, QMainWindow, QTableWidget, QTabWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout, QHeaderView, QSplashScreen,
                            QWidget, QLabel, QPushButton, QGridLayout, QDialog, QMessageBox)
from PyQt5.QtCore import QTimer, Qt, pyqtSlot ,pyqtSignal, QObject
from PyQt5.QtGui import QColor, QPalette, QPixmap, QFont



class ConexionLED(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(10, 10)
        self.conectado = False
        self.actualizar_estado()
    
    def actualizar_estado(self, conectado=False):
        self.conectado = conectado
        color = QColor(0, 255, 0) if conectado else QColor(255, 0, 0)  # Verde o Rojo
        palette = self.palette()
        palette.setColor(QPalette.Window, color)
        self.setAutoFillBackground(True)
        self.setPalette(palette)

class DetalleOperacionesDialog(QDialog):
    def __init__(self, ticker, operaciones_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Detalle de Operaciones - {ticker}")
        self.setModal(True)
        self.resize(600, 400)
        self.setAttribute(Qt.WA_DeleteOnClose)  # Eliminar el diálogo al cerrarse
        
        layout = QVBoxLayout()
        
        # Título
        titulo = QLabel(f"Operaciones para: {ticker}")
        titulo.setFont(QFont("Arial", 12, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)
        
        # Tabla de operaciones
        tabla = QTableWidget()
        tabla.setColumnCount(4)
        tabla.setHorizontalHeaderLabels(['Estado', 'Importe', 'Cantidad', 'Precio'])
        
        # Configurar tabla
        tabla.horizontalHeader().setStretchLastSection(True)
        tabla.setAlternatingRowColors(True)
        
        # Llenar datos
        operaciones = self.parsear_operaciones(operaciones_data)
        tabla.setRowCount(len(operaciones))
        
        for row, op in enumerate(operaciones):
            tabla.setItem(row, 0, QTableWidgetItem(str(op.get('DETA', ''))))
            tabla.setItem(row, 1, QTableWidgetItem(f"{float(op.get('IMPO', 0)):,.2f}"))
            tabla.setItem(row, 2, QTableWidgetItem(str(op.get('CANT', ''))))
            tabla.setItem(row, 3, QTableWidgetItem(f"{float(op.get('PCIO', 0)):,.2f}"))
            
            # Colorear según el importe (positivo/negativo)
            importe = float(op.get('IMPO', 0))
            color = QColor(144, 238, 144) if importe >= 0 else QColor(255, 182, 193)  # Verde claro / Rosa claro
            
            for col in range(4):
                item = tabla.item(row, col)
                item.setBackground(color)
                
                # Alinear números a la derecha
                if col in [1, 2, 3]:  # Importe, Cantidad, Precio
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        layout.addWidget(tabla)
        
        # Botón cerrar
        btn_layout = QHBoxLayout()
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.clicked.connect(self.accept)  # Usar accept() en lugar de close()
        btn_layout.addStretch()
        btn_layout.addWidget(btn_cerrar)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def parsear_operaciones(self, data_str):
        """Parsea los datos de operaciones desde string"""
        try:
            if str(data_str).lower() == 'nan' or not data_str:
                return []
            
            # Intentar parsear como JSON
            if isinstance(data_str, str):
                try:
                    return json.loads(data_str)
                except json.JSONDecodeError:
                    # Intentar parsear como literal de Python
                    try:
                        return ast.literal_eval(data_str)
                    except (ValueError, SyntaxError):
                        return []
            else:
                return data_str if isinstance(data_str, list) else []
                
        except Exception as e:
            print(f"Error parseando operaciones: {e}")
            return []


class TablaDataFrame(QTableWidget):
    def __init__(self, df=None):
        super().__init__()
        self.setSortingEnabled(True)  # Habilitar ordenamiento
        self.detalle_col_idx = None  # Índice de la columna de detalles
        if df is not None:
            self.actualizar_df(df)
            
    def actualizar_df(self, df):
        self.clear()
        self.setSortingEnabled(False)  # Desactivar temporalmente para la actualización
        
        # Configurar filas y columnas
        rows, cols = df.shape
        self.setRowCount(rows)
        self.setColumnCount(cols)
        
        # Configurar encabezados
        self.setHorizontalHeaderLabels(df.columns)
        
        # Encontrar y ocultar la columna de detalles
        self.detalle_col_idx = None
        try:
            self.detalle_col_idx = df.columns.get_loc('Detalle de operaciones diarias')
            self.setColumnHidden(self.detalle_col_idx, True)  # Ocultar la columna
        except KeyError:
            self.detalle_col_idx = None
        
        # Estilizar encabezados - fondo gris y texto en negrita
        for col in range(cols):
            header_item = self.horizontalHeaderItem(col)
            if header_item:
                font = header_item.font()
                font.setBold(True)
                header_item.setFont(font)
                header_item.setBackground(QColor(30, 30, 180))  # Steel Blue (más oscuro)  
                header_item.setForeground(QColor(0, 255, 255))  # Texto blanco para contraste
        
        # También puedes aplicar estilo al header usando stylesheet
        self.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #265A7C;
                color: white;
                font-weight: bold;
                border: 1px solid #666666;
                padding: 4px;
            }
        """)
        
        # Llenar con datos
        for row in range(rows):
            # Verificar si hay operaciones en esta fila
            tiene_operaciones = False
            if self.detalle_col_idx is not None:
                detalle_value = df.iloc[row, self.detalle_col_idx]
                tiene_operaciones = (str(detalle_value).lower() != 'nan' and 
                                   detalle_value and 
                                   str(detalle_value).strip() != '')
            
            for col in range(cols):
                value = df.iloc[row, col]
                
                # Convertir el valor a string para mostrarlo en la tabla
                if isinstance(value, (float, np.float64)):
                    item = QTableWidgetItem(f"{value:.2f}")
                else:
                    item = QTableWidgetItem(str(value))

                font = item.font()
                font.setBold(True)
                item.setFont(font)

                # Alinear columnas específicas a la derecha
                columnas_derecha = ['Cantidad', 
                                    'Ultimo Precio',            
                                    'Resultado', 
                                    'Costo Promedio', 
                                    'Sabe Dios', 
                                    '% Var Total', 
                                    'Importe Actual', 
                                    '% Diario',
                                    'Resultado del dia',
                                    'Actual en U$S']

                nombre_columna = df.columns[col]
                
                if nombre_columna in columnas_derecha:
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                else:
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                
                # Colorear filas con operaciones en verde agua
                if tiene_operaciones:
                    item.setBackground(QColor(127, 255, 212))  # Verde agua (Aquamarine)
                else:
                    # Alternar colores de filas - celeste claro y celeste oscuro
                    if row % 2 == 0:  # Filas pares (0, 2, 4...)
                        item.setBackground(QColor(130, 130, 130))  # Celeste claro
                    else:  # Filas impares (1, 3, 5...)
                        item.setBackground(QColor(150, 150, 150))  # Celeste oscuro
                
                # Colorear texto en rojo si contiene valores negativos
                text_value = str(value)
                if text_value.startswith('-') or (isinstance(value, (int, float, np.int64, np.float64)) and value < 0):
                    item.setForeground(QColor(180, 0, 0))  # Dark Red
                    # Opcional: hacer el texto en negrita para mayor énfasis
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
                
                # Hacer clickeable el ticker si hay operaciones
                if tiene_operaciones and nombre_columna == 'Ticker':
                    item.setData(Qt.UserRole, df.iloc[row, self.detalle_col_idx])  # Guardar datos de operaciones
                    font = item.font()
                    #font.setUnderline(True)
                    item.setFont(font)
                    item.setForeground(QColor(0, 0, 190))  # Azul para indicar que es clickeable
                
                self.setItem(row, col, item)
        
        self.resizeColumnsToContents()
        self.setSortingEnabled(True)  # Reactivar ordenamiento
        
        # Conectar evento de click solo una vez
        try:
            self.cellClicked.disconnect()  # Desconectar señales previas
        except TypeError:
            pass  # No hay conexiones previas
        self.cellClicked.connect(self.on_cell_clicked)
    
    def on_cell_clicked(self, row, col):
        """Maneja el click en las celdas"""
        item = self.item(row, col)
        if not item:
            return
        
        # Verificar si es la columna Ticker y tiene datos de operaciones
        nombre_columna = self.horizontalHeaderItem(col).text()
        if nombre_columna == 'Ticker':
            operaciones_data = item.data(Qt.UserRole)
            if operaciones_data:
                ticker = item.text()
                # Pausar temporalmente las actualizaciones
                parent_window = self.parent()
                while parent_window and not isinstance(parent_window, InterfazSHDA):
                    parent_window = parent_window.parent()
                
                if parent_window:
                    parent_window.pausar_actualizaciones()
                
                dialog = DetalleOperacionesDialog(ticker, operaciones_data, self)
                dialog.exec_()
                
                # Reanudar actualizaciones
                if parent_window:
                    parent_window.reanudar_actualizaciones()


class InterfazSHDA(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Monitoreo Tenencias IEB+")
        
        # Cargar configuración desde archivo
        self.cargar_configuracion()
        
        self.hb = None
        self.conectado = False
        self.df = pd.DataFrame()
        self.actualizaciones_pausadas = False  # Flag para pausar actualizaciones
        
        # Configurar interfaz
        self.inicializar_ui()
        
        # Configurar timer para actualización
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_datos)
        
        # Intentar conectar al inicio
        self.conectar()
        
        # Iniciar temporizador (actualización cada 5 segundos)
        self.timer.start(2000)
    
    def cargar_configuracion(self):
        """Carga la configuración desde el archivo config.json"""
        config_file = 'config.json'
        
        # Configuración por defecto
        config_default = {
            "host": 0000,
            "dni": "0000000",
            "user": "xxxxxxxx",
            "password": "xxxxxxxxx",
            "comitente": 000000
        }
        
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    
                # Asignar valores de configuración
                self.host = config.get('host', config_default['host'])
                self.dni = config.get('dni', config_default['dni'])
                self.user = config.get('user', config_default['user'])
                self.password = config.get('password', config_default['password'])
                self.comitente = config.get('comitente', config_default['comitente'])
                
                print(f"Configuración cargada desde {config_file}")
                
            else:
                # Crear archivo de configuración con valores por defecto
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(config_default, f, indent=4, ensure_ascii=False)
                
                # Usar configuración por defecto
                self.host = config_default['host']
                self.dni = config_default['dni']
                self.user = config_default['user']
                self.password = config_default['password']
                self.comitente = config_default['comitente']
                
                print(f"Archivo {config_file} creado con configuración por defecto")
                QMessageBox.information(self, "Configuración", 
                                       f"Se ha creado el archivo {config_file} con la configuración por defecto.\n"
                                       "Por favor, edite este archivo con sus credenciales reales.")
                
        except Exception as e:
            print(f"Error al cargar configuración: {e}")
            # Usar configuración por defecto en caso de error
            self.host = config_default['host']
            self.dni = config_default['dni']
            self.user = config_default['user']
            self.password = config_default['password']
            self.comitente = config_default['comitente']
            
            QMessageBox.warning(self, "Error de Configuración", 
                               f"Error al cargar {config_file}. Usando configuración por defecto.\n"
                               f"Error: {str(e)}")
    
    def inicializar_ui(self):
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        layout_principal = QVBoxLayout(central_widget)
        
        # Panel superior con indicador LED y botones
        panel_superior = QHBoxLayout()
        
        # Indicador LED
        self.led_conexion = ConexionLED()
        panel_superior.addWidget(QLabel("Estado de conexión:"))
        panel_superior.addWidget(self.led_conexion)
        
        # Botones
        self.btn_conectar = QPushButton("Conectar")
        self.btn_conectar.clicked.connect(self.conectar)
        panel_superior.addWidget(self.btn_conectar)
        
        self.btn_desconectar = QPushButton("Desconectar")
        self.btn_desconectar.clicked.connect(self.desconectar)
        panel_superior.addWidget(self.btn_desconectar)
        
        panel_superior.addStretch()
        
        # Agregar panel superior al layout principal
        layout_principal.addLayout(panel_superior)
        
        # Tabla para mostrar el DataFrame
        self.tabla = TablaDataFrame()
        layout_principal.addWidget(self.tabla)
        
        # Configuración de la ventana
        self.resize(1500, 950)
    
    def conectar(self):
        try:
            self.hb = SHDA.SHDA(self.host, self.dni, self.user, self.password)
            self.conectado = True
            self.led_conexion.actualizar_estado(True)
            self.actualizar_datos()
            print("Conexión establecida con éxito")
        except Exception as e:
            self.conectado = False
            self.led_conexion.actualizar_estado(False)
            print(f"Error de conexión: {e}")
    
    def desconectar(self):
        self.conectado = False
        self.led_conexion.actualizar_estado(False)
        self.hb = None
        print("Desconectado")

    def pausar_actualizaciones(self):
        """Pausa las actualizaciones automáticas"""
        self.actualizaciones_pausadas = True
    
    def reanudar_actualizaciones(self):
        """Reanuda las actualizaciones automáticas"""
        self.actualizaciones_pausadas = False

    def guardar_datos_anteriores(self):
        """Guarda el DataFrame actual en anterior.json"""
        try:
            # Convertir el DataFrame a JSON
            datos_json = self.df.to_json(orient='records', date_format='iso', indent=2)
            
            # Guardar en archivo
            with open('anterior.json', 'w', encoding='utf-8') as f:
                f.write(datos_json)
            
            
            
        except Exception as e:
            print(f"Error al guardar datos anteriores: {e}")

    def calcular_variaciones_diarias(self):
        """Calcula las variaciones diarias comparando con anterior.json"""
        try:
            
            
            # Inicializar SIEMPRE las columnas primero
            if not self.df.empty:
                self.df['% Diario'] = 0.0
                self.df['Resultado del dia'] = 0.0
                
            
            # Verificar si existe el archivo anterior
            if not os.path.exists('anterior.json'):
                print("No existe archivo anterior.json para comparar - columnas quedan en 0")
                return
            
            # Cargar datos anteriores
            with open('anterior.json', 'r', encoding='utf-8') as f:
                datos_anteriores = json.load(f)
            
            df_anterior = pd.DataFrame(datos_anteriores)
            
            # Crear diccionario de datos anteriores usando Ticker como clave
            if 'Ticker' in df_anterior.columns and 'Ticker' in self.df.columns:
                datos_ant_dict = {}
                for _, row in df_anterior.iterrows():
                    ticker = row.get('Ticker', '')
                    if ticker and ticker != 'TOTALES':  # Excluir fila de totales
                        datos_ant_dict[ticker] = {
                            'PCIO_anterior': float(row.get('Ultimo Precio', 0)) if row.get('Ultimo Precio', 0) != '' else 0,
                            'IMPO_anterior': float(row.get('Importe Actual', 0)) if row.get('Importe Actual', 0) != '' else 0
                        }
                
                print(f"Diccionario de datos anteriores creado con {len(datos_ant_dict)} tickers")
                
                # Calcular variaciones para el DataFrame actual
                calculos_realizados = 0
                for idx, row in self.df.iterrows():
                    ticker = row.get('Ticker', '')
                    
                    if ticker and ticker != 'TOTALES' and ticker in datos_ant_dict:
                        # Obtener valores actuales
                        pcio_actual = float(row.get('Ultimo Precio', 0)) if row.get('Ultimo Precio', 0) != '' else 0
                        impo_actual = float(row.get('Importe Actual', 0)) if row.get('Importe Actual', 0) != '' else 0
                        
                        # Obtener valores anteriores
                        pcio_anterior = datos_ant_dict[ticker]['PCIO_anterior']
                        impo_anterior = datos_ant_dict[ticker]['IMPO_anterior']
                        
                        # Calcular % Diario (variación en precio)
                        if pcio_anterior != 0:
                            variacion_diaria = ((pcio_actual - pcio_anterior) / pcio_anterior) * 100
                            self.df.at[idx, '% Diario'] = round(variacion_diaria, 2)
                        
                        # Calcular Resultado del día (diferencia en importe)
                        resultado_dia = impo_actual - impo_anterior
                        self.df.at[idx, 'Resultado del dia'] = round(resultado_dia, 2)
                        
                        calculos_realizados += 1
                
                print(f"Variaciones calculadas para {calculos_realizados} tickers")
                print("=== CALCULO DE VARIACIONES COMPLETADO ===")
            
        except Exception as e:
            print(f"ERROR al calcular variaciones diarias: {e}")
            import traceback
            traceback.print_exc()
            # En caso de error, asegurar que las columnas existan
            if not self.df.empty:
                self.df['% Diario'] = 0.0
                self.df['Resultado del dia'] = 0.0
    
    def actualizar_datos(self):
        if not self.conectado or self.hb is None or self.actualizaciones_pausadas:
            return
        
        try:
            # Obtener datos actualizados
            df_tenencia = self.hb.account(self.comitente)
            self.df = pd.DataFrame(df_tenencia)

            # Verificar si hay filas con "CIERRE" en la columna "Hora"
            if 'Hora' in self.df.columns:
                filas_cierre = self.df[self.df['Hora'].astype(str).str.upper() == 'CIERRE']
                if not filas_cierre.empty:
                    # Guardar el dataframe completo como anterior.json
                    self.guardar_datos_anteriores()
                    

            # Crear diccionario de renombrado solo para columnas que existen
            columnas_renombrar = {}
            if "AMPL" in self.df.columns:
                columnas_renombrar["AMPL"] = "Nombre de la Especie"
            if "TICK" in self.df.columns:
                columnas_renombrar["TICK"] = "Ticker"
            if "CANT" in self.df.columns:
                columnas_renombrar["CANT"] = "Cantidad"
            if "Hora" in self.df.columns:
                columnas_renombrar["Hora"] = "Hora"        
            if "PCIO" in self.df.columns:
                columnas_renombrar["PCIO"] = "Ultimo Precio"
            if "GTOS" in self.df.columns:
                columnas_renombrar["GTOS"] = "Resultado"
            if "CAN0" in self.df.columns:
                columnas_renombrar["CAN0"] = "Costo Promedio"
            if "CAN2" in self.df.columns:
                columnas_renombrar["CAN2"] = "Sabe Dios"
            if "CAN3" in self.df.columns:
                columnas_renombrar["CAN3"] = "% Var Total"
            if "IMPO" in self.df.columns:
                columnas_renombrar["IMPO"] = "Importe Actual"
            if "Detalle" in self.df.columns:
                columnas_renombrar["Detalle"] = "Detalle de operaciones diarias"

            # Renombrar solo las columnas que existen
            self.df = self.df.rename(columns=columnas_renombrar)

            # Convertir columnas numéricas solo si existen
            columnas_numericas = ['Ultimo Precio', 'Resultado', 'Costo Promedio', '% Var Total', 'Importe Actual']
            
            for col in columnas_numericas:
                if col in self.df.columns:
                    self.df[col] = pd.to_numeric(self.df[col], errors='coerce').round(2)

            ## mapeo de tipos de activos 
            if 'TIPO' in self.df.columns:
                tipo_activo = { 
                    '0': 'Acciones', '1': 'Bonos', '2': 'Panel General', '3': 'ON',
                    '4': 'Dolar USA', '5': 'Opciones', '6': 'Letras', '7': 'Cedear'
                }
                self.df['TIPO'] = self.df['TIPO'].astype(str).map(tipo_activo).fillna(self.df['TIPO'])

                # Agregar la condición especial para Cash
                if 'ESPE' in self.df.columns:
                    self.df.loc[self.df['ESPE'] == 'Cash', 'TIPO'] = 'Efectivo'
            
            # Calcular columna en USD solo si las columnas necesarias existen
            if 'Ticker' in self.df.columns and 'Ultimo Precio' in self.df.columns and 'Importe Actual' in self.df.columns:
                # Obtener el precio del dólar (valor de 'Ultimo Precio' donde Ticker == 'DOLARUSA')
                dolar_rows = self.df.loc[self.df['Ticker'] == 'DOLARUSA', 'Ultimo Precio']
                if not dolar_rows.empty:
                    precio_dolar = dolar_rows.iloc[0]
                    # Crear la nueva columna 'Actual en U$S'
                    self.df['Actual en U$S'] = (self.df['Importe Actual'] / precio_dolar).round(2)

            # IMPORTANTE: Calcular variaciones diarias ANTES de procesar las columnas finales
            self.calcular_variaciones_diarias()

            # Agregar fila de totales solo si las columnas necesarias existen
            if 'Nombre de la Especie' in self.df.columns:
                df_sin_totales = self.df[self.df['Nombre de la Especie'] != 'TOTALES']
                
                fila_totales = pd.Series(index=self.df.columns)
                fila_totales = fila_totales.fillna('')
                fila_totales['Nombre de la Especie'] = 'TOTALES'
                
                if 'Resultado' in self.df.columns:
                    total_resultado = df_sin_totales['Resultado'].sum()
                    fila_totales['Resultado'] = total_resultado
                
                if 'Importe Actual' in self.df.columns:
                    total_importe_actual = df_sin_totales['Importe Actual'].sum()
                    fila_totales['Importe Actual'] = total_importe_actual
                
                if 'Actual en U$S' in self.df.columns:
                    total_actual_usd = df_sin_totales['Actual en U$S'].sum()
                    fila_totales['Actual en U$S'] = total_actual_usd

                # Totales para las nuevas columnas
                if '% Diario' in self.df.columns:
                    fila_totales['% Diario'] = ''  # No sumar porcentajes
                
                if 'Resultado del dia' in self.df.columns:
                    total_resultado_dia = df_sin_totales['Resultado del dia'].sum()
                    fila_totales['Resultado del dia'] = total_resultado_dia

                # Agregar la fila al DataFrame usando pd.concat
                self.df = pd.concat([self.df, fila_totales.to_frame().T], ignore_index=True)

            # Seleccionar columnas finales solo si existen
            columnas_finales = []
            posibles_columnas = ['TIPO','Nombre de la Especie', 'Ticker', 'Cantidad', 'Hora','Ultimo Precio', 'Resultado', 'Costo Promedio', 'Sabe Dios', '% Var Total', 'Importe Actual', 'Actual en U$S', '% Diario','Resultado del dia', "Detalle de operaciones diarias"]
            
            for col in posibles_columnas:
                if col in self.df.columns:
                    columnas_finales.append(col)
            
            if columnas_finales:
                self.df = self.df[columnas_finales]
            
            # Actualizar la tabla
            self.tabla.actualizar_df(self.df)
            
        except Exception as e:
            print(f"Error al actualizar datos: {e}")
            self.conectado = False
            self.led_conexion.actualizar_estado(False)


def main():
    app = QApplication(sys.argv)
    ventana = InterfazSHDA()

    app.processEvents()

    ventana.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()