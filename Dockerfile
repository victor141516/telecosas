FROM klutchell/rar as rar_image
FROM python:3-alpine
WORKDIR /app
COPY --from=rar_image /usr/local/bin/rar /usr/local/bin/rar
COPY --from=rar_image /usr/local/bin/unrar /usr/local/bin/unrar
RUN apk add --no-cache gcc python3-dev py3-pip musl-dev
COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt
COPY . /app
WORKDIR /app
