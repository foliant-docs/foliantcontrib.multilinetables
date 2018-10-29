# Multiline and grid tables for Foliant

This preprocessor converts tables to multiline and grid format before creating document (very useful especially for pandoc processing). It helps to make tables in doc and pdf formats more proportional — column with more text in it will be more wide. Also it helps whith processing of extremely wide tables with pandoc. Convertation to the grid format allows arbitrary cell' content (multiple paragraphs, code blocks, lists, etc.).


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
        table_columns_to_scale: 3
        enable_hyphenation: false
        hyph_combination: '<br>'
        convert_to_grid: false
        targets:
            - docx
            - pdf
```

`min_table_width`
:   Wide markdown tables will be shrinked to this width in symbols. This parameter affects scaling - change it if table columns are merging.

`keep_narrow_tables`
:   If `true` narrow tables will not be stretched to minimum table width.

`table_columns_to_scale`
:   Minimum amount of columns to process the table.

`enable_hyphenation`
:   Switch breaking text in table cells with the tag set in `hyph_combination`. Good for lists, paragraphs, etc.

`hyph_combination`
:   Custom tag to break a text in multiline tables.

`convert_to_grid`
:   If `true` tables will be converted to the grid format, that allows arbitrary cell' content (multiple paragraphs, code blocks, lists, etc.).

`targets`
:   Allowed targets for the preprocessor. If not specified (by default), the preprocessor applies to all targets.


## Usage

Just add preprocessor to the project config and enjoy the result.
