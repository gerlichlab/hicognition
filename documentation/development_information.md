# HiCognition - Development information
Repository to collect all the decisions made for the development environment of HiCognition and a detailed description of project architecture.

## High-level design decisions 

- The app is designed as a server-client tool
- The front-end is implemented in [vue.js](https://vuejs.org/) using vue-components from [vue-material](https://vuematerial.io/).
- All the routing is done in the front-end via [vue-router](https://router.vuejs.org/).
- The back-end is a pure API implemented using [flask](https://flask.palletsprojects.com/en/1.1.x/)
- We will use a MySQL database to store User-data and meta-data about data-sets
- Results of computations such as matrices will be stored on disk and referenced in the database via filename
- Authentication with the API is token-based: User presents credentials to receive a token that is valid for 1h.
- All the expensive computations will be performed by a redis queue that is triggered by the back-end server
- All computations on datasets will be done before data exploration, and the user sees only preprocessed datasets that can be quickly examined.
- All back-end functionalities will be provided by distinct docker containers
- We will use [Nginx](https://www.nginx.com/) as a [reverse proxy](https://en.wikipedia.org/wiki/Reverse_proxy) to control access to the back-end docker network. This has the following advantages:
  - We can offload TLS-encryption/decryption to the optimized Nginx-server
  - Firewall access needs to be granted only for the port exposed by the Nginx-server (80 for http-requests and 443 for https-requests)
  - In the future, scaling will be facilitated since Nginx can perform load-balancing between multiple instances of our app
  - Static requests (e.g. for the `index.html` file as well as for the js-code and css-files) can be cached in memory to reduce wait time.
  - Dynamic requests that don't change often can also be cached (e.g. API-calls to retrieve datasets could be cached for multiple minutes).

The architecture of our app is summarized in the following figure:


<p align="center">
    <img src=assets/Architecture_v1-01.png>
</p>
<p align="center">
  Figure 1: App-architecture
</p>

## Back-end

### Flask-server

The core of our back-end is a flask-server that manages the authorization of users and exchange of data with the Vue.js front-end. This flask-server is a pure REST-API, meaning that it is mostly state-less with regards the user-requests and serves data in json-format. The api-routes are implemented using the [blueprint-pattern](https://flask.palletsprojects.com/en/1.1.x/blueprints/) to allow modularization and easy extension in the future.

The flask-server runs in a custom docker container.

The User-authorization is done either by sending the user credentials (username and password) or via a token that can be obtained from the `/tokens/` route. The token is generated using `itsdangerous.TimedJSONWebSignatureSerializer` and is currently valid for 1h. The `/tokens/` route only accepts username/password authorization to prevent malicious actors from obtaining new tokens with an old token indefinitely.

Cross-origin-requests are currently allowed from all domains via injecting the `Access-Control-Allow-Origin *` Header after every request.
TODO: Look into whether this needs to be changed.

Different configurations of the server are collected in a `config.py` file that defines classes that carry the configuration options as class-variables. These different classes are used in the `create_app` app-factory function to register the relevant config settings via `app.config.from_object()`. The relevant config class can be specified via the env-variable `FLASK_CONFIG` .The different class are:

- `DevelopmentConfig` - This configuration class is used in the development and specifies that flask should be started in development mode.
- `TestingConfig` - This configuration class is used during testing and creates an sqlite database in memory.
- `ProductionConfig` - This configuration class is used in production and specifies that the database should be created in the app-directory resides in a file.

The general policy is to provide default values for development but get the values from environment variables in production. This is achieved by using the following pattern for each config-variable: `Config = os.environ.get("ENV_VAR") or default`. The configuration variables are:

- SECRET_KEY - Secret key of flask app that is used to sign the generated token
- SQLALCHMEY_TRACK_MODIFICATIONS - Whether our ORM (SQLAlchemy) should track database modifications
- UPLOAD_DIR - Directory that is used to store uploaded datasets. This filepath is used inside the docker-container and should therefore be in relation to the mounted folder with code and data.
- CHROM_SIZES - Path to the chromosome sizes file on the server filesystem that is needed for the `hicognition` module. This filepath is used inside the docker-container and should therefore be in relation to the mounted folder with code and data.
- CHROM_ARMS - Path to the file harboring genomic locations of chromosomal arms on the server filesystem that is needed for pileups in the `tasks.py` file containing different background tasks. This filepath is used inside the docker-container and should therefore be in relation to the mounted folder with code and data.
- REDIS_URL - URL of redis server
- PREPROCESSING_MAP - Windowsize/binsize combinations that should be precomputed
- BIN_SIZES - Standard bin-sizes that are used for pileups on an uploaded cooler and bed-file
- DEBUG - Whether the flask server should be started in debug mode or not
- TESTING - Flag that indicates whether server is in testing mode or not (Currently unused)
- STACKUP_THRESHOLD - From how many regions on a stackup should be downsampled
- OBS_EXP_PROCESSES - How many processes should be used to compute obs/exp
- PILEUP_PROCESSES - How many processes should be used to construct pileups
- SQLALCHEMY_DATABASE_URI - URL of the database. Note that if only `sqlite://` is specified (as in the `TestingConfig` class, the database is created in memory)

### Database

The flask-server and the redis-queue worker use a common database to record and change information about users and datasets. We use [SQLAlchemy](https://www.sqlalchemy.org/) as an Object-relational-mapper (ORM) to abstract details of the underlying database. This allows in principle to quickly change database back-ends and allows interaction with the database via python classes and functions. Currently, we use MySQL to store meta-information about datasets (file-path, name, etc.) and users directly in the database and large data (images, raw-files, processed-files...) is stored on the filesystem.

Database migrations are managed using [FLASK-Migrate](https://flask-migrate.readthedocs.io/en/latest/) that is a wrapper for [alembic](https://alembic.sqlalchemy.org/en/latest/), a database migration tool for SQLAlchemy. Using this set-up, database migrations are scheduled using 'flask db migrate -m $MESSAGE', which creates a migration script in the `./migrations` sub-folder. This migration can then be applied using `flask db upgrade`. The `./migrations` directory is committed to version control and records the migration-history of our database. The development workflow is to define database models in a `models.py` file and commit a migration to version control. Then, on the production server, the newest changes - including the migration script - are pulled and the database migrated to the newest version using `flask db upgrade`.

Interactions with the database are managed by [FLASK-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/), which uses a `ScopedSession` object as `db` throughout the app, that ensures thread-safety of database interactions.

### Database model

Details are [here](https://github.com/gerlichlab/HiCognition_flask/blob/master/app/models.py), this is an overview drawn using https://dbdiagram.io/home:

<p align="center">
    <img src=assets/Hicognition_db.png>
</p>
<p align="center">
  Figure 2: Database-model
</p>

The tables are used to store the following information:

- User - Information about the user including which datasets and tasks the user owns
- Dataset - Information about datasets (bed-files or cooler-files) with their higlass-uuid (the id in the higlass-internal sqlite database), the file-path of this dataset as well as back-refs to the owning user an refs to the pileupregions, pileups and tasks that are associated with a given dataset.
- Pileupregion - Regions derived from a bed-file Dataset that spans +/- windowsize up- and downstream. Contains a file-path to a bedpe-file holding these records and a higlass-uuid that refers to the id of the bedpe file in the higlass-internal database.
- Pileup - Pileup derived using a cooler dataset and a pileupregion. Contains the file_path to the json-file holding the pileup-information, the binsize that was used for the pileup, the value_type - which is either raw counts or obs/exp values -  as well as back-refs for the cooler_id and pileupregion_id used for the pileup
- Task - A background task in the redis-queue that contains as id the id of the job in the redis server, back-refs to the user_id that submitted the task as well as the dataset_id that is being processed. Also contains a complete flag that indicates whether the job is complete.


### Queue

Resource heavy and long tasks are offloaded to a [redis-queue](https://python-rq.org/) that consists of a redis-server and one or more redis-workers. The redis-server accepts task items and manages distributing them to the redis-workers. The redis-server runs in a docker container that is derived from `redis:6-alpine` with a custom config-file. The redis-workers use the same docker-container as the flask-server as they need access to most modules the server needs.

All tasks that the queue can run are defined in [tasks.py](https://github.com/gerlichlab/HiCognition_flask/blob/master/back_end/app/tasks.py).

Tasks are launched using an instance-method of `User` called `User.launch_task` that accepts the name of the task, a short description as well as the dataset_id of the dataset being processed. This method enqueues the job and adds the `Task` table entry to the current database session.


### Filesystem interactions

The flask-server and the redis-worker need access to a shared filesytem since all raw and processed datasets are stored as files, with their filenames being recorded in the database.

### Docker network

All the docker containers that work together in the back-end are coordinated by docker-compose (see [docker-compose file](https://github.com/gerlichlab/HiCognition_flask/blob/master/docker-compose.yml)) and reside within a docker-network called `hicognition-net`, to facilitate networking between them. The docker containers that are used are the following:

- `hicognition` - Container that harbors the flask-server
- `mysql` - contains Mysql database
- `nginx` - contains nginx reverse-proxy
- `redis-server` - contains the redis-server
- `redis-worker` - redis-worker container

Additionally, there are two transient containers that are used:

- `node` - Node container that is started to build the front-end files

There is an additional [docker-compose file](https://github.com/gerlichlab/HiCognition_flask/blob/master/docker_dev.yml) that starts hicognition in development mode without nginx, with the flask-server set to `debug` and `node` set-up to server the front-end with hot reload.

### Testing

Tests for backend functionality are implemented via the python `unittest` module and run using `pytest`. All api route-handlers as well as redis-queue tasks in `tasks.py` are tested.

### Gate-keeping of files

In order to ensure that preprocessing runs smoothely and all analyses can be performed on uploaded files, we decided to be strict with regards to what files can be uploaded. To this end,
we implemented a format-checking logic in `hicognition.format_checkers` for all supported file formats. These format checkers need to be passed before datasets are added to the internal database via `POST /dataset/`. The requirements are the following:

#### BED files

The file can contain a header, but only with the prefixes `#`, `track` or `browser`. After the header, an optional column-name row can be present. After this optional column name row, every row needs to contain as first entry a chromosome name, then a start and an end. Additionally, bed files cannot contain entries that do not map to our accepted chromosome names. 

If any of these assumptions are not met, the file is rejected.

#### Cooler files

Cooler files need to be in the `.mcool` format, meaning that the contain data binned at multiple resolutions. Additionally, they need to contain all resolutions defined in the `PREPROCESSING_MAP` config parameters.

If any of these assumptions are not met, the file is rejected.

#### BIGWIG files

Currently no format checking logic is implemented for bigwig files.


## Front-end

We use vue.js in the front-end to manage routing, interactivity and fetching data from the back-end. Here, we employ a template-based design, where each vue-component resides in its own `.vue` file that is included in the distribution build by `webpack`.

### Build

Front-end files (`index.html`, `app.js`, `vendor.js`, `app.css`, `manifest.js`) are built using [webpack](https://webpack.js.org/) with configs set in `frontend/build/build.js` and `frontend/build/webpack.prod.conf.js` and `frontend/build/webpack.dev.conf.js` (these both use `frontend/build/webpack.base.conf.js`). 

Babel is first used to transpile js-files to support all browsers with > 1% market share and support the last 2 versions (config settings `"browsers": ["> 1%", "last 2 versions", "not ie <= 8"]`). Then, js-files are minified and both js- and css-files are included in the generated `index.html` file and copied to the `./dist` directory.

Environment variables for development and production are defined using `frontend/config/dev.env.js` and `frontend/config/prod.env.js` respectively. Variables are:

- `API_URL` - The URL of the flask-api
- `STATIC_URL` - The URL of the static directory.

These variables are accessed in js-files using `process.env.VARIABLE` and resolved by webpack during build.

Modules for build are imported using the "import"-syntax rather than the "require"-syntax (more [info](https://insights.untapt.com/webpack-import-require-and-you-3fd7f5ea93c0)). This allows webpack to only bundle the actually used parts of a module, making the bundle smaller.

### Development server

A webpack development server is started using `webpack-dev-server --inline --progress --config build/webpack.dev.conf.js --host 0.0.0.0` with the alias `npm run dev`. This enables hot-reload, real-time linting and the usage of front-end debugging using the [vue-development chrome extension](https://chrome.google.com/webstore/detail/vuejs-devtools/nhdogjmejiglipccpnnnanhbledajbpd?hl=en).

### Vue set-up

Vue is used to create a single-page-application (SPA) in the front-end. This requires the usage of several extensions that serve different parts of the app:

- [vue-router](https://router.vuejs.org/) - This manages front-end routing and enables route-nesting and routing of subsets of the current view
- [vuex](https://vuex.vuejs.org/) - Since a vue.js app often consists of multiple components and multiple routes, it is frequently necessary to share data between these parts. Vuex serves the purpose of a front-end database that allows sharing of data.
- [vuematerial](https://vuematerial.io/) - Collection of components that facilitate development by encapsulating high-level user-interfaces such as cards, buttons etc.

### Vue-router

The specifics of the router are defined in `frontend/src/router.js`. In general, there are two main views called `/login` and `/main`. `/login` defines the loginRoute component that has a different toolbar to the `/main` view components. `/main` is where the app resides and it contains four sub-routes: `/main/predefined`, `/main/compare`, `/main/explore` and `/main/annotate`. These sub-routes only change the app-content, but leave the toolbar and the side-drawer intact. They are the different content-tabs of the app and define different functionalities.

The `/login` route defines a form that sends the user credentials to the `/api/token/` back-end route to obtain a token that is valid for 1 h.

All routes that are children of `/main` require authentication. Authentication is checked by verifying that a token resides in the main `vuex` store. If no token is found, the user is redirected to `/login`. Note that this routing step does not check validity of the token. Validity is only checked when data is retrieved from the back-end.

If a back-end interaction fails, the user is redirected to `/login` to request a new token.

Requests for `/` are redirected to `/main/predefined` and `/main` requests are also redirected to `/main/predefined` because `/main` itself has empty content.


### Vuex-Store

Data that needs to be shared among multiple front-end components is stored in a vuex-store. This store is defined in `frontend/src/store.js`. There is a global store that stores data that needs to be accessible across the entire app (such as the authentication token and all available datasets). Additionally, there is a sub-store (called "modules" in vuex) for all data that needs to be shared among components in the `/main/predefined` route. This has the advantage that local data such as dataset selections for a given view do not need to be stored in the global store, which avoids clumsy naming of variables.

### Interaction with back-end

All interactions with the back-end are done via api-calls that are dispatched by [axios](https://github.com/axios/axios). The `axios` instance is bound to `Vue.prototype.$http` so all `Vue` instances and components have access to the client without import.

The api-calls are defined as a mixin in `frontend/src/mixins.js` in `apiMixin`. All components that need interaction with the back-end receive the `apiMixin`. The `apimixin` has a convenience method for fetching and storing the authentication token called `.fetchAndStoreToken` and two more generic methods that allow to dispatch get and post reqeusts, `.fetchData` and `.postData` respectively. These work by return the promise the is returned by axios-requests is there is no error in the call. The caller can then resolve the promise than receive the data. If there is an error, however, the user is redirected to the login-page to get a new token.

### Testing

Front-end tests are implemented via `jest`. Currently, we only test stand-alone functions that are not dependent on a `Vue` instance. In the future we want to extend testing the `Vue` components.


## Git actions and Code tests
(TODO) Git actions will be set up in sprint 2. 

All python code must pass:
 - Formatting: `black --check .`
 - Coding standards: `pylint --disable=C0330 --fail-under=8 app/`
 - Code Complexity: `pylama --linters mccabe`
 - Unit Tests: `pytest`

## Naming conventions
 - Namespace will be defined in sprint 2.
 - Naming format convention will be after PEP8 and [pylint](http://pylint-messages.wikidot.com/messages:c0103)

## Linting and formatting guidelines

We will use [black](https://github.com/psf/black) for code formatting and [pylama](https://github.com/klen/pylama) and [pyright](https://github.com/microsoft/pyright) for linting and (sort of) static type checking. We will however not add type hints to our code.

[Google python style guide](https://google.github.io/styleguide/pyguide.html)

### Black integration into VSCode

Install black via `pip install black` and set it as your python formatting provider in VSCode (see [here](https://medium.com/@marcobelo/setting-up-python-black-on-visual-studio-code-5318eba4cd00) for details). Then, you can use the `Format document` command in VSCode to format a file. Black does not support selection formatting.

## Language convention
We will use american english spelling conventions.

## Documentation guidelines

Every function/class should have docstrings according to the rules laid out in [PEP257](https://www.python.org/dev/peps/pep-0257/):

>Multi-line docstrings consist of a summary line just like a one-line docstring, followed by a blank line, followed by a more elaborate description. The summary line may be used by automatic indexing tools; it is important that it fits on one line and is separated from the rest of the docstring by a blank line. The summary line may be on the same line as the opening quotes or on the next line. The entire docstring is indented the same as the quotes at its first line (see example below).

Every module should contain one or more ipython notebooks exemplifying the usage of each function/class. In addition, the module should have a readme that includes the following elements:

- Short description of purpose
- Installation guide
- Minimal working example of the tool if the module is an app
- Link to more detailed documentation, where all the docstrings mentioned above have been converted to a coherent text.