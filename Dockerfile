FROM python:3-onbuild

RUN python setup.py install

CMD [ "rma", "--help" ]