FROM alpine:3.17.2
RUN apk --update add python3
WORKDIR /app
COPY chatserver.py chatserver.py
CMD ["python3", "chatserver.py"]
EXPOSE 6969