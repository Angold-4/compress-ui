#!/bin/sh
input_name=$1

python scripts/aec/compress.py compress b2018-gdn-128-4 uploads/$input_name
mv uploads/$input_name.tfci compress/aec/compressed.tfci
