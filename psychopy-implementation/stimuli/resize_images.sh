#!/bin/bash
for file in c*.png;
  do convert $file -scale 256x256 $file;
done

