FROM alpine:latest

RUN mkdir /app

WORKDIR /app

RUN echo "Hello, World!" > hello.txt

CMD ["cat", "hello.txt"]
