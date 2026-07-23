Instructions on validating your changes with pylint.

1. Make sure the latest `pylint` is installed - the version in apt is out of date and will complain about numpy.
   - `apt-get remove pylint pylint3`
   - `pip3 install pylint`
2. `cd` into the `holodeck` folder in the cloned git repo (ie `holodeck/holodeck`)
3. `pylint filename.py` to check the file 
