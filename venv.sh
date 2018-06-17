#!/usr/bin/env bash
#!/usr/bin/env bash
DIRECTORY=virtualenvs/.modana
deactivate 2> /dev/null
if [ -d "${DIRECTORY}" ]; then
    source ${DIRECTORY}/bin/activate
else
    virtualenv -p `which python3` ${DIRECTORY}
    source ${DIRECTORY}/bin/activate
fi