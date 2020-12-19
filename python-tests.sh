#!/bin/bash
echo -e "\033[7m Traffic Simulation Python Tests \033[0m"
echo -e "Usage:"
echo -e "./python-tests.sh"
echo -e "    Run tests and show summary after each test file"
echo -e "./python-tests.sh -v"
echo -e "    Show result of each test individually (for troubleshooting)"

# Tests in default xml files
(
echo -e "\033[91m"
cd default-files || exit
for f in *.py
do
  echo -e "$f"
  python3 "$f" $1
done
)

# Tests for xsd files
(
echo -e "\033[92m"
cd xml/tests || exit
for f in *.py
do
  echo -e "$f"
  python3 "$f" $1
done
)

# tests for simulator
(
echo -e "\033[93m"
cd src/py || exit
IFS=
while read -r file
do
  echo -e "$file"
  rootname=${file:2:-3}
  python3 -m "${rootname//\//.}" $1
done < <(find . -type f -name "test_*.py" -print)
)

echo -e "\033[0m"