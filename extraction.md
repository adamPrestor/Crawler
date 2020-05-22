# Data extraction

* Regular expressions and XPath queries for data extraction from `rtvslo.si`, `overstock.com` and `themoviedb.org`.
* Implementation of an automatic data extraction wrapper generator.

The report is available [here](report-extraction.pdf).

## Setup

The dependencies for the project are `numpy` and `lxml`. They can be installed automatically using the `implementation-extraction/requirements.txt` file.

```bash
pip install -r implementation-extraction/requirements.txt

# OR
pip install numpy lxml
```

## Run extraction

Move into the `implementation-extraction` dir.

Run regex extraction

```bash
python run-extraction.py A
```

Run XPath extraction

```bash
python run-extraction.py B
```

Run automatic wrapper generation

```bash
python run-extraction.py C
```

## Generated wrappers

Generated XML wrappers are available for each of the sites.
* [rtvslo.si](wrappers-extraction/rtvslo.si.xml)
* [overstock.com](wrappers-extraction/overstock.com.xml)
* [themoviedb.com](wrappers-extraction/themoviedb.org.xml)
* [test](wrappers-extraction/test.xml)

XPath output for generalized nodes is also available [here](wrappers-extraction/XPaths.txt).

