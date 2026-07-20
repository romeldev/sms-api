# SMS API — Notas de instalacion y solucion de problemas

## Hardware

- Modem: **Huawei E1756** (USB 3G Movistar)
- VID:PID: `12D1:1417`
- Puerto AT: **COM4** (HUAWEI Mobile Connect - 3G PC UI Interface)

## Interfaces del modem

| Interfaz          | COM  | Driver           | Uso                  |
|-------------------|------|------------------|----------------------|
| MI_00 (Modem)     | COM5 | Modem.sys        | Llamadas de datos    |
| MI_01 (Network)   | -    | ewusbnet.sys     | Conexion a internet  |
| MI_02 (App)       | COM6 | hwdatacard.sys   | Protocolo propietario|
| MI_03 (PC UI)     | COM4 | hwdatacard.sys   | **Comandos AT**      |
| MI_04 (SmartCard) | -    | -                | Lector SIM           |
| MI_05 (Storage)   | -    | USBSTOR          | CD-ROM virtual       |

## Problemas encontrados y soluciones

### 1. Puerto COM4 ocupado por hwdatacard

**Problema:** El driver `hwdatacard.sys` toma control exclusivo de COM4, impidiendo abrirlo con pySerial.

**Solucion:**
```powershell
# En PowerShell como Administrador (una sola vez):
sc.exe config hwdatacard start= disabled
```
Luego reiniciar la PC. Despues del reinicio COM4 queda libre.

Si no se quiere reiniciar, detener el servicio manualmente:
```powershell
sc.exe stop hwdatacard
```
(Puede fallar con error 1052 porque es un driver kernel — en ese caso solo queda reiniciar)

### 2. Windows sin permisos de administrador

No se puede detener el servicio `hwdatacard` ni deshabilitar dispositivos sin ser admin.
Ejecutar los comandos de arriba en **PowerShell como Administrador**.

### 3. WSL no fue util

Se intento pasar el USB a WSL2 con `usbipd-win` para usar el modulo nativamente en Linux,
pero la descarga e instalacion de `usbipd-win` requerian permisos de administrador
y la descarga desde GitHub fallaba. Al final todo funciona directamente desde Windows con pySerial + COM4.

### 4. AT+CNUM no devuelve el numero

La mayoria de operadores (Movistar incluido) no almacenan el numero telefonico en el SIM.
`AT+CNUM` devuelve solo `OK`. El numero hay que obtenerlo de la factura o del empaque del SIM.

### 5. Senal en 0 o 99

Si `AT+CSQ` devuelve `99,99` o `0,99` significa que el modulo no tiene cobertura.
Posibles causas:
- Sin SIM insertado
- SIM vencido o sin saldo
- Sin cobertura 3G en la zona
- El modulo no encuentra la red adecuada (probar `AT+COPS=?` para listar operadores)

### 6. readline() devuelve linea vacia

Los modems responden con `\r\n` antes de cada linea. Al hacer `port.readline().strip()`,
las lineas vacias rompen el bucle de lectura prematuramente.

**Solucion:** Saltar lineas vacias con `if not line: continue` en lugar de `if not line: break`.

## Como se comunica la API

```
FastAPI (Windows) → pySerial → COM4 → Modem Huawei E1756
```

No hay bridges, WSL, ni scripts externos. Todo es Python puro con `pyserial`.

## Instalacion en otra PC

```powershell
# 1. Deshabilitar hwdatacard (Admin, una vez)
sc.exe config hwdatacard start= disabled
# Reiniciar PC

# 2. Clonar repo
git clone https://github.com/romeldev/sms-api.git
cd sms-api

# 3. Crear .env
echo "MODEM_PORT=COM4" > .env
echo "MODEM_BAUDRATE=115200" >> .env
echo "API_HOST=0.0.0.0" >> .env
echo "API_PORT=8000" >> .env

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Ejecutar
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# 6. Probar
curl http://localhost:8000/api/sms/health
curl http://localhost:8000/api/sms/status
```
