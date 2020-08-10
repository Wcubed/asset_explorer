[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=Wcubed_asset_explorer&metric=alert_status)](https://sonarcloud.io/dashboard?id=Wcubed_asset_explorer)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=Wcubed_asset_explorer&metric=code_smells)](https://sonarcloud.io/project/issues?id=Wcubed_asset_explorer&resolved=false&types=CODE_SMELL)

This is an attempt to make it easy to search for a particular kind of item or image in a large collection of icons.

# Feature list
## Required

- [x] Add an asset pack (folder) to the library.
- [ ] Remove an asset pack (folder) from the library.
- [x] Save the asset packs loaded into one of the common user directories. (in QStandardPaths::AppConfigLocation?)
- [x] Show all images in an asset pack.
- [x] Only load images when they are actually visible in the list.
- [ ] Tag images.
- [ ] Show what tags an image has.
- [ ] Remember the tags. By saving them in a `.asset_dir.csv` in the directory itself?
- [ ] Show all images with a tag
- [ ] Grid of images instead of a list. That way you can see more of them (the whole point of the exercise)
- [ ] Drop the full image from memory again if we don't need it. Otherwise we will fill quite a bit of ram.

# Whishlist
- Remember the images by the hash of their path that way we can:
    - Cache the thumbnails on disk, by saving them with the hash of the asset path.
- Autosave interval? So we don't save for every little thing.
- Automatically discover alternate versions of an image (transparent / psd file etc.)
- Detect when we add a folder which is inside a folder we already have added.
    - Or vice-versa, if we add a folder which is a parent folder of another one.

# Dependencies

- PyQt5 (pip/pip3 install PyQt5)
    - Docs: https://doc.qt.io/qtforpython/contents.html
    - Class reference: https://doc.bccnsoft.com/docs/PyQt5/class_reference.html
    - Or in case you have the QT5 assistant installed, you can use that as a reference.