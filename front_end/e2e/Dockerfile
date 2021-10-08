FROM cypress/included:3.2.0


RUN npm install -g wait-on

# copy entry script

COPY init.sh /bin/init_tests

RUN chmod 770 /bin/init_tests

ENTRYPOINT [ "/bin/bash" ]