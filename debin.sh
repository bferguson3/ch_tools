dir="./Tactics_Ystext/TACTICS/SCRIPT"
for FILE in "$dir"/*; do 
    echo "$FILE"
    python3 ./dumpbin.py $FILE
    if [ $? -ne 0 ]; then 
        echo "FAILURE ON $FILE"
    fi 
done 