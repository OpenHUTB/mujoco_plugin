The engine side of holodeck is an Unreal project that has synchronization code written in C++ to communicate with the engine, found in the [`holodeck-engine`](https://github.com/BYU-PCCL/holodeck-engine) repo. For details on how those two halves communicate, see [Holodeck Communication Protocol](https://github.com/BYU-PCCL/holodeck/wiki/Holodeck-Communication-Protocol).

### 1. Get Unreal Editor
In order to modify the engine, you must have the Unreal Editor installed. For Windows, you can just install it from the Epic Game Launcher (see https://www.unrealengine.com/), but for Linux you must compile the editor  yourself (see [here](https://docs.unrealengine.com/en-US/Platforms/Linux/BeginnerLinuxDeveloper/SettingUpAnUnrealWorkflow/index.html)

You must install the version of Unreal Editor that holodeck is currently using, check the [changelog](https://holodeck.readthedocs.io/en/latest/changelog/changelog.html) to see which version holodeck-engine is currently using. As of this writing the current version is 4.22.

### 2. Clone Repo

To start, clone the repo (https://github.com/BYU-PCCL/holodeck-engine). You must have git-lfs installed and enabled, after running `git clone` you should be able to run `git lfs pull` and get output like the following:
```console
jayden@NAGA:~/dev/temp$ git clone git@github.com:BYU-PCCL/holodeck-engine.git
Cloning into 'holodeck-engine'...
remote: Enumerating objects: 57, done.
remote: Counting objects: 100% (57/57), done.
remote: Compressing objects: 100% (44/44), done.
remote: Total 6769 (delta 22), reused 24 (delta 12), pack-reused 6712
Receiving objects: 100% (6769/6769), 4.53 MiB | 9.84 MiB/s, done.
Resolving deltas: 100% (3884/3884), done.
Filtering content: 100% (181/181), 224.26 MiB | 9.61 MiB/s, done.
jayden@NAGA:~/dev/temp$ cd holodeck-engine/
jayden@NAGA:~/dev/temp/holodeck-engine$ git lfs pull
jayden@NAGA:~/dev/temp/holodeck-engine$
```

### 3. Opening Project
You should now be able to open `holodeck.uproject` in the editor.

If you get an error about assets being corrupt, you didn't do a git lfs pull correctly.

If you get an error about assets being saved with a different engine version, make sure you installed the correct version.

You should see the ExampleLevel loaded up:

<img src="images/editor.png" height="50%" width="50%" alt="Editor loaded up">

### 4. Generate Project Files

On Windows, right click the `holodeck.uproject` file in Explorer and select
"Refresh Visual Studio Projects"

On Linux, see [How to Debug Holodeck Engine on Linux](https://github.com/BYU-PCCL/holodeck/wiki/How-to-Configure-Debugger-on-Linux) to generate the project files.

This allows you to open Holodeck in an IDE and edit the C++ files, as well as 
debug the compiled project.

### 5. Cook Content
In the Unreal Editor, go to File -> Cook Content for {Platform}. After a few 
minutes you should get a success popup in the lower right.

You must do this before you run Holodeck from the debugger.


### 6. Run It
From here, you can either package the project in order to launch it from the 
client (eg using `holodeck.make()` or instantiating a `HolodeckEnvironment`), or
by attaching the client to an instance of the engine running in a debugger or
the Unreal editor. 

- [Packaging the Project](https://github.com/BYU-PCCL/holodeck/wiki/Packaging-Project)

TODO: Write up and link to pages explaining how to run the project here.

## FAQ

#### Where are all the levels/assets? 

We have licensed many assets to create the levels we distribute in packages, we
do not own them. According to the terms of those licenses, we are unable to 
distribute them in non-cooked form. Unfortunately, what you get in the 
holodeck-engine repo is all we can provide, sorry. You are free to create your
own levels/worlds and license them yourselves.

