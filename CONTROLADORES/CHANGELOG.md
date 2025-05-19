# Changelog CONTROLADORES

## Controlador PROSIM8 [Versión 1.1.0] - Correcciones Críticas y Mejoras de Estabilidad

### Corregido
- **Manejo de conexión serial**: 
  - Verificación explícita de `self.con is not None` en todos los métodos
  - Eliminación de errores de Pylance `OptionalMemberAccess` con type hints (`Optional[serial.Serial]`)
  - Cierre seguro de puerto en `disconnect()` con doble verificación mediante `is_open`
  
- **Protocolo de comunicación**:c
  - Agregado `\r` final en `writecommand()` para cumplir con la forma de comunicación del PS8
  - Formateo correcto de parámetros numéricos (ej: `025` en `SetArtifactSize`) para cumplir con la forma de comunicación del PS8
  - Validación de heart rate en 3 dígitos (`f"{self.HEARTRATE:03d}"`) para cumplir con la forma de comunicación del PS8

- **Manejo de errores**:
  - Excepciones personalizadas para operaciones sin conexión
  - Decodificación fallback a `latin1` en `readcommand()`

### Mejorado
- **Robustez de conexión**:
  - Reconexión automática evitada (`connect()` verifica estado actual)
  - Timeout de lectura configurado a 1 segundo
  
- **Métodos clave**:
  - `NormalRate()` ahora usa formato de 3 dígitos para frecuencias
  - `SetArtifactSize()` con conversión numérica segura
  - Comandos de polaridad/amplitud del marcapasos sincronizados inmediatamente

## [Versión 1.0.0] - Implementación Inicial

### Características
- Clase base con configuración inicial de parámetros
- Métodos básicos de conexión/desconexión
- Implementación inicial de comandos:
  - Control de ritmo cardíaco
  - Artefactos ECG
  - Arritmias programables
  - Configuración de marcapasos
