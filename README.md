# csvspoon: a tool to manipulate csv file with headers

Again, again, and again.

## Installing

From pypi:

```
pip3 install csvspoon
```

Or developer version:

```
git clone <this repo>
cd csvspoon
pip3 install -e .
```

## Enable completion (for bash or other shells using bash-completion)

```
mkdir -p ~/.local/share/bash-completion/completions
register-python-argcomplete csvspoon > ~/.local/share/bash-completion/completions/csvspoon
```

## Python module

All methods and functions are accessible in the python module.
## Cli usage
```
usage: csvspoon [-h] {cat,apply,filter,sort,join,aggregate} ...

A tool to manipulate csv files with headers.
Again, again and again.

optional arguments:
  -h, --help            show this help message and exit

subcommands:
  {cat,apply,filter,sort,join,aggregate}
    cat                 Concatenate csv files.
    apply               Apply a formula to compute a new column.
    filter              Filter a csv with a formula.
    sort                Sort csv files.
    join                Operate join on csv files
    aggregate           Apply a aggregation formula to compute a new column.

```
## `csvspoon cat`
```
usage: csvspoon cat [-h] [-d DELIM] [-c INPUTENC] [-o OUTPUT] [-u ODELIM]
                    [-C OUTPUTENC] [-f FORMAT]
                    [input ...]

Concatenate csv files.
Empty fields added if some columns do not exist in all files
This method is completely streamed and no data is stored in memory.

positional arguments:
  input                 Input file specification. If no input file is
                        provided, stdin is used as first input file, otherwise
                        use explicitly "-" for stdin. Can be a filename (e.g.
                        "file.csv"), a filename followed a semicolon and
                        column names separated by commas (e.g.
                        "file.csv:a_colname,another_colname"). A column can be
                        renamed while reading the file (e.g.
                        "file.csv:a_colname,new_colname=old_colname"). When
                        column names are specified, only these columns are
                        used, with the provided order.

optional arguments:
  -h, --help            show this help message and exit
  -d DELIM, --delim DELIM
                        Input delimiter. (default: ',')
  -c INPUTENC, --inputenc INPUTENC
                        Input encoding. (default: 'utf8')
  -o OUTPUT, --output OUTPUT
                        Output file, else output on stdout.
  -u ODELIM, --output-delim ODELIM
                        Output delimiter. (default: ',')
  -C OUTPUTENC, --outputenc OUTPUTENC
                        Output encoding. (default: 'utf8')
  -f FORMAT, --format FORMAT
                        Apply a format on a column on output. The argument
                        must be a column name followed by a colon and a format
                        specifier. e.g. "a_colname:5d" or "a_colname:+07.2f".
                        This option can be specified multiple time to format
                        different columns.

Examples:
  Change delimiter of a csv file:
    csvspoon cat -d "\t" -u ";" file.csv > result.csv

  Change delimiter of a csv file with specified output:
    csvspoon cat -o result.csv -d "\t" -u ";" file.csv

  Cat two csv files:
    csvspoon cat file1.csv file2.csv

  Reformat two columns of a csv files:
    csvspoon cat -f a_colname:5.1f -f another_colname:04d file.csv

  Cat one csv file, keeping only a column:
    csvspoon cat file.csv:a_col

  Cat two csv files, renaming a column on the second file:
    csvspoon cat file1.csv file2.csv:new_col=old_col,another_col

```
## `csvspoon apply`
```
usage: csvspoon apply [-h] [-d DELIM] [-c INPUTENC] [-o OUTPUT] [-u ODELIM]
                      [-C OUTPUTENC] [-f FORMAT] [-b BEFORE] [--np] [--sp]
                      [-t TYPE] [-a COLSPEC FORMULA]
                      [input]

Apply a formula to compute a new column.
The formula must be a valid python expression evaluated on each row.
This method is completely streamed and no data is stored in memory.

positional arguments:
  input                 Input file specification. If no input file is
                        provided, stdin is used as input file. Can be a
                        filename (e.g. "file.csv"), a filename followed a
                        semicolon and column names separated by commas (e.g.
                        "file.csv:a_colname,another_colname"). A column can be
                        renamed while reading the file (e.g.
                        "file.csv:a_colname,new_colname=old_colname"). When
                        column names are specified, only these columns are
                        used, with the provided order.

optional arguments:
  -h, --help            show this help message and exit
  -d DELIM, --delim DELIM
                        Input delimiter. (default: ',')
  -c INPUTENC, --inputenc INPUTENC
                        Input encoding. (default: 'utf8')
  -o OUTPUT, --output OUTPUT
                        Output file, else output on stdout.
  -u ODELIM, --output-delim ODELIM
                        Output delimiter. (default: ',')
  -C OUTPUTENC, --outputenc OUTPUTENC
                        Output encoding. (default: 'utf8')
  -f FORMAT, --format FORMAT
                        Apply a format on a column on output. The argument
                        must be a column name followed by a colon and a format
                        specifier. e.g. "a_colname:5d" or "a_colname:+07.2f".
                        This option can be specified multiple time to format
                        different columns.
  -b BEFORE, --before BEFORE
                        Run the following code before evaluate the expression
                        on each row. Can be specified multiple times. (e.g.
                        "import math").
  --np                  Shortcut to `--before "import numpy as np"`
  --sp                  Shortcut to `--np --before "import scipy as sp"`
  -t TYPE, --type TYPE  Apply type conversion on specified command prior to
                        expression. The argument must be a column name
                        followed by a valid Python type. See "--before" to
                        define non standard type. e.g. "a_column:int" or
                        "a_column:float". This option can be specified
                        multiple time to type different columns.
  -a COLSPEC FORMULA, --add COLSPEC FORMULA, --add-column COLSPEC FORMULA
                        Append a new column (or update existing one). Take two
                        argument, COLSPEC and FORMULA. COLSPEC is the name of
                        the created column obtained by appling the formula.
                        The column is remplaced if already exists. The COLSPEC
                        can also contains a colon and a format specifier, see
                        "--format" for example. FORMULA must be a valid python
                        expression. For the current row, columns values are
                        accessible as local variable. e.g. "a_colname +
                        other_colname" or "min(a_colname, other_colname)". See
                        "--type" for typing other columns and "--before" for
                        run code before evaluating expression. Can be
                        specified multiple time.

Examples:
  Combine text columns by a formula:
    csvspoon apply -a name "lastname.upper()+' '+firstname.lower()" file.csv

  Sum to integer columns:
    csvspoon apply -t cola:int -t colb:int -a colsum "cola+colb" file.csv

  Sum to integer columns and format the result:
    csvspoon apply -t cola:int -t colb:int -a colsum:05d "cola+colb" file.csv

  Compute complex expression between columns:
    csvspoon apply \
            -b "import math" \
            -t x:float \
            -t y:float \
            -a norm "math.sqrt(x**2+y**2)" \
            file.csv

  Multiple computation can be done reusing newly created columns:
    csvspoon apply -t x:int -a x2p1 "x**2+1" -a x2p1m1 "x2p1-1" file.csv

```
## `csvspoon filter`
```
usage: csvspoon filter [-h] [-d DELIM] [-c INPUTENC] [-o OUTPUT] [-u ODELIM]
                       [-C OUTPUTENC] [-f FORMAT] [-b BEFORE] [--np] [--sp]
                       [-t TYPE] [-a FILTER_FORMULA]
                       [input]

Evaluate a formula on each row, and keep only rows where the formula
is evaluated True.
The formula must be a valid python expression evaluated on each row.
This method is completely streamed and no data is stored in memory.

positional arguments:
  input                 Input file specification. If no input file is
                        provided, stdin is used as input file. Can be a
                        filename (e.g. "file.csv"), a filename followed a
                        semicolon and column names separated by commas (e.g.
                        "file.csv:a_colname,another_colname"). A column can be
                        renamed while reading the file (e.g.
                        "file.csv:a_colname,new_colname=old_colname"). When
                        column names are specified, only these columns are
                        used, with the provided order.

optional arguments:
  -h, --help            show this help message and exit
  -d DELIM, --delim DELIM
                        Input delimiter. (default: ',')
  -c INPUTENC, --inputenc INPUTENC
                        Input encoding. (default: 'utf8')
  -o OUTPUT, --output OUTPUT
                        Output file, else output on stdout.
  -u ODELIM, --output-delim ODELIM
                        Output delimiter. (default: ',')
  -C OUTPUTENC, --outputenc OUTPUTENC
                        Output encoding. (default: 'utf8')
  -f FORMAT, --format FORMAT
                        Apply a format on a column on output. The argument
                        must be a column name followed by a colon and a format
                        specifier. e.g. "a_colname:5d" or "a_colname:+07.2f".
                        This option can be specified multiple time to format
                        different columns.
  -b BEFORE, --before BEFORE
                        Run the following code before evaluate the expression
                        on each row. Can be specified multiple times. (e.g.
                        "import math").
  --np                  Shortcut to `--before "import numpy as np"`
  --sp                  Shortcut to `--np --before "import scipy as sp"`
  -t TYPE, --type TYPE  Apply type conversion on specified command prior to
                        expression. The argument must be a column name
                        followed by a valid Python type. See "--before" to
                        define non standard type. e.g. "a_column:int" or
                        "a_column:float". This option can be specified
                        multiple time to type different columns.
  -a FILTER_FORMULA, --add FILTER_FORMULA, --add-filter FILTER_FORMULA
                        FORMULA must be a valid python expression, which is
                        casted to bool(). For the current row, columns values
                        are accessible as local variable. e.g. "a_colname >
                        other_colname" or "a_colname=='fixedvalue'". See "--
                        type" for typing other columns and "--before" for run
                        code before evaluating filter expression. Can be
                        specified multiple time.

Examples:
  Filter csv file using two columns:
    csvspoon filter -a "lastname!=firstname" file.csv

  Chain filters on csv file:
    csvspoon filter \
            -a "lastname.startswith('Doe')" \
            -a "firstname.starswith('John')" \
            file.csv

  Filter csv file with float column price:
    csvspoon filter -t price:float -a "price>12.5" file.csv

  Filter csv file with complex expression:
    csvspoon filter \
            -b "import math" \
            -t x:float \
            -t y:float \
            -t z:float \
            -a "math.sqrt(x**2+y**2)>z" \
            file.csv

```
## `csvspoon sort`
```
usage: csvspoon sort [-h] [-d DELIM] [-c INPUTENC] [-o OUTPUT] [-u ODELIM]
                     [-C OUTPUTENC] [-f FORMAT] [-k KEYS] [-n] [-r] [-R]
                     [input]

Sort csv file.
Warning: this method need to store in memory all the input csv file.

positional arguments:
  input                 Input file specification. If no input file is
                        provided, stdin is used as input file. Can be a
                        filename (e.g. "file.csv"), a filename followed a
                        semicolon and column names separated by commas (e.g.
                        "file.csv:a_colname,another_colname"). A column can be
                        renamed while reading the file (e.g.
                        "file.csv:a_colname,new_colname=old_colname"). When
                        column names are specified, only these columns are
                        used, with the provided order.

optional arguments:
  -h, --help            show this help message and exit
  -d DELIM, --delim DELIM
                        Input delimiter. (default: ',')
  -c INPUTENC, --inputenc INPUTENC
                        Input encoding. (default: 'utf8')
  -o OUTPUT, --output OUTPUT
                        Output file, else output on stdout.
  -u ODELIM, --output-delim ODELIM
                        Output delimiter. (default: ',')
  -C OUTPUTENC, --outputenc OUTPUTENC
                        Output encoding. (default: 'utf8')
  -f FORMAT, --format FORMAT
                        Apply a format on a column on output. The argument
                        must be a column name followed by a colon and a format
                        specifier. e.g. "a_colname:5d" or "a_colname:+07.2f".
                        This option can be specified multiple time to format
                        different columns.
  -k KEYS, --key KEYS   Column used for sorting. Can be specified multiple
                        time.
  -n, --numeric-sort    Compare according to numerical value.
  -r, --reverse         Reverse the result of comparisons.
  -R, --random-sort     Shuffle. If key specified, shuffle is performed inside
                        lines with the same key.

Examples:
  Sort csv file using column cola:
    csvspoon sort -k cola file.csv

  Sort csv file using columns cola and colb:
    csvspoon sort -k cola -k colb file.csv

  Sort csv file using numerical mode on column numcol:
    csvspoon sort -n -k numcol file.csv

  Shuffle csv file:
    csvspoon sort -R file.csv

```
## `csvspoon join`
```
usage: csvspoon join [-h] [-d DELIM] [-c INPUTENC] [-o OUTPUT] [-u ODELIM]
                     [-C OUTPUTENC] [-f FORMAT] [-l] [-r] [-e]
                     input [input ...]

Natural join of csv files.
Joins are performed from left to right.
Warning: this method need to store in memory all csv except the
    first which is streamed.

If neither --left or --right specified, inner join is realized. For
complete outer join, use --left and --right together.

positional arguments:
  input                 Input file specification. If less than two input files
                        are provided, stdin is used as first input file,
                        otherwise use explicitly "-" for stdin. Can be a
                        filename (e.g. "file.csv"), a filename followed a
                        semicolon and column names separated by commas (e.g.
                        "file.csv:a_colname,another_colname"). A column can be
                        renamed while reading the file (e.g.
                        "file.csv:a_colname,new_colname=old_colname"). When
                        column names are specified, only these columns are
                        used, with the provided order.

optional arguments:
  -h, --help            show this help message and exit
  -d DELIM, --delim DELIM
                        Input delimiter. (default: ',')
  -c INPUTENC, --inputenc INPUTENC
                        Input encoding. (default: 'utf8')
  -o OUTPUT, --output OUTPUT
                        Output file, else output on stdout.
  -u ODELIM, --output-delim ODELIM
                        Output delimiter. (default: ',')
  -C OUTPUTENC, --outputenc OUTPUTENC
                        Output encoding. (default: 'utf8')
  -f FORMAT, --format FORMAT
                        Apply a format on a column on output. The argument
                        must be a column name followed by a colon and a format
                        specifier. e.g. "a_colname:5d" or "a_colname:+07.2f".
                        This option can be specified multiple time to format
                        different columns.
  -l, --left            Perform left join. If more than two files are
                        provided, each join in a left join. Can be used with
                        `-r` to obtain a outer join.
  -r, --right           Perform right join. If more than two files are
                        provided, each join in a right join. Can be used with
                        `-l` to obtain a outer join.
  -e, --empty           Indicate than empty field have to be considered as a
                        value.

Examples:
  Operate NATURAL JOIN on two csv files:
    csvspoon join file1.csv file2.csv

  Operate two NATURAL JOIN on three csv files:
    csvspoon join file1.csv file2.csv file3.csv

  Operate LEFT JOIN on two csv files
    csvspoon join -l file1.csv file2.csv

  Operate RIGHT JOIN on two csv files
    csvspoon join -r file1.csv file2.csv

  Operate OUTER JOIN on two csv files
    csvspoon join -lr file1.csv file2.csv

```
## `csvspoon aggregate`
```
usage: csvspoon aggregate [-h] [-d DELIM] [-c INPUTENC] [-o OUTPUT]
                          [-u ODELIM] [-C OUTPUTENC] [-f FORMAT] [-b BEFORE]
                          [--np] [--sp] [-t TYPE] [-a COLSPEC FORMULA]
                          [-k KEYS]
                          [input]

Apply a formula to compute a new column.
The formula must be a valid python expression evaluated for each
groupped row.
Only aggregation or column with non ambiguous values are keeped.
Warning: this method need to store in memory all the input csv file.

positional arguments:
  input                 Input file specification. If no input file is
                        provided, stdin is used as input file. Can be a
                        filename (e.g. "file.csv"), a filename followed a
                        semicolon and column names separated by commas (e.g.
                        "file.csv:a_colname,another_colname"). A column can be
                        renamed while reading the file (e.g.
                        "file.csv:a_colname,new_colname=old_colname"). When
                        column names are specified, only these columns are
                        used, with the provided order.

optional arguments:
  -h, --help            show this help message and exit
  -d DELIM, --delim DELIM
                        Input delimiter. (default: ',')
  -c INPUTENC, --inputenc INPUTENC
                        Input encoding. (default: 'utf8')
  -o OUTPUT, --output OUTPUT
                        Output file, else output on stdout.
  -u ODELIM, --output-delim ODELIM
                        Output delimiter. (default: ',')
  -C OUTPUTENC, --outputenc OUTPUTENC
                        Output encoding. (default: 'utf8')
  -f FORMAT, --format FORMAT
                        Apply a format on a column on output. The argument
                        must be a column name followed by a colon and a format
                        specifier. e.g. "a_colname:5d" or "a_colname:+07.2f".
                        This option can be specified multiple time to format
                        different columns.
  -b BEFORE, --before BEFORE
                        Run the following code before evaluate the expression
                        on each row. Can be specified multiple times. (e.g.
                        "import math").
  --np                  Shortcut to `--before "import numpy as np"`
  --sp                  Shortcut to `--np --before "import scipy as sp"`
  -t TYPE, --type TYPE  Apply type conversion on specified command prior to
                        expression. The argument must be a column name
                        followed by a valid Python type. See "--before" to
                        define non standard type. e.g. "a_column:int" or
                        "a_column:float". This option can be specified
                        multiple time to type different columns.
  -a COLSPEC FORMULA, --add COLSPEC FORMULA, --add-aggregation COLSPEC FORMULA
                        Append a new colon by aggregation of values. Take two
                        argument, COLSPEC and FORMULA. COLSPEC is the name of
                        the created column obtained the aggregation. The
                        COLSPEC can also contains a colon and a format
                        specifier, see "--format" for example. FORMULA must be
                        a valid python expression. For each column, list of
                        values to aggregate are accessible as local variable.
                        The formula should return a single value. e.g.
                        "sum(a_colname) + sum(other_colname)". See "--type"
                        for typing other columns and "--before" for run code
                        before evaluating expression. Can be specified
                        multiple time.
  -k KEYS, --key KEYS   Column used groupping the aggregate. Can be specified
                        multiple time. Similar to "GROUP BY" in SQL.

Examples:
  Keeping unique lines, one line per group:
    csvspoon aggregate \
            -k group \
            file.csv

  Computing the total mean grade:
    csvspoon aggregate \
            --np \
            -t grade:float \
            -a meangrade "np.mean(grade)" \
            file.csv

  Computing the total mean grade specifing a format:
    csvspoon aggregate \
            --np \
            -t grade:float \
            -a meangrade:.2f "np.mean(grade)" \
            file.csv

  Computing the mean grade by group:
    csvspoon aggregate \
            --np \
            -t grade:float \
            -a meangrade "np.mean(grade)" \
            -k group \
            file.csv

  Computing the mean grade, median, standard deviation by group:
    csvspoon aggregate \
            --np \
            -t grade:float \
            -a meangrade "np.mean(grade)" \
            -a mediangrade "np.median(grade)" \
            -a stdgrade "np.std(grade)" \
            -k group \
            file.csv

```
## Cli example
### csvspoon cat: Concatenate CSV files
 - Change delimiter of a csv file:
```
csvspoon cat -d "\t" -u ";" file.csv > result.csv
```
 - Change delimiter of a csv file with specified output:
```
csvspoon cat -o result.csv -d "\t" -u ";" file.csv
```
 - Cat two csv files:
```
csvspoon cat file1.csv file2.csv
```
 - Reformat two columns of a csv files:
```
csvspoon cat -f a_colname:5.1f -f another_colname:04d file.csv
```
 - Cat one csv file, keeping only a column:
```
csvspoon cat file.csv:a_col
```
 - Cat two csv files, renaming a column on the second file:
```
csvspoon cat file1.csv file2.csv:new_col=old_col,another_col
```
### csvspoon apply: Apply functions to add columns
 - Combine text columns by a formula:
```
csvspoon apply -a name "lastname.upper()+' '+firstname.lower()" file.csv
```
 - Sum to integer columns:
```
csvspoon apply -t cola:int -t colb:int -a colsum "cola+colb" file.csv
```
 - Sum to integer columns and format the result:
```
csvspoon apply -t cola:int -t colb:int -a colsum:05d "cola+colb" file.csv
```
 - Compute complex expression between columns:
```
csvspoon apply \
        -b "import math" \
        -t x:float \
        -t y:float \
        -a norm "math.sqrt(x**2+y**2)" \
        file.csv
```
 - Multiple computation can be done reusing newly created columns:
```
csvspoon apply -t x:int -a x2p1 "x**2+1" -a x2p1m1 "x2p1-1" file.csv
```
### csvspoon sort: Sort CSV file
 - Sort csv file using column cola:
```
csvspoon sort -k cola file.csv
```
 - Sort csv file using columns cola and colb:
```
csvspoon sort -k cola -k colb file.csv
```
 - Sort csv file using numerical mode on column numcol:
```
csvspoon sort -n -k numcol file.csv
```
 - Shuffle csv file:
```
csvspoon sort -R file.csv
```
### csvspoon filter: Filter CSV from given conditions
 - Filter csv file using two columns:
```
csvspoon filter -a "lastname!=firstname" file.csv
```
 - Chain filters on csv file:
```
csvspoon filter \
        -a "lastname.startswith('Doe')" \
        -a "firstname.starswith('John')" \
        file.csv
```
 - Filter csv file with float column price:
```
csvspoon filter -t price:float -a "price>12.5" file.csv
```
 - Filter csv file with complex expression:
```
csvspoon filter \
        -b "import math" \
        -t x:float \
        -t y:float \
        -t z:float \
        -a "math.sqrt(x**2+y**2)>z" \
        file.csv
```
### csvspoon join: Join CSV files
 - Operate NATURAL JOIN on two csv files:
```
csvspoon join file1.csv file2.csv
```
 - Operate two NATURAL JOIN on three csv files:
```
csvspoon join file1.csv file2.csv file3.csv
```
 - Operate LEFT JOIN on two csv files
```
csvspoon join -l file1.csv file2.csv
```
 - Operate RIGHT JOIN on two csv files
```
csvspoon join -r file1.csv file2.csv
```
 - Operate OUTER JOIN on two csv files
```
csvspoon join -lr file1.csv file2.csv
```
### csvspoon aggregate: Compute aggregation on CSV file
 - Keeping unique lines, one line per group:
```
csvspoon aggregate \
        -k group \
        file.csv
```
 - Computing the total mean grade:
```
csvspoon aggregate \
        --np \
        -t grade:float \
        -a meangrade "np.mean(grade)" \
        file.csv
```
 - Computing the total mean grade specifing a format:
```
csvspoon aggregate \
        --np \
        -t grade:float \
        -a meangrade:.2f "np.mean(grade)" \
        file.csv
```
 - Computing the mean grade by group:
```
csvspoon aggregate \
        --np \
        -t grade:float \
        -a meangrade "np.mean(grade)" \
        -k group \
        file.csv
```
 - Computing the mean grade, median, standard deviation by group:
```
csvspoon aggregate \
        --np \
        -t grade:float \
        -a meangrade "np.mean(grade)" \
        -a mediangrade "np.median(grade)" \
        -a stdgrade "np.std(grade)" \
        -k group \
        file.csv
```
