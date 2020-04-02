# pre-commit

###### Note: The *default* branch develop might contain breaking changes if the sast image is not up to date. Make sure to pull from master for a stable version.
This repository uses a [cloudbuilder-sast](https://github.com/vwt-digital/cloudbuilder-sast) image.  
If you do not have access to the vwt gcr registry, you will need to build this image yourself and change the install 
script to use the location of your image.

This repository contains commit hook scripts that can be installed globally by running the installation script.
Both Linux and OSX are supported.

```
./install.sh
```

If you want to apply the commit hooks to an existing local repository, execute the following command in that repository:

```
git init
```
