# Script buscador tematicos pnt

python version 3.13

1- setup environment
2- install packages using `uv pip install -r requirements.txt` or `pip install -r requirements.txt`
3- install browser `PLAYWRIGHT_BROWSERS_PATH=0 playwright install chromium`

## Execute script

example

```bash
PLAYWRIGHT_BROWSERS_PATH=0 python run_loop.py -o "Ciudad de México" "Federación" "Hidalgo" "Jalisco" "Estado de México"

// you can add more estados / organos
```

**ps**: the script will run for all years and tematicos automatically
