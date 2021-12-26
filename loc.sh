#!/bin/bash
function get_linecount () {
    result=($@)
    echo ${result[${#result[@]}-2]}
}
total=0
array=($(find . -name '*.sh' | xargs wc -l))
result=$(get_linecount "${array[@]}")
echo "$result lines of .sh files"
total=$((total + result))
array=($(find . -name '*.css' -not -path './venv/*' | xargs wc -l))
result=$(get_linecount "${array[@]}")
echo "$result lines of .css files"
total=$((total + result))
array=($(find . -name '*.js' -not -path './venv/*' | xargs wc -l))
result=$(get_linecount "${array[@]}")
echo "$result lines of .js files"
total=$((total + result))
array=($(find . -name '*.html' | xargs wc -l))
result=$(get_linecount "${array[@]}")
echo "$result lines of .html files"
total=$((total + result))
array=($(find . -name '*.py' ! -path './venv/*' ! -path '*/migrations/*' | xargs wc -l))
result=$(get_linecount "${array[@]}")
echo "$result lines of .py files"
total=$((total + result))
echo "Total LoC: $total"
