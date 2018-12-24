Move a file from Google Drive to Telegram

```
docker build -t telecosas .

docker run -it --rm \
    -v $(pwd)/config:/app/config \
    telecosas \
    python gd2tg.py [gdrive file ID or URL]]
```
