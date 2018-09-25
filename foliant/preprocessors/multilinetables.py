'''
Preprocessor for Foliant documentation authoring tool.
Makes markdown tables multiline before pandoc processing.
'''

import re
from pathlib import Path

from foliant.preprocessors.base import BasePreprocessor


class Preprocessor(BasePreprocessor):
    defaults = {
        'min_table_width': 100,
        'keep_narrow_tables': True,
        'table_columns_to_scale': 3,
        'enable_hyphenation': True,
        'hyph_combination': '<br>',
        'targets': [],
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.logger = self.logger.getChild('maketablesmultiline')

        self.logger.debug(f'Preprocessor inited: {self.__dict__}')

        self._min_table_width = self.options['min_table_width']
        self._keep_narrow_tables = self.options['keep_narrow_tables']
        self._table_columns_to_scale = self.options['table_columns_to_scale']
        self._enable_hyphenation = self.options['enable_hyphenation']
        self._hyph_combination = self.options['hyph_combination']

    def _if_table_is_table(self, new_file_data, table_to_scale):
        if len(table_to_scale) > 2 and not re.search('\w', table_to_scale[1]):
            new_file_data = self._process_table(new_file_data, table_to_scale)
        else:
            for line in table_to_scale:
                new_file_data.append(''.join(map(str, line)))

        return new_file_data

    def _process_table(self, new_file_data, table_to_scale):
        for i, line in enumerate(table_to_scale):
            table_to_scale[i] = line.split('|')
        table_to_scale = self._prepare_table(table_to_scale)
        scaled_table = self._scale_table(table_to_scale)
        table_to_scale = []
        for line in scaled_table:
            new_file_data.append(line)

        return new_file_data

    def _prepare_table(self, table):
        table = self._remove_empty_columns(table, 'left_side')
        table = self._remove_empty_columns(table, 'right_side')
        table = self._clear_spaces(table)

        return table

    def _remove_empty_columns(self, table_to_scale, side):
        new_iteration = True

        while new_iteration:
            if side == 'left_side':
                index = 0
            if side == 'right_side':
                index = len(table_to_scale[0])-1

            if all(table_to_scale[element][index] in ('', '\n') for element in range(len(table_to_scale))):
                new_table_to_scale = []
                for row in table_to_scale:
                    row.pop(index)
                    new_table_to_scale.append(row)
            else:
                new_iteration = False

        return table_to_scale

    def _clear_spaces(self, table_to_scale):
        new_table_to_scale = []

        for row in table_to_scale:
            new_row = []
            for item in row:
                new_row.append(item.strip())
            new_table_to_scale.append(new_row)

        return new_table_to_scale

    def _scale_cell(self, width, cell_to_cut, scaled_cell):
        if len(cell_to_cut) < width:
            scaled_cell.append(cell_to_cut)
        else:
            splitted_cell_part = cell_to_cut.split(' ')
            cell_string = ''

            for word in splitted_cell_part:
                if (len(cell_string) + len(word)) < width:
                    cell_string = cell_string + ' ' + word
                else:
                    scaled_cell.append(cell_string.strip())
                    cell_string = word
            scaled_cell.append(cell_string.strip())

        return scaled_cell

    def _scale_table(self, table_to_scale):
        table_to_scale.pop(1)
        columns = list(zip(*table_to_scale))

        min_column_widths = [0 for i in range(len(columns))]
        max_cell_lenghts = [0 for i in range(len(columns))]
        column_volumes = [0 for i in range(len(columns))]

        for i, column in enumerate(columns):
            for cell in column:
                max_cell_lenghts[i] = max(max_cell_lenghts[i], len(cell) + 1)
                column_volumes[i] += len(cell)
                for item in cell.split(' '):
                    if len(item) >= min_column_widths[i]:
                        min_column_widths[i] = len(item) + 1

        table_width = max(sum(min_column_widths) + len(columns) - 1, self._min_table_width)
        if self._keep_narrow_tables and sum(max_cell_lenghts) < table_width:
            table_width = sum(max_cell_lenghts) + len(columns) - 1

        column_widths = [0 for i in range(len(columns))]
        rest_of_columns_width = 0
        scalable_volume = 0
        for i, column in enumerate(min_column_widths):
            if max_cell_lenghts[i] <= min_column_widths[i]:
                column_widths[i] = min_column_widths[i]
            else:
                rest_of_columns_width += min_column_widths[i]
                scalable_volume += column_volumes[i]

        rest_of_table_width = table_width - sum(column_widths) - len(columns) + 1

        for i, column in enumerate(column_widths):
            if column_widths[i] == 0:
                column_widths[i] = min_column_widths[i] + round((rest_of_table_width - rest_of_columns_width) * column_volumes[i] / scalable_volume)

        table_width = sum(column_widths) + len(columns) - 1

        scaled_table = []
        is_header = True
        header_hight = 0

        for row in table_to_scale:
            scaled_row = [[] for i in range(len(row))]
            cell_hight = 1

            for column_number, cell in enumerate(row):
                scaled_cell = []
                if self._enable_hyphenation and self._hyph_combination in cell:
                    cell = cell.split(self._hyph_combination)
                    for cell_part in cell:
                        scaled_cell = self._scale_cell(column_widths[column_number], cell_part, scaled_cell)
                else:
                    scaled_cell = self._scale_cell(column_widths[column_number], cell, scaled_cell)

                if len(scaled_cell) > cell_hight:
                    cell_hight = len(scaled_cell)

                scaled_row[column_number] = scaled_cell

            if cell_hight > 1:
                for cell in scaled_row:
                    if len(cell) < cell_hight:
                        for i in range(cell_hight - len(cell)):
                            cell.append('')

            if is_header:
                header_hight = cell_hight
                is_header = False

            strings = ['' for i in range(cell_hight)]

            for column_number, column in enumerate(scaled_row):
                for i in range(cell_hight):
                    strings[i] = strings[i] + column[i] + ' ' * ((column_widths[column_number] - len(column[i]) + 1))
            for i in range(len(strings)):
                strings[i] = strings[i][:-1]

            for string in strings:
                scaled_table.append(string)
                scaled_table.append('\n')
            scaled_table.append('\n')

        scaled_table.insert(0, ''.join(('-' * table_width, '\n')))
        scaled_table.pop(header_hight*2)
        header_separator = ''

        for column in column_widths:
            header_separator = header_separator + '-' * column + ' '

        header_separator = header_separator.strip()
        header_separator = '\n' + header_separator
        scaled_table.insert(header_hight*2, header_separator)

        scaled_table.insert(len(scaled_table) - 1, ''.join(('-' * table_width, '\n')))

        return scaled_table

    def apply(self):
        self.logger.info('Applying preprocessor')

        if not self.options['targets'] or self.context['target'] in self.options['targets']:

            for markdown_file_path in self.working_dir.rglob('*.md'):
                self.logger.debug(f'Processing Markdown file: {markdown_file_path}')

                with open(markdown_file_path, encoding='utf8') as file_to_read:
                    file_data = list(file_to_read)

                new_file_data = []
                table_to_scale = []
                scaled_table = []
                table_found = False

                for string in file_data:

                    if '|' not in string or len([cell for cell in string.split('|') if cell]) < self._table_columns_to_scale:
                        if table_found:
                            table_found = False
                            new_file_data = self._if_table_is_table(new_file_data, table_to_scale)
                        table_to_scale = []

                        new_file_data.append(string)

                    else:
                        table_found = True
                        table_to_scale.append(string)
                        for item in table_to_scale[len(table_to_scale)-1]:
                            item.strip()

                if table_found:
                    new_file_data = self._if_table_is_table(new_file_data, table_to_scale)

                with open(markdown_file_path, 'w', encoding="utf-8") as file_to_write:
                    for string in new_file_data:
                        file_to_write.write(string)

        self.logger.info('Preprocessor applied')
