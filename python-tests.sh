#!/bin/bash
echo -e "\033[7m Traffic Simulation Python Tests \033[0m"
echo -e "Usage:"
echo -e "./python-tests.sh"
echo -e "    Run tests and show summary after each test file"
echo -e "./python-tests.sh -v"
echo -e "    Show result of each test individually (for troubleshooting)"
cd default-files
for f in *.py
do
  python3 $f $1
done
cd ..
cd xml/tests
for f in *.py
do
  python3 $f $1
done
cd ../..
