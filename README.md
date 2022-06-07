# mritools
Some misc tools that I use when working with MRI data. These will work outside my (clab) environment only if you fix the paths to your data.

## FFS.py
Instead of adding volumes manually (or with cmd line) just type in the ID number and set a flag to display volumes of interest.
Required:
* id either as `sub-12345` or `12345`. 

Options:
* `-i`: Inflated
* `-o`: Dedicated mode to visually detect holes
* `-a`: Loads default view with aparc.a2009s parcelation
* `-r`: Given RAS coordinates the view will be centered on the coordinates
* `-c`: Compares old and new parcelation
* `-m`: Specify machine, if using KPC: `-m kpc`
* `-l`: Specify line width, default is 1, but 2 may be helpful if you are using a x2go connection with low bandwidth. 

Examples:
* General use:
```bash
python fss.py 12345
```
* Compare QA changes for sub-12345 on KPC with line width 2:
```bash
python fss.py 12345 -m kpc -c -l 2
```
* Show parcelation and segmentation for sub-12345:
```bash
python fss.py 12345 -a
```
* Show inflated surface for sub-12345:
```bash
python fss.py 12345 -i
```