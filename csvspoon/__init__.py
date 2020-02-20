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

"""
csvspoon: a tool to manipulate csv file with headers

"""

__title__ = "csvspoon"
__author__ = "Jean-Benoist Leger"
__licence__ = "MIT"

version_info = (0, 8)
__version__ = ".".join(map(str, version_info))

from .spoon import (
    ColFormat,
    ColType,
    ContentCsv,
    CsvColumnsNotFound,
    CsvFileSpec,
    NewColFormat,
    NotValidContent,
)

__all__ = [
    "ColFormat",
    "ColType",
    "ContentCsv",
    "CsvColumnsNotFound",
    "CsvFileSpec",
    "NewColFormat",
    "NotValidContent",
]
