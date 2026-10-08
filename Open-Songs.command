#!/bin/bash
# Opens the songs folder and Book1.csv (the file the matching game reads)
# so you can add singer names. Save with Cmd+S when done, then press
# "↻ Reload songs" on the game page.

cd "$(dirname "$0")"

open "./Songs"

if [ -f "./Songs/Book1.csv" ]; then
  open -a "Microsoft Excel" "./Songs/Book1.csv"
else
  say -v Samantha "Could not find Book1 dot csv in the Songs folder"
  osascript -e 'display alert "Book1.csv not found" message "Put your answer key file named Book1.csv in the Songs folder, then run me again."'
fi