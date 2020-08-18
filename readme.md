[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=Wcubed_asset_explorer&metric=alert_status)](https://sonarcloud.io/dashboard?id=Wcubed_asset_explorer)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=Wcubed_asset_explorer&metric=code_smells)](https://sonarcloud.io/project/issues?id=Wcubed_asset_explorer&resolved=false&types=CODE_SMELL)

This is an attempt to make it easy to search for a particular kind of item or image in a large collection of icons.

# Feature list
## Required

- [ ] Allow selecting in image grid.
- [ ] Allow right-mouse-button -> Copy image / path / folder path, on assets in the grid and list.
- [ ] Allow for copying the image itself. Instead of the path.
- [ ] Show asset directories and their subdirectories in the tree view.
- [ ] More complex search:
  - Tagged with x or x or x
  - Not tagged with x or x or x

- [x] Auto-save asset directories every x minutes (check for dirty assets before saving a directory).
- [x] Filter images by tag.
- [x] Add asset packs via dialog, instead of the file explorer sidebar.
- [x] Tag images.
- [x] Show what tags an image has.
- [x] Remember the tags. By saving them in a `.asset_dir.json` in each directory and subdirectory?
- [x] Add a menu item to clear the cache.
- [x] Add an asset pack (folder) to the library.
- [x] Remove an asset pack (folder) from the library.
- [x] Save an asset packs info into a json file in it's directory.
- [x] Grid of images instead of a list. That way you can see more of them (the whole point of the exercise).
- [x] Save the asset packs loaded into one of the common user directories. (in QStandardPaths::AppConfigLocation?)
- [x] Show all images in an asset pack.
- [x] Only load images when they are actually visible in the list.
- [x] Remember the images by the hash of their path that way we can:
    - [x] Cache the thumbnails on disk, by saving them with the hash of the asset path.
- [x] Drop the full image from memory again if we don't need it. Otherwise we will fill quite a bit of ram.
- [x] Allow for clearing the thumbnail cache.
- [x] Auto-complete tag input with known tags.

## Wishlist
- [ ] When you tag an image / remove a tag from an image, and there is a filter active. Re-run the filter.
    - [ ] Make this a toggleable option with a checkbox?
- [ ] Sort the tags alphabetically in the selection boxes.
- [ ] Log the date when an image was last scanned / made a thumbnail for. If the image on disk is newer, invalidate
      any automatic tags and thumbnails and re-scan the image.
- [ ] Ability to quickly colorize images.
- [ ] Ability to add frames / backdrops / backgrounds to images.
- [ ] Ability to save those generated images in a folder.
    - Frame goes around the image, and is transparent in the middle.
    - Slot goes behind the image and contains it. (like one of those hexagon tiles)
    - Background fills the entire image and goes behind everything.
- [ ] Allow the moving of assets between folders?
- [ ] Also show subdirectories in the directory tree that don't contain assets.
- [ ] Allow for renaming assets?
- [ ] Filter images by size?
- [ ] Allow dragging the image to copy it to for example a file input of another application (QDrag?)
- [ ] Allow renaming assets from both the details view, and the asset list (the table view).
- Add colors to certain tags? So that assets get an outline with that color? Might be difficult with how the tags are saved now.
  Could work if the tags are also saved in the config.json. but then you should be able to put the config.json somewhere 
  other than the appdata directory, for cross-platform and backup functionality.
- Allow saving the "config.json" somewhere else. Maybe by using a "look here" setting in the appdata config?
  Or simply simlink :P.
  
- Add built-in tags, like: "transparent-background"
- Detect images with transparent backgrounds, and system-tag them accordingly (built-in tags)? How to do this reliably and quickly?
- Detect predominant colors on images automatically.
    - For example: is the percentage with pixels near color x above y percent? then tag it with that color's system tag.
    - Allow overriding those automatic system tags?
- General robustness (file not found, config key not found, and such.)
- Make it clear that removing a pack, will not actually remove the "asset_pack.json" and therefore it's settings will
  be remembered.
- Sort asset packs by name.
- Re-Scan known asset packs on startup? And add a re-scan button.
    - Do something smart when old assets cannot be found.
- Automatically discover alternate versions of an image (transparent / psd file etc.)
- Detect when we add a folder which is inside a folder we already have added.
    - Or vice-versa, if we add a folder which is a parent folder of another one.

# Dependencies

- Run with Python 3.6 or higher.
- PyQt5 5.15.0 (pip/pip3 install PyQt5)
    - Docs: https://doc.qt.io/qtforpython/contents.html
    - Class reference: https://doc.bccnsoft.com/docs/PyQt5/class_reference.html
    - Or in case you have the QT5 assistant installed, you can use that as a reference.

## Test dependencies
- pytest 6.01, to run the tests.
- pyfakefs 4.1.0, to mock the filesystem.