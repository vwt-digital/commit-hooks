# Pre-commit

###### Note: The *default* branch develop might contain breaking changes if the sast image is not up to date. Make sure to pull from master for a stable version.
This repository contains commit hook scripts that can be installed globally by running the installation script.
Both Linux and OSX are supported.

## Installation
1. Clone this repository
2. Make sure Docker is properly installed on your system. Test this by running `docker run hello-world`.
3. Configure Docker for gcloud using `gcloud auth configure-docker`
4. Login to gcloud using `gcloud auth login`
5. Run the install.sh script

**Windows users, please note**:
Use the newest release instead of the source code from the repository. You still need to follow the rest of the steps except step 1,
with an added step of unzipping the released source.

If your python path isn't set, or if it doesn't redirect to python3, change the following to your specification:
- [install.sh](https://github.com/vwt-digital/commit-hooks/blob/develop/install.sh#L39-L42)
- [pre-commit](https://github.com/vwt-digital/commit-hooks/blob/develop/hooks/pre-commit#L142)


This repository uses a [cloudbuilder-sast](https://github.com/vwt-digital/cloudbuilder-sast) image.  
If you do not have access to the vwt gcr registry, you will need to build this image yourself and change the install 
script and the hooks to use the location of your image.


## Usage 
After running the install script, the git hooks path is set to the hooks directory in this repository. Any changes to
the files in that directory will be automatically applied. There is no need to run the install script again, unless 
pulling a newer version of the cloudbuilder-sast container.

## Use Remotes
When using `--no-verify`, git will still call `commit-msg` and `post-commit`. 
That is why you can use the `remotes` configuration file to specify what remotes should run all commit hooks.
Other remotes will not use `commit-msg` and `post-commit`.
You can add or remove any remote from the list.


## Validation
When a commit message has been created, a check mark will be added to the end of the message. This will notify
other contributors that the commit hooks have been used.

## Configuration
**See the [cloudbuilder-sast](https://github.com/vwt-digital/cloudbuilder-sast) readme for configuration options.**
