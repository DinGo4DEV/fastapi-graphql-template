ARG VERSION=3.10.4-slim
ARG ARTIFACT=python
ARG HOST="docker.io"
FROM --platform=linux/amd64 $HOST/$ARTIFACT:$VERSION

USER 0
RUN rm -f /etc/localtime \
&& ln -sv /usr/share/zoneinfo/Hongkong /etc/localtime \
&& echo "Hongkong" > /etc/timezone

WORKDIR /epc-account-management

COPY requirements.txt .

RUN pip install -r requirements.txt


ENV env=uat

COPY . .
RUN chgrp -R 0 /epc-account-management && chmod -R g=u /epc-account-management
USER 1001
CMD ["sh","-c","uvicorn app.main:app --host 0.0.0.0 --port 8080 --workers 2 --root-path /api/$env"]