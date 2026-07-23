We follow the [PEP-8 Python Style Guide.](https://www.python.org/dev/peps/pep-0008/)

## Holodeck Command Center

### Definition
The holodeck command center can be used to change the state of holodeck environments by handling the memory mapped files. A command may be used to, for example, edit the weather or change the day time. In the future, commands will be made more flexible to the unique qualities of each world
### Pros
- flexible to each world
- can be used to control elements of the world not related to agents
- easy to implement
### Cons
- effects of commands are not maintained through environment resets
- changes that are specific to one world cannot be generalized to other worlds
### Deciding
If the command you want to implement affects certain elements of the worlds which are not part of the agents behavior, sensor input, or reward/task system, using the command center is probably the best option.