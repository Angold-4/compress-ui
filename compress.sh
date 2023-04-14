#!/bin/sh
input_name=$1

python scripts/lossyrnn/encoder.py --model scripts/lossyrnn/models/encoder_epoch_00000080.pth --input uploads/$input_name --output codes --iterations 16
python scripts/lossyrnn/decoder.py --model scripts/lossyrnn/models/decoder_epoch_00000080.pth --input codes.npz --output compress/
