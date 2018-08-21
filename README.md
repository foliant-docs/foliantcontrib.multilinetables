# Multiline tables for Foliant

Multiline tables preprocessor converts tables in project markdown files to multiline format (very useful especially for pandoc processing). It helps to make tables in doc and pdf formats more proportional — column with more text in it will be more wide. Also it helps whith processing of extremely wide tables with pandoc.


## Installation

```shell
$ pip install foliantcontrib.multilinetables
```


## Config

To enable the preprocessor with default options, add `multilinetables` to `preprocessors` section in the project config:

```yaml
preprocessors:
  - multilinetables
```

The preprocessor has a number of options (best values set by default):

```yaml
preprocessors:
  - multilinetables:
      min_table_width: 100
      keep_narrow_tables: true
      table_columns_to_scale: 2
```

`min_table_width`
:   Wide markdown tables will be shrinked to this width in symbols.

`keep_narrow_tables`
:   If `true` narrow tables will not be stretched to minimum table width.

`table_columns_to_scale`
:   Minimum amount of columns to process the table.


## Usage

Just add preprocessor to the project config and enjoy the result.