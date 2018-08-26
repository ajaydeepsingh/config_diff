#!/bin/sh

python ConfigDiff.py
echo "Successfully generated diff files"
diff2html -i file week.diff -s side -F week.html
echo "Created week.html"
diff2html -i file twoweek.diff -s side -F twoweek.html
echo "Created twoweek.html"