# Copyright 2019-2020, Jean-Benoist Leger <jb@leger.tf>
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

import functools
import argcomplete
import argparse
import textwrap
import sys
import os

from csvspoon import (
    ColFormat,
    ColType,
    ContentCsv,
    CsvColumnsNotFound,
    CsvFileSpec,
    NewColFormat,
    NotValidContent,
)


class _alternatively_NewColFormat_Formula:
    def __init__(self):
        self._alternatively = 0

    def __call__(self, value):
        if self._alternatively == 0:
            typ = NewColFormat
        else:
            typ = str
        self._alternatively += 1
        self._alternatively %= 2
        return typ(value)


def cli_example_main_doc():
    examples = cli_examples()
    section_doc = {
        "cat": "Concatenate CSV files",
        "apply": "Apply functions to add columns",
        "sort": "Sort CSV file",
        "filter": "Filter CSV from given conditions",
        "join": "Join CSV files",
        "aggregate": "Compute aggregation on CSV file",
    }
    doc = "## Cli example\n"
    for subcommand, section_title in section_doc.items():
        doc += "### csvspoon {}: {}\n".format(subcommand, section_title)
        incode = False
        initem = False
        for l in examples[subcommand].split("\n"):
            l = l.format(command="csvspoon {}".format(subcommand))
            if not l:
                continue
            if l.startswith(" " * 2):
                if initem:
                    initem = False
                if not incode:
                    incode = True
                    doc += "```\n"
                doc += l[2:] + "\n"
            else:
                if incode:
                    incode = False
                    doc += "```\n"
                if not initem:
                    initem = True
                    doc += " - "
                else:
                    doc += "   "
                doc += l + "\n"
        if incode:
            doc += "```\n"
    return doc


def cli_examples():
    examples = {
        "cat": textwrap.dedent(
            """\
            Change delimiter of a csv file:
              {command} -d "\\t" -u ";" file.csv > result.csv

            Change delimiter of a csv file with specified output:
              {command} -o result.csv -d "\\t" -u ";" file.csv

            Cat two csv files:
              {command} file1.csv file2.csv

            Reformat two columns of a csv files:
              {command} -f a_colname:5.1f -f another_colname:04d file.csv

            Cat one csv file, keeping only a column:
              {command} file.csv:a_col

            Cat two csv files, renaming a column on the second file:
              {command} file1.csv file2.csv:new_col=old_col,another_col
            """
        ),
        "join": textwrap.dedent(
            """\
            Operate NATURAL JOIN on two csv files:
              {command} file1.csv file2.csv

            Operate two NATURAL JOIN on three csv files:
              {command} file1.csv file2.csv file3.csv

            Operate LEFT JOIN on two csv files
              {command} -l file1.csv file2.csv

            Operate RIGHT JOIN on two csv files
              {command} -r file1.csv file2.csv

            Operate OUTER JOIN on two csv files
              {command} -lr file1.csv file2.csv
            """
        ),
        "apply": textwrap.dedent(
            """\
            Combine text columns by a formula:
              {command} -a name "lastname.upper()+' '+firstname.lower()" file.csv

            Sum to integer columns:
              {command} -t cola:int -t colb:int -a colsum "cola+colb" file.csv

            Sum to integer columns and format the result:
              {command} -t cola:int -t colb:int -a colsum:05d "cola+colb" file.csv

            Compute complex expression between columns:
              {command} \\
                      -b "import math" \\
                      -t x:float \\
                      -t y:float \\
                      -a norm "math.sqrt(x**2+y**2)" \\
                      file.csv

            Multiple computation can be done reusing newly created columns:
              {command} -t x:int -a x2p1 "x**2+1" -a x2p1m1 "x2p1-1" file.csv
            """
        ),
        "sort": textwrap.dedent(
            """\
            Sort csv file using column cola:
              {command} -k cola file.csv

            Sort csv file using columns cola and colb:
              {command} -k cola -k colb file.csv

            Sort csv file using numerical mode on column numcol:
              {command} -n -k numcol file.csv

            Shuffle csv file:
              {command} -R file.csv
            """
        ),
        "filter": textwrap.dedent(
            """\
            Filter csv file using two columns:
              {command} -a "lastname!=firstname" file.csv

            Chain filters on csv file:
              {command} \\
                      -a "lastname.startswith('Doe')" \\
                      -a "firstname.starswith('John')" \\
                      file.csv

            Filter csv file with float column price:
              {command} -t price:float -a "price>12.5" file.csv

            Filter csv file with complex expression:
              {command} \\
                      -b "import math" \\
                      -t x:float \\
                      -t y:float \\
                      -t z:float \\
                      -a "math.sqrt(x**2+y**2)>z" \\
                      file.csv
            """
        ),
        "aggregate": textwrap.dedent(
            """\
            Keeping unique lines, one line per group:
              {command} \\
                      -k group \\
                      file.csv

            Computing the total mean grade:
              {command} \\
                      --np \\
                      -t grade:float \\
                      -a meangrade "np.mean(grade)" \\
                      file.csv

            Computing the total mean grade specifing a format:
              {command} \\
                      --np \\
                      -t grade:float \\
                      -a meangrade:.2f "np.mean(grade)" \\
                      file.csv

            Computing the mean grade by group:
              {command} \\
                      --np \\
                      -t grade:float \\
                      -a meangrade "np.mean(grade)" \\
                      -k group \\
                      file.csv

            Computing the mean grade, median, standard deviation by group:
              {command} \\
                      --np \\
                      -t grade:float \\
                      -a meangrade "np.mean(grade)" \\
                      -a mediangrade "np.median(grade)" \\
                      -a stdgrade "np.std(grade)" \\
                      -k group \\
                      file.csv
            """
        ),
    }
    return examples


def parseargs():
    epilogs = {
        subcommand: (
            "Examples:\n" + textwrap.indent(example, " " * 2).format(command="%(prog)s")
        )
        for subcommand, example in cli_examples().items()
    }

    parser = argparse.ArgumentParser(
        description=textwrap.dedent(
            """
            A tool to manipulate csv files with headers.
            Again, again and again.
            """
        ),
        epilog="",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--version", action="version", version="", help=argparse.SUPPRESS
    )

    common_parser = argparse.ArgumentParser(add_help=False)
    common_parser.add_argument(
        "-d",
        "--delim",
        dest="delim",
        default=",",
        help="Input delimiter. (default: ',')",
    )
    common_parser.add_argument(
        "-o", "--output", dest="output", help="Output file, else output on stdout."
    )
    common_parser.add_argument(
        "-u",
        "--output-delim",
        dest="odelim",
        default=",",
        help="Output delimiter. (default: ',')",
    )
    common_parser.add_argument(
        "-f",
        "--format",
        dest="format",
        action="append",
        default=[],
        type=ColFormat,
        help="""
            Apply a format on a column on output. The argument must be a column
            name followed by a colon and a format specifier. e.g. "a_colname:5d"
            or "a_colname:+07.2f". This option can be specified multiple time to
            format different columns.
            """,
    )

    coltyped_parser = argparse.ArgumentParser(add_help=False)
    coltyped_parser.add_argument(
        "-b",
        "--before",
        action="append",
        default=[],
        help="""
            Run the following code before evaluate the expression on each row.
            Can be specified multiple times. (e.g. "import math").
            """,
    )
    coltyped_parser.add_argument(
        "--np",
        action="store_true",
        help="""
            Shortcut to `--before "import numpy as np"`
            """,
    )
    coltyped_parser.add_argument(
        "--sp",
        action="store_true",
        help="""
            Shortcut to `--np --before "import scipy as sp"`
            """,
    )
    coltyped_parser.add_argument(
        "-t",
        "--type",
        action="append",
        type=ColType,
        default=[],
        help="""
            Apply type conversion on specified command prior to expression. The
            argument must be a column name followed by a valid Python type. See
            "--before" to define non standard type. e.g. "a_column:int" or
            "a_column:float". This option can be specified multiple time to type
            different columns.
            """,
    )

    input_filespec_help = """
        Input file specification. {} Can be a filename (e.g. "file.csv"), a
        filename followed a semicolon and column names separated by commas (e.g.
        "file.csv:a_colname,another_colname"). A column can be renamed while
        reading the file (e.g. "file.csv:a_colname,new_colname=old_colname").
        When column names are specified, only these columns are used, with the
        provided order.
        """

    subparsers = parser.add_subparsers(
        dest="subcommand", title="subcommands", required=True
    )

    # cat
    parser_cat = subparsers.add_parser(
        "cat",
        help="Concatenate csv files.",
        description=textwrap.dedent(
            """
            Concatenate csv files.
            Empty fields added if some columns do not exist in all files
            This method is completely streamed and no data is stored in memory.
            """
        ),
        parents=(common_parser,),
        epilog=epilogs["cat"],
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser_cat.add_argument(
        "input",
        help=input_filespec_help.format(
            """
            If no input file is provided, stdin is used as first input file,
            otherwise use explicitly "-" for stdin.
            """
        ),
        nargs="*",
        type=CsvFileSpec,
    )

    # apply
    parser_apply = subparsers.add_parser(
        "apply",
        help="Apply a formula to compute a new column.",
        description=textwrap.dedent(
            """
            Apply a formula to compute a new column.
            The formula must be a valid python expression evaluated on each row.
            This method is completely streamed and no data is stored in memory.
            """
        ),
        parents=(common_parser, coltyped_parser),
        epilog=epilogs["apply"],
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser_apply.add_argument(
        "-a",
        "--add",
        "--add-column",
        dest="added",
        nargs=2,
        action="append",
        metavar=("COLSPEC", "FORMULA"),
        type=_alternatively_NewColFormat_Formula(),
        help="""
            Append a new column (or update existing one). Take two argument,
            COLSPEC and FORMULA. COLSPEC is the name of the created column
            obtained by appling the formula. The column is remplaced if already
            exists. The COLSPEC can also contains a colon and a format
            specifier, see "--format" for example. FORMULA must be a valid
            python expression. For the current row, columns values are accessible
            as local variable.  e.g. "a_colname + other_colname" or
            "min(a_colname, other_colname)".  See "--type" for typing other
            columns and "--before" for run code before evaluating expression.
            Can be specified multiple time.
            """,
    )
    parser_apply.add_argument(
        "input",
        help=input_filespec_help.format(
            """
            If no input file is provided, stdin is used as input file.
            """
        ),
        type=CsvFileSpec,
        nargs="?",
    )

    # filter
    parser_filter = subparsers.add_parser(
        "filter",
        help="Filter a csv with a formula.",
        description=textwrap.dedent(
            """
            Evaluate a formula on each row, and keep only rows where the formula
            is evaluated True.
            The formula must be a valid python expression evaluated on each row.
            This method is completely streamed and no data is stored in memory.
            """
        ),
        parents=(common_parser, coltyped_parser),
        epilog=epilogs["filter"],
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser_filter.add_argument(
        "-a",
        "--add",
        "--add-filter",
        dest="added",
        action="append",
        metavar="FILTER_FORMULA",
        help="""
            FORMULA must be a valid python expression, which is casted to
            bool(). For the current row, columns values are accessible as
            local variable.  e.g.  "a_colname > other_colname" or
            "a_colname=='fixedvalue'".  See "--type" for typing other columns
            and "--before" for run code before evaluating filter expression. Can
            be specified multiple time.
            """,
    )
    parser_filter.add_argument(
        "input",
        help=input_filespec_help.format(
            """
            If no input file is provided, stdin is used as input file.
            """
        ),
        type=CsvFileSpec,
        nargs="?",
    )

    # sort
    parser_sort = subparsers.add_parser(
        "sort",
        help="Sort csv files.",
        description=textwrap.dedent(
            """
            Sort csv file.
            Warning: this method need to store in memory all the input csv file.
            """
        ),
        parents=(common_parser,),
        epilog=epilogs["sort"],
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser_sort.add_argument(
        "-k",
        "--key",
        dest="keys",
        action="append",
        help="""
            Column used for sorting. Can be specified multiple time.
            """,
    )
    parser_sort.add_argument(
        "-n",
        "--numeric-sort",
        dest="numeric",
        action="store_true",
        help="Compare according to numerical value.",
    )
    parser_sort.add_argument(
        "-r",
        "--reverse",
        dest="reverse",
        action="store_true",
        help="Reverse the result of comparisons.",
    )
    parser_sort.add_argument(
        "-R",
        "--random-sort",
        dest="random",
        action="store_true",
        help="""
            Shuffle. If key specified, shuffle is performed inside lines with
            the same key.
            """,
    )
    parser_sort.add_argument(
        "input",
        help=input_filespec_help.format(
            """
            If no input file is provided, stdin is used as input file.
            """
        ),
        type=CsvFileSpec,
        nargs="?",
    )

    # join
    parser_join = subparsers.add_parser(
        "join",
        help="Operate join on csv files",
        description=textwrap.dedent(
            """
            Natural join of csv files.
            Joins are performed from left to right.
            Warning: this method need to store in memory all csv except the
                first which is streamed.

            If neither --left or --right specified, inner join is realized. For
            complete outer join, use --left and --right together.
            """
        ),
        parents=(common_parser,),
        epilog=epilogs["join"],
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser_join.add_argument(
        "-l",
        "--left",
        action="store_true",
        help="""
            Perform left join. If more than two files are provided, each join in
            a left join. Can be used with `-r` to obtain a outer join.
            """,
    )
    parser_join.add_argument(
        "-r",
        "--right",
        action="store_true",
        help="""
            Perform right join. If more than two files are provided, each join in
            a right join. Can be used with `-l` to obtain a outer join.
            """,
    )
    parser_join.add_argument(
        "-e",
        "--empty",
        action="store_true",
        help="""
            Indicate than empty field have to be considered as a value.
            """,
    )
    parser_join.add_argument(
        "input",
        help=input_filespec_help.format(
            """
            If less than two input files are provided, stdin is used as first
            input file, otherwise use explicitly "-" for stdin.
            """
        ),
        nargs="+",
        type=CsvFileSpec,
    )

    # aggregate
    parser_aggregate = subparsers.add_parser(
        "aggregate",
        help="Apply a aggregation formula to compute a new column.",
        description=textwrap.dedent(
            """
            Apply a formula to compute a new column.
            The formula must be a valid python expression evaluated for each
            groupped row.
            Only aggregation or column with non ambiguous values are keeped.
            Warning: this method need to store in memory all the input csv file.
            """
        ),
        parents=(common_parser, coltyped_parser),
        epilog=epilogs["aggregate"],
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser_aggregate.add_argument(
        "-a",
        "--add",
        "--add-aggregation",
        dest="added",
        nargs=2,
        action="append",
        metavar=("COLSPEC", "FORMULA"),
        type=_alternatively_NewColFormat_Formula(),
        help="""
            Append a new colon by aggregation of values. Take two argument,
            COLSPEC and FORMULA. COLSPEC is the name of the created column
            obtained the aggregation. The COLSPEC can also contains a colon and a format
            specifier, see "--format" for example. FORMULA must be a valid
            python expression. For each column, list of values to aggregate are
            accessible as local variable. The formula should return a single
            value.
            e.g. "sum(a_colname) + sum(other_colname)".
            See "--type" for typing other columns and "--before" for run code
            before evaluating expression. Can be specified multiple time.
            """,
    )
    parser_aggregate.add_argument(
        "-k",
        "--key",
        dest="keys",
        action="append",
        help="""
            Column used groupping the aggregate. Can be specified multiple time.
            Similar to "GROUP BY" in SQL.
            """,
    )
    parser_aggregate.add_argument(
        "input",
        help=input_filespec_help.format(
            """
            If no input file is provided, stdin is used as input file.
            """
        ),
        type=CsvFileSpec,
        nargs="?",
    )

    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    return args


def write_result(args, result):
    result.write(
        open(args.output, "w") if args.output else sys.stdout,
        delim=args.odelim,
        fmt=args.format,
    )


def coltyped_common(args, inputstream):
    fake_global = {"__name__": "__main__"}
    if args.np or args.sp:
        ast = compile("import numpy as np", "<string>", "exec")
        exec(ast, fake_global)
    if args.sp:
        ast = compile("import scipy as sp", "<string>", "exec")
        exec(ast, fake_global)
    for before in args.before:
        ast = compile(before, "<string>", "exec")
        exec(ast, fake_global)
    for t in args.type:
        t.build_type(fake_global)
        inputstream.add_type(*t.get_coltype)
    return fake_global


def main_aggregate(args):
    if args.input is None:
        args.input = CsvFileSpec("-")
    input_csv = ContentCsv(filespec=args.input, delim=args.delim)
    fake_global = coltyped_common(args, input_csv)
    if args.added is None:
        args.added = []

    for colspec, _ in args.added:
        args.format.insert(0, colspec)

    aggregations = [
        (
            colspec.colname,
            (lambda f: lambda store: eval(f, fake_global, store))(formula),
        )
        for colspec, formula in args.added
    ]

    result = input_csv.aggregate(keys=args.keys, aggregations=aggregations)
    write_result(args, result)


def main_sort(args):
    if args.input is None:
        args.input = CsvFileSpec("-")
    result = ContentCsv(filespec=args.input, delim=args.delim).sort(
        keys=args.keys,
        numeric=args.numeric,
        reverse=args.reverse,
        random_sort=args.random,
    )
    write_result(args, result)


def main_filter(args):
    if args.input is None:
        args.input = CsvFileSpec("-")
    if args.added is None:
        args.added = []
    result = ContentCsv(filespec=args.input, delim=args.delim)
    fake_global = coltyped_common(args, result)

    for formula in args.added:
        result.add_filter(func=(lambda f: lambda r: eval(f, fake_global, r))(formula))

    write_result(args, result)


def main_apply(args):
    if args.input is None:
        args.input = CsvFileSpec("-")
    if args.added is None:
        args.added = []
    result = ContentCsv(filespec=args.input, delim=args.delim)
    fake_global = coltyped_common(args, result)

    for colspec, formula in args.added:
        result.add_apply(
            colname=colspec.colname,
            func=(lambda f: lambda r: eval(f, fake_global, r))(formula),
        )
        args.format.insert(0, colspec)

    write_result(args, result)


def main_join(args):
    if len(args.input) < 2:
        args.input.insert(0, CsvFileSpec("-"))
    result = functools.reduce(
        lambda x, y: x.join(y, left=args.left, right=args.right, empty=args.empty),
        (ContentCsv(filespec=fn, delim=args.delim) for fn in args.input),
    )
    write_result(args, result)


def main_cat(args):
    if len(args.input) == 0:
        args.input.insert(0, CsvFileSpec("-"))
    result = functools.reduce(
        lambda x, y: x.concat(y),
        (ContentCsv(filespec=fn, delim=args.delim) for fn in args.input),
    )
    write_result(args, result)


def main():
    args = parseargs()

    try:
        if args.subcommand == "join":
            main_join(args)
        if args.subcommand == "cat":
            main_cat(args)
        if args.subcommand == "apply":
            main_apply(args)
        if args.subcommand == "sort":
            main_sort(args)
        if args.subcommand == "filter":
            main_filter(args)
        if args.subcommand == "aggregate":
            main_aggregate(args)
        sys.stdout.flush()
    except BrokenPipeError:
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        sys.exit(1)


if __name__ == "__main__":
    main()
