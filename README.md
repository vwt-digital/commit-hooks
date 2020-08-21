# pre-commit

###### Note: The *default* branch develop might contain breaking changes if the sast image is not up to date. Make sure to pull from master for a stable version.
This repository contains commit hook scripts that can be installed globally by running the installation script.
Both Linux and OSX are supported.

## Installation
1. Clone this repository
2. Make sure Docker is properly installed on your system. Test this by running `docker run hello-world`.
3. Configure Docker for gcloud using `gcloud auth configure docker`
4. Login to gcloud using `gcloud auth login`
5. Run the install.sh script

This repository uses a [cloudbuilder-sast](https://github.com/vwt-digital/cloudbuilder-sast) image.  
If you do not have access to the vwt gcr registry, you will need to build this image yourself and change the install 
script and the hooks to use the location of your image.

#### Extra install option(s)
<sub><sup>*FOLLOWING OPTION(s) OVERWRITE(s) RECOMMENDED SETTINGS*</sub></sup>

Install.sh will ask for user input on the following option(s):

1. pre-commit-stage-control (y/N)
> Denies the pre-commit to stage and unstage. Runs `git reset` when test fails. Disabled (N) by default. 
> Could resolve issues when removing / editing files in IDE.

Removal of all options without running install.sh, is possible by deleting `control.config` from the hooks folder.


## Usage 
After running the install script, the git hooks path is set to the hooks directory in this repository. Any changes to
the files in that directory will be automatically applied. There is no need to run the install script again, unless 
pulling a newer version of the cloudbuilder-sast container.
## Configuration
**See the [cloudbuilder-sast](https://github.com/vwt-digital/cloudbuilder-sast) readme for configuration options.**
