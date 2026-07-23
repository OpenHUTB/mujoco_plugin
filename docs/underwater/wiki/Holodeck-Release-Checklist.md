This is the rough order of things that need to happen to push a release out the door.

0. As soon as the previous release is done, make sure the you've bumped the version number and append `dev` to the end 
   See [[Holodeck Versioning|Holodeck Versioning]].
   So if we just released `0.2.1`, bump it to `0.2.2dev`

   This is done so that development releases don't get mixed in with actual releases.

1. Update the [changelog](https://github.com/BYU-PCCL/holodeck/blob/master/docs/changelog/changelog.rst) with
   - New features
   - Bugs present in last release that were fixed in this release
   
   It can be useful to look at the milestone or closed pull requests in a certain date range.

   Follow [[this format.|Holodeck Release Notes Template]]

2. As you go through the changelog, update the rest of the documentation as needed
   
   Hopefully, pull requests that introduce new features or change old ones update the docs as they happen. We shouldn't put updating the docs to the last second.
3. Get the latest build of `develop` off of Jenkins, make this your "release candidate" for Linux (make sure the version in the `config.json` of `holodeck-worlds` is correct) by going to monster.cs.byu.edu.

5. Put that build on S3 (with `dev` appended to the version number), verify that the client can download it and run it on Linux. Holodeck aws account has access to the bucket at https://s3.console.aws.amazon.com/s3/buckets/holodeckworlds
6. Run integration tests locally by having an editable install of holodeck installed (see `tests/README.md`)
7. Run integration tests in tox by typing `tox` from the root of the holodeck repo
8. Package a Windows version and repeat steps 5,7, and 8.

   **Remember to change the config files for the Windows packages!**

9. Build the python code and upload it to pip, make sure you can install it

    ***MAKE SURE THE VERSION STILL HAS `dev` APPENDED TO IT***
   
    Once you upload a version to pip, you can't re-upload it without bumping the version number. pip knows to treat versions `dev` appended differently

    See [here](https://packaging.python.org/tutorials/packaging-projects/#generating-distribution-archives) for instructions on how to test & upload packages.

    If you need to upload another development version, just add a number after dev, so it would be `1.2.4dev0`
10. Install the development version with `pip install --pre holodeck` (you may need to `pip uninstall holodeck`

    In the output that pip prints out, make sure it installed the version with `dev` appended
11. Run tests again, make sure everything seems OK
12. Change the version numbers to remove `dev`, commit those changes, and merge into master
13. Checkout master, repeat step 8 to upload the final version of the python package
14. Upload the final binaries to S3 without the `dev` appended
15. In `holodeck`, `holodeck-worlds`, `holodeck-engine`, and `holodeck-configs` make a release that tags the commit that the packages were generated against. This is so we can find out later exactly what was in a released version of holodeck
16. Update the Docker images. **Note that the docker build process is triggered on push/pull requests to master. The build depends on the pip package and worlds being up to date**. Make sure those are in place before doing a final merge on the master branch. Check to make sure the image builds completed successfully. 
17. Consider writing a blog post with changes on the PCCL blog
18. Order pizza
19. Wait for the bugs to roll in