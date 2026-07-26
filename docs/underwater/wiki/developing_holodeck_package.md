The [`holodeck`](https://github.com/BYU-PCCL/holodeck) repo contains the holodeck
client (See [here](https://github.com/BYU-PCCL/holodeck/wiki/Holodeck-Communication-Protocol) for explaination of client and server).

We distribute this python package through pip, so a user can just run
`pip install holodeck` and away they go. When we are working on that package,
however, we need a way to run the code we are modifying instead of the released
version in pip.

We can conveniently do this with `pip`.

From the root of the `holodeck` repo cloned on your computer:

```
pip install --editable .
```

(on Linux you may need to use `pip3`)

This will install the current package in a way that allows you to 
`import holodeck` from any directory or terminal on your system and the 
`holodeck` package that is imported will point to the code in the repo you have
cloned.
