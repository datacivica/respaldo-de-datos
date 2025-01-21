# respaldo-de-datos

## Desarrollo

## CompraNet

- virtualenv venv
- source .venv/bin/activate
- pip install -r compranet/requirements.txt
- playwright install

En este punto necesitarás un archivo de entrada en excel de formato excel
descargado de Compranet.

Ejecuta

```bash
$python3 compranet/main.py archivo.xlsx xlsx <nombre> --sem=10
```

El `<nombre>` es un identificador usado para nombrar el archivo de salida.

## Plataforma de transparencia / Solicitudes

- virtualenv venv
- source venv/bin/activate
- pip install -r pnt/requirements.txt
- playwright install chromium

Ejecuta

```bash
$python3 pnt/solicitudes.py file_path

```

El `<file_path>` es el path del archivo `jsonl`
