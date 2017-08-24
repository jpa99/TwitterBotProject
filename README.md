# Twitter Bot Project at Rice University

This is the repo for Twitter bot detection and classification project at Rice
****

**I've been designing this repository for a while. I hope virtualization and version control will make everyone's life easier. I plan to incorporate Travis CI to enable continuous integration and continuous deployment in the future. Meanwhile feel free to restructure files or folders if you have a better idea!**

How to get started:
 * Make sure you have `python` installed (I'm using Python 2.7.10)
 * Install virtualenv via pip:
	```bash
    $ pip install virtualenv
    ```
 * fork the project to your own repo
 * clone your repo to your local directory
 * `git clone git@github.com:USERNAME/TwitterBotProject.git`
 * `cd TwitterBotProject`
 * `virtualenv env` (this is only needed when you first clone the project)
 * `source env/bin/activate`
 * `pip install -r requirements.txt`
 * Now you are good to go!
 
 
 * You can try running script: `python detect.py`


How to contribute (I can teach you the whole process if you haven't done that before):
 * Everytime you work on this project, remember to activate the environment    
      `source env/bin/activate`
 * Everytime you finish working on this project, deactivate it
  `deactivate`
 * Create a new branch to add new features
 * Submit a merge request to this repo, and I will merge as soon as I can
 * Rebase from master branch regularly (Again, I can teach you what is rebase and how to rebase)