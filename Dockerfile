FROM debian:latest

MAINTAINER Hans-Willi Werres

RUN apt-get update 

RUN apt-get install -y --no-install-recommends \
        fetchmail

# python3 shared with most images
RUN apt-get install -y --no-install-recommends \
        python3 \
        python3-pip 

# Image specific layers under this line
#RUN apk add --no-cache ca-certificates openssl \
# && pip3 install requests

#COPY --from=builder /fetchmail-7.0.0-alpha6/fetchmail /usr/local/bin
COPY fetchmail.py /fetchmail.py

RUN adduser fetchmail
USER fetchmail

CMD ["/fetchmail.py"]
