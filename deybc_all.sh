dir="./Tactics_Ystext/Ystext"
if [ ! -d "$dir" ]; then 
    echo "DAT dir not found"
    exit 1 
fi 
for FILE in "$dir"/*; do 
    echo "$FILE"
    python3 ./deybc.py $FILE
    if [ $? -ne 0 ]; then 
        echo "FAILURE ON $FILE"
    fi 
done 