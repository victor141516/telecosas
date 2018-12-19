```
docker build -t telecosas .

docker run -it --rm \
    -v $(pwd)/credentials.json:/app/credentials.json \
    -v $(pwd)/config.py:/app/config.py \
    telecosas \
    python gd2tg.py [gdrive file ID or URL]]
```
