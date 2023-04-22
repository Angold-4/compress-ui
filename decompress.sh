#!/bin/sh
input_name=$1

python scripts/aec/compress.py decompress uploads/$input_name
mv uploads/$input_name.png uploads/decompress/decompress.png
