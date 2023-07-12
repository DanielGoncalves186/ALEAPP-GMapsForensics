# ALEAPP

Android Logs Events And Protobuf Parser

If you want to contribute hit me up on twitter: https://twitter.com/AlexisBrignoni  

Details in blog post here: https://abrignoni.blogspot.com/2020/02/aleapp-android-logs-events-and-protobuf.html  

## Requirements

**Python 3.9 or above** (older versions of 3.x will also work with the exception of one or two modules)

### Dependencies

Dependencies for your python environment are listed in `requirements.txt`. Install them using the below command. Ensure 
the `py` part is correct for your environment, eg `py`, `python`, or `python3`, etc. 

`py -m pip install -r requirements.txt`  
or  
 `pip3 install -r requirements.txt`

To run on **Linux**, you will also need to install `tkinter` separately like so:

`sudo apt-get install python3-tk`

To install dependencies offline Troy Schnack has a neat process here:
https://twitter.com/TroySchnack/status/1266085323651444736?s=19

## Compile to executable

To compile to an executable so you can run this on a system without python installed.

To create aleapp.exe, run:

```
pyinstaller --onefile aleapp.spec
```

To create aleappGUI.exe, run:

```
pyinstaller --onefile --noconsole aleappGUI.spec
```

## Usage

### CLI

```
$ python aleapp.py -t <zip | tar | fs | gz> -i <path_to_extraction> -o <path_for_report_output>
```

### GUI

```
$ python aleappGUI.py 
```

### Help

```
$ python aleapp.py --help
```

## Contributing artifact plugins

Each plugin is a Python source file which should be added to the `scripts/artifacts` folder which will be loaded 
dynamically each time ALEAPP is run.

The plugin source file must contain a dictionary named `__artifacts__` which defines the artifacts which the plugin 
processes. The keys in the `__artifacts__` dictionary should be IDs for the artifact(s) which must be unique within
ALEAPP; the values should be tuples containing 3 items: the category of the artifact as a string; a tuple of strings
containing glob search patterns to match the path of the data that the plugin expects for the artifact; and the function 
which is the entry point for the artifact's processing (more on this shortly).

For example:

```python
__artifacts__ = {
    "cool_artifact_1": (
        "Really cool artifacts",
        ('*/com.android.cooldata/databases/database*.db'),
        get_cool_data1),
    "cool_artifact_2": (
        "Really cool artifacts",
        ('*/com.android.cooldata/files/cool.xml'),
        get_cool_data2)
}
```

The functions referenced as entry points in the `__artifacts__` dictionary must take the following arguments:

* An iterable of the files found which are to be processed (as strings)
* The path of ALEAPP's output folder(as a string)
* The seeker (of type FileSeekerBase) which found the files
* A Boolean value indicating whether or not the plugin is expected to wrap text

For example:

```python
def get_cool_data1(files_found, report_folder, seeker, wrap_text):
    pass  # do processing here
```

Plugins are generally expected to provide output in ALEAPP's HTML output format, TSV, and optionally submit records to 
the timeline. Functions for generating this output can be found in the `artifact_report` and `ilapfuncs` modules. 
At a high level, an example might resemble:

```python
import datetime
from scripts.artifact_report import ArtifactHtmlReport
import scripts.ilapfuncs

def get_cool_data1(files_found, report_folder, seeker, wrap_text):
    # let's pretend we actually got this data from somewhere:
    rows = [
     (datetime.datetime.now(), "Cool data col 1, value 1", "Cool data col 1, value 2", "Cool data col 1, value 3"),
     (datetime.datetime.now(), "Cool data col 2, value 1", "Cool data col 2, value 2", "Cool data col 2, value 3"),
    ]
    
    headers = ["Timestamp", "Data 1", "Data 2", "Data 3"]
    
    # HTML output:
    report = ArtifactHtmlReport("Cool stuff")
    report_name = "Cool DFIR Data"
    report.start_artifact_report(report_folder, report_name)
    report.add_script()
    report.write_artifact_data_table(headers, rows, files_found[0])  # assuming only the first file was processed
    report.end_artifact_report()
    
    # TSV output:
    scripts.ilapfuncs.tsv(report_folder, headers, rows, report_name, files_found[0])  # assuming first file only
    
    # Timeline:
    scripts.ilapfuncs.timeline(report_folder, report_name, rows, headers)


__artifacts__ = {
    "cool_artifact_1": (
        "Really cool artifacts",
        ('*/com.android.cooldata/databases/database*.db'),
        get_cool_data1)
}
```

## Acknowledgements

This tool is the result of a collaborative effort of many people in the DFIR community.
