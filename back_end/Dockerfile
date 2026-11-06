# One release behind the newest Python: pybbi has no wheels for 3.14 yet (pyproject.toml).
FROM python:3.13-slim-trixie

# The dependencies go into /opt/venv, which comes first on PATH: /code, where docker-compose
# mounts the checkout, would hide them.
ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_ROOT_USER_ACTION=ignore \
    POETRY_VIRTUALENVS_CREATE=false \
    VIRTUAL_ENV=/opt/venv \
    PATH=/opt/venv/bin:$PATH

# cooltools ships only source code, which the dependencies' installation compiles
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

# The Poetry that writes poetry.lock, in a venv of its own: poetry sync removes whatever
# the lock doesn't list from the environment it installs into.
RUN python -m venv /opt/poetry && /opt/poetry/bin/pip install poetry==2.5.1 \
    && python -m venv /opt/venv

WORKDIR /code
COPY pyproject.toml poetry.lock ./
# the runtime dependencies and pytest, as locked; ruff and pre-commit stay out
RUN /opt/poetry/bin/poetry sync --no-root --with test

# the code, so that the image runs without the checkout mounted
COPY . /code

CMD ["/bin/bash"]
