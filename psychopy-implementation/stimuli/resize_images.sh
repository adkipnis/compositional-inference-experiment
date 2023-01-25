#!/bin/bash
# cues
for file in c_*.png;
  do convert $file -scale 256x256 $file;
done

# stimuli
convert s_globe.png -scale 180x180 s_globe.png
convert s_shoe.png -scale 190x190 s_shoe.png
convert s_frog.png -scale 200x200 s_frog.png
convert s_puzzle.png -scale 200x200 s_puzzle.png
convert s_banana.png -scale 210x210 s_banana.png
convert s_signpost.png -scale 220x220 s_signpost.png
convert s_rocket.png -scale 220x220 s_rocket.png
convert s_heart.png -scale 230x230 s_heart.png

# rest
convert magicBooks.png -scale 60% magicBooks.png

