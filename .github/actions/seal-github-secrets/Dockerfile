FROM python:3.9-slim AS builder
ADD . /app
WORKDIR /app

RUN pip install --target=/app pyyaml

# A distroless container image with Python and some basics like SSL certificates
# https://github.com/GoogleContainerTools/distroless
#@@@ ADJUST IMAGE?
FROM gcr.io/distroless/python3-debian10
#@@@ SKIP WRITING TO TAR FILE, JUST PIPE TO DECOMPRESS
RUN curl -sSLf https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.18.2/kubeseal-0.18.2-linux-amd64.tar.gz | tar xzf - \
 && sudo install -m 755 kubeseal /usr/local/bin/kubeseal \
 && rm -f kubeseal
COPY --from=builder /app /app
WORKDIR /app
ENV PYTHONPATH /app
CMD ["/app/main.py"]
