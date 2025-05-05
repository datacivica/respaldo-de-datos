# buscador tematicos pnt

python version 3.13

1- setup environment [uv](https://docs.astral.sh/uv/pip/environments/) or [python](https://docs.python.org/3/library/venv.html)
2- `source your_env/bin/activate` windows `your_env\Scripts\Activate` ...etc
2- install packages using `uv pip install -r requirements.txt` or `pip install -r requirements.txt`
3- install browser `PLAYWRIGHT_BROWSERS_PATH=0 playwright install chromium`

## Notas de uso

- El script va ejecutar un navigador
- El script va mandar request al api de timatico
- La default index es 10000 va salir al cuando ejecuta el script y va cambiar solo
- Si quieren agregar mas de un órgano (estado) necesitan descomentar la linea 353
- va crear carpeta `buscador_tematico/timatico que esta descagando/estado/ano`
- El script se ejecutará durante todos los años y de forma automática
- Error de base de datos `An error occurred: invalid integer value "default_port" for connection option "port"` son normales no causan problema con ejecución del script, si vamos a hacer base de datos van quitar estos errores solos
- El script registra un error JSON cuando se emite como búfer. Para obtener más información sobre este [issue](https://github.com/microsoft/playwright/issues/26388) podemos arreglar el límite del navegador. Pero ahora tenemos que registrar el error y luego descargar estos errores.

- Registro como sueldos.json directorio.json ....etc si borran cuando termina el temático.
- el run loop state.json es para registrar el proceso de temático y órganos va crear después de terminar la primer temático.
- va notar diferencia entre los temáticos de descarga por ejemplo el dirctorio es mas rapido seuldo pero mas linto de tramites

- cerar el script con Ctrl+c

## Subir archivos JSON a Google Drive

Subir los archivos .zip generados a Google Drive
orden de los carpetas en drive
[Sueldos](https://drive.google.com/drive/folders/1Jbq91oU7ohl4iC6ei9Dy6kO9M8NxlQ2r?usp=drive_link)
[Directorio](https://drive.google.com/drive/folders/1u_lup1xrBVi6GMBC1ob-XEh0kgjcb7d6?usp=drive_link)
[Servicios](https://drive.google.com/drive/folders/1P7rub_cLAFr90exLFTuYIo9oIF7z8U-s?usp=drive_link)
[Contratos](https://drive.google.com/drive/folders/1Uog2fDcBrDNqbzk5UVf-aNoSPz147X1W?usp=drive_link)
[Tramites](https://drive.google.com/drive/folders/1F7TLlhECm63vs4Kpeeaj6bUPHkM99-iD?usp=drive_link)
[servidores_sancionados](https://drive.google.com/drive/folders/1wDBdjDucXtycia4dV9I5ql9ODgQNpHjR?usp=drive_link)
[presupueso_anual](https://drive.google.com/drive/folders/1qgmRd8Kdvwl8lpPxn49yIb3bvFTDDyrB?usp=sharing)
[EJERCICIO_PRESUPUESTO](https://drive.google.com/drive/folders/1ydsIcrgfcswvRK6lQso8cKrd6uQj5C1F?usp=drive_link)
[resoluciones](https://drive.google.com/drive/folders/1slkxUhCqpv7fCWABaQGRLiLCuEDUffEr?usp=drive_link)

## Execute script

basem

```bash
PLAYWRIGHT_BROWSERS_PATH=0 python run_loop.py -o "Ciudad de México"
```

abraham

```bash
PLAYWRIGHT_BROWSERS_PATH=0 python run_loop.py -o "Estado de México"
```

paul

```bash
PLAYWRIGHT_BROWSERS_PATH=0 python run_loop.py -o "Federación"
```

jorge M

```bash
PLAYWRIGHT_BROWSERS_PATH=0 python run_loop.py -o "Jalisco"
```

Ricalanis

```bash
PLAYWRIGHT_BROWSERS_PATH=0 python run_loop.py -o "Nuevo León"
```
