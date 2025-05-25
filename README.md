# Monitoreo de Portfolio personal 

Una aplicación de escritorio desarrollada en Python para monitorear y visualizar tenencias de instrumentos financieros en tiempo real, conectándose a la API de SHDA (Sistema de Homebanking para Agentes).

## Características Principales

### 🔄 Monitoreo en Tiempo Real
- Actualización automática cada 2 segundos
- Indicador LED de estado de conexión (verde/rojo)
- Pausado inteligente de actualizaciones durante visualización de detalles

### 📊 Visualización Completa de Datos
- **Información de instrumentos**: Ticker, nombre, cantidad, último precio
- **Análisis financiero**: Resultado, costo promedio, porcentaje de variación total
- **Conversión a USD**: Cálculo automático usando cotización del dólar
- **Análisis diario**: Variación porcentual y resultado del día comparado con sesión anterior

### 💹 Gestión de Operaciones
- Visualización de operaciones diarias por instrumento
- Detalle completo: estado, importe, cantidad y precio de cada operación
- Códigos de color para identificar operaciones positivas/negativas
- Interface clickeable en tickers con operaciones disponibles

### 🎨 Interface Intuitiva
- Tabla con ordenamiento por columnas
- Alternancia de colores por filas para mejor legibilidad
- Resaltado especial para instrumentos con operaciones del día
- Formato numérico apropiado con alineación y colores para valores negativos

## Requisitos del Sistema

### Dependencias Python
```bash
pip install PyQt5 pandas numpy
```

### Librerías Adicionales
- `SHDA`: Librería para conexión con el sistema SHDA (debe estar disponible en el entorno)
- Gracias por compartir @franco-lamas

## Configuración

### Archivo de Configuración
La aplicación utiliza un archivo `config.json` que se crea automáticamente en el primer uso:

```json
{
    "host": 0000,
    "dni": "0000000",
    "user": "xxxxxxxx",
    "password": "xxxxxxxxx",
    "comitente": 000000
}
```

**⚠️ Importante**: Edite este archivo con sus credenciales reales antes de usar la aplicación.

### Configuración de Parámetros
- **host**: Numero de ALYC 
- **dni**: Documento Nacional de Identidad
- **user**: Usuario de acceso
- **password**: Contraseña de acceso
- **comitente**: Código de comitente

### Broker	                   Byma Id
- Buenos Aires Valores S.A.	    12
- Proficio Investment S.A.	    20
- Tomar Inversiones S.A.	    81
- Bell Investments S.A.	        88
- RIG Valores S.A.	            91
- Soluciones Financieras S.A.	94
- Maestro y Huerres S.A.         127
- Bolsa de Comercio del Chaco	153
- Prosecurities S.A.	        164
- Servente y Cia. S.A.	        186
- Alfy Inversiones S.A.	        201
- Invertir en Bolsa S.A.	    203
- Futuro Bursátil S.A.	        209
- Sailing S.A.	                233
- Negocios Financieros y Bursátiles S.A. (Cocos Capital)	265
- Veta Capital S.A.	           284

## Instalación y Uso

### 1. Preparación del Entorno
```bash
# Clonar o descargar el proyecto
# Instalar dependencias
pip install PyQt5 pandas numpy

# Asegurar que la librería SHDA esté disponible

pip install SHDA --upgrade --no-cache-dir
```

### 2. Configuración Inicial
```bash
# Ejecutar la aplicación por primera vez
python tenencias.py

# Editar el archivo config.json generado con sus credenciales
# Reiniciar la aplicación
```

### 3. Uso de la Aplicación
1. **Conexión**: Usar el botón "Conectar" para establecer conexión con SHDA
2. **Monitoreo**: Los datos se actualizan automáticamente cada 2 segundos
3. **Análisis**: Hacer click en tickers con operaciones para ver detalles
4. **Desconexión**: Usar el botón "Desconectar" cuando termine

## Funcionalidades Detalladas

### Tipos de Instrumentos Soportados
- **Acciones** (TIPO: 0)
- **Bonos** (TIPO: 1)
- **Panel General** (TIPO: 2)
- **Obligaciones Negociables** (TIPO: 3)
- **Dólar USA** (TIPO: 4)
- **Opciones** (TIPO: 5)
- **Letras** (TIPO: 6)
- **CEDEARs** (TIPO: 7)


### Cálculos Automáticos

#### Conversión a USD
- Utiliza la cotización del dólar (DOLARUSA) para convertir importes
- Columna "Actual en U$S" se calcula automáticamente

#### Variaciones Diarias
- **% Diario**: Variación porcentual del precio respecto al cierre anterior
- **Resultado del día**: Diferencia en pesos del importe actual vs. anterior
- Se basa en comparación con archivo `anterior.json` generado automáticamente

### Gestión de Datos Históricos
- Al detectar hora "CIERRE", se guarda snapshot en `anterior.json`
- Permite comparaciones de rendimiento diario
- Persistencia automática de datos para análisis temporal

## Estructura de Archivos

```
proyecto/
├── tenencias.py          # Archivo principal de la aplicación
├── config.json           # Configuración de credenciales (auto-generado)
├── anterior.json         # Datos de sesión anterior (auto-generado)
└── README.md            # Este archivo
```

## Clases Principales

### `InterfazSHDA`
Clase principal que maneja la ventana y lógica de la aplicación.

### `TablaDataFrame`
Widget personalizado para mostrar DataFrames con funcionalidades específicas.

### `DetalleOperacionesDialog`
Diálogo modal para mostrar detalles de operaciones por instrumento.

### `ConexionLED`
Indicador visual del estado de conexión.

## Solución de Problemas

### Error de Conexión
- Verificar credenciales en `config.json`
- Confirmar conectividad con el servidor SHDA
- Revisar configuración de host

### Datos No Actualizan
- Verificar estado de conexión (LED verde)
- Confirmar que no hay diálogos abiertos (pausan actualización)
- Reintentar conexión

### Errores de Configuración
- Eliminar `config.json` para regenerar con valores por defecto
- Verificar formato JSON del archivo de configuración
- Confirmar que todos los campos están completos

## Seguridad

⚠️ **Importante para la Seguridad**:
- Nunca compartir el archivo `config.json` con credenciales reales
- Mantener las credenciales seguras y actualizadas
- La aplicación almacena credenciales en texto plano

## Contribuciones

Para contribuir al proyecto:
1. Fork del repositorio
2. Crear rama para nueva funcionalidad
3. Implementar cambios con documentación apropiada
4. Enviar Pull Request con descripción detallada

## Licencia

MIT License
la mayor parte del codigo fue creado por IA


## Contacto

tonygennaro@gmail.com

---
## Atribuciones y marcas
Home Broker una marca registrada de Estudio Gallo S.R.L. Agradecemos a Diego Degese  por crear y compartir pyhomebroker y a Franco Lamas por compratir SHDA
## DISCLAIMER
La información es mostrada “tal cual es”, puede ser incorrecta o contener errores, eso es responsabilidad de cada sitio. No somos responsables por el uso indebido de los Scripts.
