#!/bin/bash

# cues
for file in c_*.png;
  do convert $file -scale 256x256 $file;
done

# keyboards
for file in keyBoard*.png;
  do convert $file -scale 65% $file;
done

# stimuli
convert s_globe.png -scale 160x160 s_globe.png
convert s_shoe.png -resize 160x190! s_shoe.png
convert s_frog.png -scale 180x180 s_frog.png
convert s_puzzle.png -scale 190x190 s_puzzle.png
convert s_banana.png -scale 200x200 s_banana.png
convert s_signpost.png -scale 210x210 s_signpost.png
convert s_rocket.png -scale 210x210 s_rocket.png
convert s_heart.png -scale 220x220 s_heart.png

# rest
convert leftArrow.png -scale 128x128 leftArrow.png
convert magicWand.png -scale 200x200 magicWand.png
convert magicChart.png -scale 256x256 magicChart.png
convert pauseClock.png -scale 256x256 pauseClock.png
convert magicBooks.png -scale 60% magicBooks.png
convert splash.png -scale 50% splash.png

