FROM alpine:3.17.2
RUN apk --update add python3
WORKDIR /app
COPY loadbalancer.py loadbalancer.py
CMD ["python3", "loadbalancer.py"]
EXPOSE 16432