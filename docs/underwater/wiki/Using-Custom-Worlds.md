If you have built a custom Unreal world using the [Holodeck backend](https://github.com/BYU-PCCL/Holodeck) you can now follow this tutorial to use it for training agents from the python bindings.

## Packaging
Before packaging the project, ensure that you have completed the following:
* You have followed the [pre-build checks](https://github.com/BYU-PCCL/Holodeck/wiki/Pre-Build-Checks)
* You know the names of the levels and agents in the world that you plan to use
* If you are packaging for linux you have followed [this tutorial](https://github.com/BYU-PCCL/Holodeck/wiki/Cross-Compiling-for-Linux)

Go to File>Package Project>_operating system_ to package. After packaging, you should have a directory called WindowsNoEditor or LinuxNoEditor depending on what OS you packaged it for.

## Using the Packaged World
Now a config file must be written to inform the python bindings about each level in your world. Follow the [json format](https://github.com/BYU-PCCL/HolodeckPythonBinding/wiki/The-Config-File-Format) to write the config file. When finished, put both the config file and the NoEditor folder in a directory called WindowsDefaultWorlds or LinuxDefaultWorlds.

The worlds are stored in the location `Users/User/Local/AppData/Holodeck` for Windows and `home/user/.local/share/holodeck` for Linux. If the holodeck directory doesn't exist, create it. Move the WindowsDefaultWorlds or LinuxDefaultWorlds into the holodeck directory. 

You can now use `env = Holodeck.make("YOUR_MAP_NAME")` to run your custom world!