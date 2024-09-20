# Respaldo-de-datos

Este script está diseñado para realizar web scraping de URLs listadas en tablas CSV o XLSX. Utiliza playwright y asyncio para manejar múltiples URLs de forma concurrente, lo que mejora significativamente la velocidad del proceso de scraping.

El script no solo extrae datos de las URLs, sino que también utiliza el paquete playwright para navegar e interactuar con las páginas web. Esto le permite descargar todos los archivos vinculados en estos sitios. Los métodos querySelector y click del paquete playwright se utilizan para localizar y iniciar la descarga de cada enlace de archivo en el sitio.

Este script es especialmente útil para tareas que involucran scraping de múltiples URLs y descarga de archivos, como la recopilación de datos para investigación o análisis, o la automatización de la descarga de archivos de sitios web. Al utilizar programación asíncrona y el paquete playwright, el script puede manejar un gran número de URLs y archivos de manera eficiente y rápida.

## Capacidades

El tiempo de ejecución de este script puede variar significativamente dependiendo de varios factores, incluyendo las capacidades del dispositivo utilizado, la velocidad y la fiabilidad de la conexión a Internet, y el tamaño de los datos que se están raspando.

Para gestionar el número de conexiones simultáneas y optimizar el rendimiento, este script utiliza un método de semáforo de la biblioteca asyncio. Un semáforo es un primitivo de sincronización que limita el número de tareas concurrentes que se pueden ejecutar. De forma predeterminada, el script utiliza un tamaño de semáforo de 10 para limitar el número de conexiones simultáneas a la piscina. Esto significa que hasta 10 URLs se rascarán simultáneamente en cualquier momento.

El tamaño del semáforo se puede ajustar para satisfacer las necesidades específicas de la tarea y los recursos disponibles. El tamaño del semáforo se puede cambiar utilizando la bandera `--sem`, seguida del número deseado de semáforos, que va de 1 a 10. Un tamaño de semáforo mayor permitirá más conexiones simultáneas, lo que puede resultar en tiempos de raspado más rápidos, pero también puede poner una mayor carga en los recursos del dispositivo y la conexión a Internet. Por el contrario, un tamaño de semáforo más pequeño resultará en tiempos de raspado más lentos, pero será más amigable con los recursos y menos propenso a causar problemas con la conexión a Internet.

En última instancia, el tamaño de semáforo óptimo dependerá de los requisitos específicos de la tarea y los recursos disponibles. Es posible que sea necesario experimentar con diferentes tamaños de semáforo para determinar el mejor equilibrio entre velocidad, uso de recursos y fiabilidad.

## instalaciónes

```env
python3 -m venv env
```

```activate
source env/bin/activate
```

```pip
pip3 install -r requirements.txt
```

## Argumentos

`-h --help`: Muestra esta pantalla de uso.
`file_path`: La ruta al archivo que desea procesar. Debe ser una cadena que especifique la ubicación del archivo en su sistema.
`file_format`: El formato del archivo con el que está trabajando. Debe ser 'csv' o 'xlsx', lo que indica si el archivo es un archivo de valores separados por comas o una hoja de cálculo de Excel.
`name`: Nombre de referencia.

## Opciones

`--sem=<sem>`: Esta bandera se utiliza para gestionar el número de conexiones simultáneas y optimizar el rendimiento. El valor de `<sem>` representa el número máximo de conexiones simultáneas que el script realizará al servidor. Esto puede ayudar a evitar la sobrecarga del servidor y mejorar la velocidad del proceso de scraping. Por defecto, `10`.
`--col=<column_name>`: Esta bandera se utiliza para el nombre de la columna de URL en pandas DataFrame.
`--outputcsv=<csv>`: Esta bandera se utiliza para especificar el nombre del archivo de datos de salida. El valor de `<csv>` debe ser una cadena que represente el nombre deseado del archivo de salida, incluyendo la extensión del archivo (por ejemplo, `--outputcsv=my_data.csv`). Por defecto, `output_<name>.csv`.
`--downloads_path=<downloads_path>`: Esta bandera se utiliza para especificar la ruta donde se guardarán los archivos que se descargan durante el proceso de scraping. El valor de `<downloads_path>` debe ser una cadena que represente la ruta de archivo deseada (por ejemplo, `--downloads_path=/home/user/downloads`). Por defecto, `your_project_path/downloads`.

## Uso

```Usage:
Uso:
  python3 main.py file_path file_format name --sem=sem --output_file_name=output_file_name --downloads_path=downloads_path --col=column_name
```

## Apoyo

Jorge Andrade:<jorge.andrade@datacivica.org>
Basem Hamza: <basem.hamza@datacivica.org>
