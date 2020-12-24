ARG PYTHON_VERSION
FROM python:$PYTHON_VERSION
ENV LANG C.UTF-8
ENV TZ Asia/Tokyo

RUN apt-get update -qq && \
  apt-get install -y \
    vim \
    less && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir /app
WORKDIR /app

ENTRYPOINT ["./containers/python/entrypoint.sh"]
