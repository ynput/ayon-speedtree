# SpeedTree addon

This adds Unity SpeedTree integration for AYON. SpeedTree is the industry-standard vegetation toolkit for projects of any size and style, used across both games and film.

## Dev resources

* https://docs.unity3d.com/speedtree-runtime-sdk/manual/index.html
* https://docs.unity3d.com/speedtree-pipeline-sdk/manual/index.html

## Settings
Path to SpeedTree executable must be set in the Ayon Setting in `Applications` addon (`ayon+settings://applications/applications/speedtree`), for more information see [Applications and Tools](https://help.ayon.app/articles/3945756-applications-and-tools) documentation.

### Implemented workflows
Currently supports importing/exporting models and saving/opening/publishing workfiles in SpeedTree integration. All the associated data would be stored in `.sptree_metadata` folder

## How to start
There is a `create_package.py` python file which contains logic how to create the addon from AYON codebase. Just run the code.
```shell
python ./create_package.py

