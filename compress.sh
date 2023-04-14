#!/bin/sh
input_name=$1

python scripts/lossyrnn/encoder.py --model scripts/lossyrnn/models/encoder_epoch_00000195.pth --cuda --input uploads/$input_name --output codes --iterations 16
sleep 1
python scripts/lossyrnn/decoder.py --model scripts/lossyrnn/models/decoder_epoch_00000195.pth  --cuda --input codes.npz --output compress/
