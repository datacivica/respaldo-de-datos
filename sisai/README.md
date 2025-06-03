# Archivos Adjunto SISAI

## Notas de uso

- si estuviste bajando temático no es necesario hacer instalaciones, si no para instalacion instalaciones porfa ver el [Readme](../README.md)

- para usar este script necesita poner el archivo json por ej(01_2024.json ) en la root de la carpeta aquí no en un carpeta
  asi si debe ser sisai root:
  sisai/

```bash
sisai
    ├── 13_2024.json
    ├── README.md
    ├── archivo_adjunto_sisai_13_2024
    |──   └── .zips
    ├── check.py
    ├── download_files_PNT_SISAI.log
    ├── sisai
    │   └── scrapingArchivosSISAI.py
    ├── solicitudes.py
    └── state_index_SISAI_13_2024.json

```

- el script baja 10 archivo en el mismo tiempo
- navegador sin cera y no puedes usar el compu mientras

## Subir archivos JSON a Google Drive

Subir a Google Drive
[SISAI](https://drive.google.com/drive/folders/1zu8o8am0xe654jBD2NqU--4EMrQzcXuy)

**Tareas:**

| Región | Responsable | Enlace                                                                                                 |
| ------ | ----------- | ------------------------------------------------------------------------------------------------------ |
| Norte  | Ric         | [Ver carpeta](https://drive.google.com/drive/folders/1_LioAwDyUPG3eCXMzouFnxL5jHCU3dlo?usp=drive_link) |
| Centro | Basem       | [Ver carpeta](https://drive.google.com/drive/folders/1vFvoDpH3zxjpPfV7qOnLoOIk0nZiot2i?usp=drive_link) |
| Sur    | Abraham     | [Ver carpeta](https://drive.google.com/drive/folders/1_t6c2WGB3NmbAXaUOpergXkVBXDnvvzk?usp=drive_link) |

## Execute script

```bash
cd sisai
```

### Cli helper

```bash
usage: solicitudes.py [-h] [-d DOWNLOADS_PATH] file_path

Procesar un archivo y descargar adjuntos usando Scraping DataFrame. Este script toma un archivo JSON con registros SISAI y descarga los archivos adjuntos especificados.

positional arguments:
  file_path             La ruta al archivo que desea procesar. Este archivo debe ser un JSON con registros SISAI.

options:
  -h, --help            show this help message and exit
  -d, --downloads_path DOWNLOADS_PATH
                        Ruta donde se guardarán los archivos descargados. Por defecto es None, lo que significa que se guardarán en el directorio actual.
```

### Python

`PLAYWRIGHT_BROWSERS_PATH=0  python3 solicitudes.py 01_2024.json`
_puedes agregar -d para cambiar la ruta de descarga_

### UV

`PLAYWRIGHT_BROWSERS_PATH=0  uv run solicitudes.py 01_2024.json`
_puedes agregar -d para cambiar la ruta de descarga_

## Hacer check despues de terminar

```bash
python3 check.py 33_2018.json archivo_adjunto_sisai_33_2018 0 46220 ── index final desde state_index_SISAI_******.json
                     └── json file       └── carpeta        └──index de empezar
```

Python

```bash
python3 check.py 33_2018.json archivo_adjunto_sisai_33_2018 0 135000
```

UV

```bash
uv run check.py 33_2018.json archivo_adjunto_sisai_33_2018 0 135000
```

⚠️ si no puede hacer check del folio unico porfa revisa `def replaceIdentifier(x: str):` en check.py si hay el nombre corto de entidad.
