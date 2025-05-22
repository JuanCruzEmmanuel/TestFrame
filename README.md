# PROYECTO SMVA EN PYTHON

El alcance del proyecto aún se está evaluando, pero la idea inicial es intentar replicar el funcionamiento que existe en el código de LabVIEW y poder obtener mejoras a largo plazo.

Se dividirá en diferentes tópicos: Interfaz Gráfica, Funciones, Instrumentos, Base de Datos y Exportación. Luego es esencial agregar un sistema de gestión de los datos para entrenar una IA.

> **Nota:** El "○ viñeta" se logra con `Alt+9`, aunque parezca una "o minúscula", es un separador.

## INTERFAZ GRÁFICA: UI O GUI

- **Pantalla de Log-In:**
  - Permite acceder a partir de los usuarios ya creados.
  
- **Pantalla Principal:**
  - Tomar los equipos que se encuentran local para aumentar la velocidad.
  - Posibilidad de actualizar los equipos locales.
  - Filtrar los equipos por nombre.
  - Filtrar los equipos por estado (vigente/no vigente).
  - Conexión con ventana para creación y edición de protocolos (pendiente).
  - Ver protocolos ejecutados (pendiente).
  - Creación de nuevos usuarios (pendiente).
  - Selección de protocolo para ejecución (filtrado o no).
  
- **Pantalla para Selección de Configuración:**
  - Mostrar configuraciones creadas.
  - Seleccionar la configuracion
  - Permitir la creación de nuevas configuraciones. (Pendiente)
  - Permitir eliminar configuraciones. (Pendiente)

- **Pantalla Selección Número de Serie:**
  - Permitir seleccionar número de serie ya existente.
  - Permitir ingresar nuevo número de serie.

- **Pantalla Ejecución de Protocolo:**
  - Visor de bloques de protocolo:
    - Se completa de forma dinámica.
    - Se colorea de manera dinámica.
    - Contador de bloques.
  - Visor de pasos en ejecución:
    - Se completa de forma dinámica.
    - Se colorea de manera dinámica.
    - Contador de progreso (pendiente).
    - Bloque estadístico.
    - Botón de abortar.
    - Botón de detener ejecución (pendiente).
    - Botón de continuar ejecución (pendiente).
    - Botón exportar (pendiente).
    - Botón reporte de errores (pendiente).
  - Ingreso manual (texto):
    - Visor de información texto.
    - Botón Auto OK.
    - Completar respuesta.
  - Ingreso manual (numérico):
    - Visor de información texto.
    - Visor de rangos.
    - Permitir completar.
  - **Pantalla de Ejecución Manual (Esencial):**
    - Botón de salto (Esencial). Listo
    - Botón automático/manual.
    - Botón avanzar. 

## BASE DE DATOS

- **Acceder a los usuarios:**
  - Crear una lista local para aumentar la velocidad.
  - Crear nuevos usuarios (pendiente).
  - Permisos (pendiente).

- **Acceder a los protocolos modelos:**
  - Crear un diccionario con todos los protocolos en formato JSON para acceder de manera instantánea.
  - Poder actualizar el diccionario siempre que sea necesario.

- **Actualizar datos en ejecución:**
  - Copia y actualiza los datos de pasos de protocolo.
  - Subir protocolo cuando se realiza alguna pausa, se aborta o se finaliza (pendiente).

## INSTRUMENTOS MIGRADOS

- Torre de rele.
- Simulador de temperatura con torre rele.
- Multímetros.
- ESA620.
- Fuente programable.
- Carga eléctrica programable.
- Impulse 7000 (muy pocas funciones).
- ProSim 8 .
- MedSim 300 (pendiente).
- Impedanciometro (pendiente).
- Alarmas multipar/PM9000.
- Osciloscopios.
- Mediciones multipares/PM9000 (pendiente).
- Robot SZGH T750 (pendiente).
- Robot PM9000.
- Sumulador Guia de Presiones

## SECCIÓN INTELIGENCIA ARTIFICIAL

En proceso de planificación.
