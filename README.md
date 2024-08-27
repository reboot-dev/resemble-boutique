# Resemble Boutique

For the impatient:
1. Prepare an environment by either:
    * [Using VSCode connected to a GitHub Codespace](#using-vscode-connected-to-a-github-codespace)
    * [Installing prerequisites directly](#installing-prerequisites-directly)
2. [Run the application](#run-the-application)

### Overview

This repository contains an example online store application written using Resemble.

It was originally forked from
[GoogleCloudPlatform/microservices-demo](https://github.com/GoogleCloudPlatform/microservices-demo),
and demonstrates how Resemble makes it simple to write correct microservice applications.

The [Resemble '.proto' definition](https://docs.reboot.dev/develop/schema#code-generation)
can be found in the `api/` directory, grouped into
subdirectories by proto package, while backend specific code can be
found in `backend/` and front end specific code in `web/`.

_For more information on all of the Resemble examples, please [see the docs](https://docs.reboot.dev/get_started/examples)._

## Prepare an environment by...

<a id="using-vscode-connected-to-a-github-codespace"></a>
### Using VSCode connected to a GitHub Codespace

This method requires running [VSCode](https://code.visualstudio.com/) on your machine: if that isn't your bag, see [the other environment option](#install-prerequisites-directly) below.

This repository includes a [Dev Container config](./.devcontainer/devcontainer.json) (more about [Dev Containers](https://containers.dev/)) that declares all of the dependencies that you need to build and run the example. Dev Containers can be started locally with VSCode, but we recommend using GitHub's [Codespaces](https://github.com/features/codespaces) to quickly launch the Dev Container:

1. Right-click to create a Codespace in a new tab or window:
    * [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/reboot-dev/resemble-boutique)
    * *Important*: In order to view the example's front end, you must connect your local VSCode to the codespace: you cannot use VSCode in a browser window.
2. Go to [https://github.com/codespaces](https://github.com/codespaces) and click the three dots next to the codespace you just created and then click `Open in Visual Studio Code`.
    * You can [set your default editor to VSCode for codespaces](https://docs.github.com/en/codespaces/customizing-your-codespace/setting-your-default-editor-for-github-codespaces) to avoid this step in the future. See [these instructions](https://docs.github.com/en/codespaces/developing-in-codespaces/opening-an-existing-codespace?tool=vscode) for more information.

Now you're ready to [run the application](#run-the-application)!

<a id="installing-prerequisites-directly"></a>
### Installing prerequisites directly

Running directly on a host requires:

- A platform of either:
   - `x86_64 Linux` with `glibc>=2.35` (Ubuntu Jammy and other equivalent-generation Linux distributions)
   - `arm64 or x86_64 MacOS` with `MacOS>=13.0` and `Xcode>=14.3`
- [Rye](https://rye-up.com/) - A tool to manage `python`, `pip`, and `venv`.
   - If you are already familiar with Python [virtual environments](https://docs.python.org/3/library/venv.html), feel free to use your tool of choice with [`pyproject.toml`](./pyproject.toml). Python==3.10 is required.
- Node.js
    - Including `npm`.
- Docker
    - Note: the example does not run "inside of" Docker, but Docker is used to host a native support service for local development.

If you are unable to meet any of these requirements, we suggest using the [VSCode and Dev Container environment](#using-vscode-connected-to-a-github-codespace) discussed above.

Now you're ready to [run the application](#run-the-application)!

<a id="run-the-application"></a>
## Run the application

### Backend

Our backend is implemented in Python and we must install its dependencies before
running it. The most notable of those dependencies is the `reboot-resemble` PyPI
distribution, which contains both the Resemble CLI (`rsm`) and the `resemble`
Python package.

Using `rye`, we can create and activate a virtualenv containing this project's dependencies (as well as fetch an appropriate Python version) using:
```sh
rye sync --no-lock
source .venv/bin/activate
```

#### Setup secrets

To start the Resemble boutique backend you need to make sure you have
secrets in place; you need the `mailgun-api-key` secret in the
directory `backend/secrets`.

```shell
mkdir secrets
```

Replace `MY_MAILGUN_API_KEY` with your own mailgun API key, which you can get
from [your Mailgun account](https://www.mailgun.com):
```shell
echo -n "MY_MAILGUN_API_KEY" >secrets/mailgun-api-key
```

If you are using Reboot Cloud, read
[the documentation about `rsm cloud secret`](https://docs.reboot.dev/develop/secrets) to
learn how to set a secret.

#### Run the backend

Then, to run the application, you can use the Resemble CLI `rsm` (present in the active virtualenv):
```shell
rsm dev run
```

Running `rsm dev run` will watch for file modifications and restart the
application if necessary. See the `.rsmrc` file for flags and
arguments that get expanded when running `rsm dev run`.

### Front end

Similar to the backend, the front end has dependencies that need to be installed before running it. Open a separate terminal/shell and do:
```shell
cd web/
npm install
npm start
```

If using VSCode, the page will load automatically.
If not using VSCode, visit [http://127.0.0.1:3000](http://127.0.0.1:3000)`.
### Tests

The application comes with backend tests.

Before you run the tests, you'll
need to ensure you've run `rsm protoc`.  If you've already run `rsm dev run`
without modifying `.rsmrc`, `rsm protoc` will have been run for you as
part of that command.
Otherwise, you can do it manually.

```sh
rsm protoc
```

`rsm protoc` will automatically make required Resemble '.proto'
dependencies like `resemble/v1alpha1/options.proto` available on the
import path without you having to check them into your own repository.

Now you can run the tests using `pytest`:

```sh
pytest backend/
```
### Running on the Reboot Cloud

Pick a public Docker registry you can push images to. Determine the name you'd
like the image to have in that registry. For example:
`ghcr.io/your-github-username/resemble-boutique`.

#### Build and push the Docker image like you're used to.

```shell
export IMAGE_NAME=yourregistry.io/yourname/yourproject/yourappname
docker build --tag $IMAGE_NAME .
docker push $IMAGE_NAME
```

#### Launch the image on the Resemble cloud
Include the image's SHA in its name, so that it is unambiguous exactly which version of the image you're choosing.
```sh
export IMAGE_NAME_WITH_SHA=$(docker inspect --format='{{index .RepoDigests 0}}' $IMAGE_NAME)
rsm cloud up --image-name=$IMAGE_NAME_WITH_SHA --api-key=YOUR_API_KEY
```

Execute that `rsm cloud up` command to have your pushed Resemble container run
on the Resemble Cloud! 🎉

To make calls to the application that just started, get the endpoint URL from
message output to the console.

```sh
Application starting; your application will be available at:

<application_id>.prod1.resemble.cloud:9991
```

To build a version of the front end that can talk to the deployed app, update
the `REACT_APP_REBOOT_RESEMBLE_ENDPOINT` value in `web/.env`:

```tsx
REACT_APP_REBOOT_RESEMBLE_ENDPOINT=https://<application_id>.prod1.resemble.cloud:9991
```

Then, in the `web/` directory, run `npm run build`.

Once built, this front end can be deployed to any static hosting provider like
S3, Vercel, Cloudflare or Firebase hosting.

