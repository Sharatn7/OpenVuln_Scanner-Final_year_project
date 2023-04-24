#!/bin/bash
# if [ -f $1 ]; then
#     echo "SHA1 hash:$(sha1sum $1)"
# else
#     echo "File not found!"
# fi

#!/bin/bash

if [ -f "$1" ]; then
  sha256sum "$1"
else
  echo "File not found!"
fi
