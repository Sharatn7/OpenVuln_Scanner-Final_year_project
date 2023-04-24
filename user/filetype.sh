#!/bin/bash
# if [ -f $1 ]
# then
#     echo "The filetype of $1 is $(file $1)"
# else
#     echo "File not found!"
# fi


if [ -f "$1" ]; then
  file_type=$(file "$1")
  echo "The filetype is $file_type"
else
  echo "File not found!"
fi