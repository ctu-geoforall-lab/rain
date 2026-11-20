FROM sphinxdoc/sphinx:8.2.3
WORKDIR /docs
ADD requirements.txt /docs
RUN pip3 install -r requirements.txt

CMD ["/docs/build.sh"]