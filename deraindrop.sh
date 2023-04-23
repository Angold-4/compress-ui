#!/bin/sh

cd scripts/cyclegan
python test.py --dataroot ./datasets/raindrop2clear --name raindrop2clear --model cycle_gan
