# respaldo-de-datos

## Desarrollo

* virtualenv .venv
* source .venv/bin/activate
* pip install -r compranet/requirements.txt
* playwright install

En este punto necesitarás un archivo de entrada en excel de formato excel
descargado de Compranet.

Ejecuta

```bash
$ python compranet/main.py archivo.xlsx xlsx <nombre> --sem=10
```

El `<nombre>` es un identificador usado para nombrar el archivo de salida.
