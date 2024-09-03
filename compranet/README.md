# Respaldo-de-datos

```Usage:
  main.py <file_path> <file_format> <start_index> <end_index> <dev_name>

Arguments:
    -h --help

    file_path:     The path to the file that you want to process. This should be a string specifying the location of the file on your system.

    file_format:   The format of the file you are working with. This should be either 'csv' or 'xlsx', indicating whether the file is a comma-separated values file or an Excel spreadsheet.

    start_index:   The starting index of the range within the DataFrame from which you will begin scraping URLs. This should be an integer indicating the first row of the DataFrame to process.

    end_index:     The ending index of the range within the DataFrame where you will stop scraping URLs. This should be an integer indicating the last row of the DataFrame to process, type all if you want all indexes.

    dev_name:      Your name

```

## Merge all outputs files

```Usage:
  merge_data.py <outputFolder_path> <dev_name>

Arguments:
    -h --help

    outputFolder_path:     Where you want to save Merge csv and xlsx files
    dev_name:              Your name

```
