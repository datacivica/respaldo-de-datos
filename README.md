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

El `<file_path>` es el path del archivo `jsonl`

## Plataforma de transparencia / Obligacion

- **version de python es 3.13.2**

- pueden instalar [pyenv](https://github.com/pyenv/pyenv) para manejar los versiones

### Ejecuta

```bash
chmod +x setup.sh run.sh

./setup.sh

```

### Ejecuta de nuevo

```bash
./run.sh
```

## usar el APP

**necesitamos doc del proceso**

### Nota

los credenciales en .env de postgresQL vamos a mandar privado
