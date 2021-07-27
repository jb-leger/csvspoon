# Copyright 2019, Jean-Benoist Leger <jb@leger.tf>
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import random
import math
import csv
import sys
import re


class CsvFileSpec:
    def __init__(self, filespec):
        regex = re.compile(r"^(?P<filename>[^:]+)(?::(?P<columns>.+))?$")
        match = regex.match(filespec)
        if not match:
            raise TypeError(
                "{filespec!r} can not be interpreted as {}".format(
                    self.__class__.__name__
                )
            )
        self._filename = match["filename"]
        if match["columns"] is not None:
            self._columns = tuple(match["columns"].split(","))
        else:
            self._columns = None

    @property
    def filename(self):
        return self._filename

    @property
    def columns(self):
        return self._columns


class CsvColumnsNotFound(Exception):
    pass


class ColFormat:
    def __init__(self, colfmt):
        if colfmt.count(":") != 1:
            raise TypeError("Not a col format for {}".format(self.__class__.__name__))
        colname, fmt = colfmt.split(":")
        if fmt and fmt[-1] in "bcdoxXn":
            self._convert = int
        elif fmt and fmt[-1] in "eEfFgGn%":
            self._convert = float
        else:
            self._convert = lambda x: x
        self._colname = colname
        self._fmt = "{:%s}" % fmt

    def format(self, row):
        if self._colname not in row:
            raise CsvColumnsNotFound("Column {} is not found.".format(self._colname))
        row[self._colname] = self._fmt.format(self._convert(row[self._colname]))


class NewColFormat(ColFormat):
    def __init__(self, colfmt):
        if ":" not in colfmt:
            colfmt += ":"
        ColFormat.__init__(self, colfmt)

    @property
    def colname(self):
        return self._colname


class ColType:
    def __init__(self, coltype):
        if coltype.count(":") != 1:
            raise TypeError("Not a col type for {}".format(self.__class__.__name__))
        colname, typename = coltype.split(":")
        self._colname = colname
        self._typename = typename

    def build_type(self, glob):
        self._type = eval(self._typename, glob)

    @property
    def get_coltype(self):
        return (self._colname, self._type)


def _cast_pseudo_numerical(value):
    for i in range(len(value), 0, -1):
        substr1, substr2 = value[0:i], value[i:]
        try:
            x = float(substr1)
        except ValueError:
            continue
        return (x, substr2)
    return (math.inf, value)


class NotValidContent(Exception):
    pass


def _cat_rowgen(gen1, gen2, only1, only2):
    for row in gen1:
        row.update({k: "" for k in only2})
        yield row
    for row in gen2:
        row.update({k: "" for k in only1})
        yield row


def _join_rowgen(gen1, dict_of_oth, common, left_added_keys, added_keys, left, right):
    if right:
        not_viewed_oth = set(dict_of_oth.keys())
    for l1 in gen1:
        value = tuple(l1[k] for k in common)
        if value in dict_of_oth:
            if right and value in not_viewed_oth:
                not_viewed_oth.remove(value)
            for l2 in dict_of_oth[value]:
                new_line = l1.copy()
                new_line.update(l2)
                yield new_line
        else:
            if left:
                new_line = dict(l1)
                new_line.update({k: "" for k in added_keys})
                yield new_line
    if right:
        for value in not_viewed_oth:
            for l2 in dict_of_oth[value]:
                new_line = dict(l2)
                new_line.update({k: "" for k in left_added_keys})
                yield new_line


def _aggregate_row_gen(new_fieldnames, stored_by_key_data_column, aggregation):
    fields_aggregation = set(colname for colname, _ in aggregation)
    for store in stored_by_key_data_column.values():
        row = {
            colname: store[colname][0]
            for colname in new_fieldnames
            if colname not in fields_aggregation
        }
        row.update({colname: func(store) for colname, func in aggregation})
        yield row


class ContentCsv:
    def __init__(
        self,
        *,
        filespec: CsvFileSpec = None,
        delim=",",
        encoding=None,
        _fieldnames=None,
        _rows=None
    ):
        self._applied = []
        self._types = {}
        self._new_fieldnames = []
        self._filters = []
        if filespec is not None:
            dialect = csv.excel
            dialect.delimiter = delim
            if filespec.filename == "-":
                f = sys.stdin
            else:
                f = open(filespec.filename, encoding=encoding)
            reader = csv.DictReader(f, dialect=dialect)
            if filespec.columns is None:
                self._fieldnames = reader.fieldnames
                fieldnames_map = {k: k for k in self._fieldnames}
            else:
                old_col_name = lambda col: col.split("=")[1] if "=" in col else col
                new_col_name = lambda col: col.split("=")[0] if "=" in col else col
                cols_not_found = set(
                    old_col_name(col) for col in filespec.columns
                ).difference(reader.fieldnames)
                if cols_not_found:
                    raise CsvColumnsNotFound(
                        "Columns {} are not found in {}.".format(
                            cols_not_found, filespec.filename
                        )
                    )
                self._fieldnames = [new_col_name(col) for col in filespec.columns]
                fieldnames_map = {
                    new_col_name(col): old_col_name(col) for col in filespec.columns
                }
            self._rows = (
                {c: row[fieldnames_map[c]] for c in self._fieldnames} for row in reader
            )
            self._valid = True
        else:
            if _fieldnames is None or _rows is None:
                raise TypeError("{} need filespec".format(self.__class__.__name__))
            # for internal use only
            self._rows = _rows
            self._fieldnames = _fieldnames
            self._valid = True

    @property
    def fieldnames(self):
        return tuple(self._fieldnames) + tuple(self._new_fieldnames)

    @property
    def rows(self):
        return self._get_rows()

    @property
    def rows_typed(self):
        return self._get_rows(typed=True)

    def _get_rows(self, typed=False):
        if not self._valid:
            raise NotValidContent
        self._valid = False
        computed_cols = set(colname for colname, _ in self._applied)
        for row in self._rows:
            if self._applied or self._filters or typed:
                typed_row = row.copy()
                typed_row.update(
                    {
                        c: t(row[c])
                        for c, t in self._types.items()
                        if c not in computed_cols
                    }
                )
            for colname, func in self._applied:
                row[colname] = func(typed_row)
                if colname in self._types:
                    typed_row[colname] = self._types[colname](row[colname])
                else:
                    typed_row[colname] = row[colname]
            filter_ok = True
            for func in self._filters:
                if not func(typed_row):
                    filter_ok = False
            if filter_ok:
                if typed:
                    yield typed_row
                else:
                    yield row

    def add_apply(self, colname, func):
        if colname not in self._fieldnames:
            self._new_fieldnames.append(colname)
        self._applied.append((colname, func))

    def add_filter(self, func):
        self._filters.append(func)

    def add_type(self, colname, typ):
        self._types[colname] = typ

    def join(self, oth, *, left=False, right=False, empty=False):
        common = set(self.fieldnames).intersection(set(oth.fieldnames))
        dict_of_oth = {}
        for l in oth.rows:
            value = tuple(l[k] for k in common)
            if not empty and all(not bool(x) for x in value):
                continue
            if value not in dict_of_oth:
                dict_of_oth[value] = []
            dict_of_oth[value].append(l)
        left_added_keys = [k for k in self.fieldnames if k not in common]
        added_keys = [k for k in oth.fieldnames if k not in common]
        new_fieldnames = list(self.fieldnames) + added_keys
        return ContentCsv(
            _fieldnames=new_fieldnames,
            _rows=_join_rowgen(
                self.rows, dict_of_oth, common, left_added_keys, added_keys, left, right
            ),
        )

    def concat(self, oth):
        only_self = set(self.fieldnames).difference(set(oth.fieldnames))
        only_oth = set(oth.fieldnames).difference(set(self.fieldnames))
        new_fieldnames = list(self.fieldnames) + [
            k for k in oth.fieldnames if k in only_oth
        ]
        return ContentCsv(
            _fieldnames=new_fieldnames,
            _rows=_cat_rowgen(self.rows, oth.rows, only_self, only_oth),
        )

    def aggregate(self, keys, aggregations):
        if aggregations is None:
            aggregations = ()
        if keys is None:
            keys = ()

        stored_by_key_data_column = {}
        for row in self._get_rows(typed=True):
            keyvalue = tuple(row[k] for k in keys)
            if keyvalue not in stored_by_key_data_column:
                store = {colname: [] for colname in self.fieldnames}
                stored_by_key_data_column[keyvalue] = store
            else:
                store = stored_by_key_data_column[keyvalue]
            for colname, value in row.items():
                store[colname].append(value)
        new_fieldnames = [
            colname
            for colname in self.fieldnames
            if all(
                len(set(store[colname])) == 1
                for store in stored_by_key_data_column.values()
            )
        ]
        new_fieldnames.extend(
            colname for colname, _ in aggregations if colname not in new_fieldnames
        )
        return ContentCsv(
            _fieldnames=new_fieldnames,
            _rows=_aggregate_row_gen(
                new_fieldnames, stored_by_key_data_column, aggregations
            ),
        )

    def sort(self, keys=tuple(), numeric=False, reverse=False, random_sort=False):
        if keys is None:
            keys = ()
        if numeric:
            cast_numeric = _cast_pseudo_numerical
        else:
            cast_numeric = lambda x: x

        if random_sort:
            append_random = lambda t: t + (random.random(),)
        else:
            append_random = lambda t: t

        key_fun = lambda row: append_random(tuple(cast_numeric(row[k]) for k in keys))

        return ContentCsv(
            _fieldnames=self.fieldnames,
            _rows=(row for row in sorted(self.rows, key=key_fun, reverse=reverse)),
        )

    def write(self, f, *, delim=",", fmt=None):
        dialect = csv.excel
        dialect.delimiter = delim
        writer = csv.DictWriter(f, self.fieldnames, dialect=dialect)
        writer.writeheader()
        for l in self.rows:
            row = l.copy()
            for colfmt in fmt:
                colfmt.format(row)
            writer.writerow(row)
