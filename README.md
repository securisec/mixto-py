# mixto-py

The python library for Mixto. 

## Install

```
pip install mixto-py
```

For dev instances, clone this repo and run from inside of the directory:

```
pip install -e .
```

## Usage

```py
from mixto import Mixto
```

The main class can be instantiated in two ways:

```py
m = Mixto()
# or
m = Mixto(host="https://mixto_host", api_key="youapikey")
```

## Example

```py
from mixto import Mixto

m = Mixto()


```
