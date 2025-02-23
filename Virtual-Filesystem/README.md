
# Virtual File System with image encryption

## Overview
You've been infiltrated!

Is what I probably would say, assuming that you downloaded the contents of this repository, ran the FS_interface.py program, and it actually had control over the files on your computer. Close enough, though.
This project aims to implement a virtual filesystem allowing a user to create, read, update and delete files and directories. When the user exits the filesystem, the current state is encypted and saved in _puppy_picture.png_. When attempting to retrieve the data, a password wich functions as the decryption key is required. In this way, the project emulates the rudimentary parts of a trojan program, and uses steganography to hide changes to the disk.

## Features
- Create and remove directories
- Create and remove files
- Read and write file contents
- Navigate through directories
- Use quick access to show the five most visited directories (with a cool formula for calculating directory popularity)
- Load the previous state when starting the program using a password, and save it when exiting
- Test the program with some unit tests in _test_virtualfilesystem.py_

## Installation
1. Clone the repository:
    ```sh
    git clone https://github.com/Koli-Aron/Virtual-Filesystem-Challenge.git
    ```
2. Navigate to the project directory:
    ```sh
    cd Virtual-Filesystem-Challenge
    ```
3. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Usage
1. Run the filesystem interface:
    ```sh
    python FS_interface.py
    ```
2. Input a password (if you want to check out my current filestate, the password is _cheese_):
    ```sh
    Enter the password: cheese
    ```
3. Use the following commands within the interface:
    - `cd <dir_name/path>`: Change the current directory. Use cd .. to move backwards.
    - `ls`: List all children of the current directory.
    - `mkdir <dir_name/path>`: Create a new directory.
    - `mkfile <file_name/path>`: Create a new file.
    - `readfile <file_name>`: Read the contents of a file.
    - `writefile <file_name>`: Write to a file.
    - `rmdir <file_name>`: Remove a directory and all subdirectories.
    - `rmfile <file_name>`: Remove a file.
    - `quickaccess`: Open the quicksearch interface.
    - `exit`: Exit the interface. Also saves the state.

## Creative Features

These are some of my creative approaches to this task:
- `Steganography`: The filestate is saved and hidden in the metadata of a PNG file given in the repository (as inspired by Mitre: _https://attack.mitre.org/techniques/T1564/005/_). When viewing the picture, it seems like just a cute puppy!
- `Quickaccess`: Inspired by the Windows File Explorer feature of the same name, quickaccess lists the five most popular directories in the filestate (with popularity being calculated with a rather sophisticated formula). The user can enter the number of the listed directory, and quickly be taken there.
- `Relative and absolute paths`: The user can navigate the filesystem as well as create files and directories by inputting relative paths (this/is/a/test) and absolute paths (/this/is/a/test).
- `Password authentication`: When attempting to read data from the image, the program asks for a password. The password functions as the encryption key (after being salted with a fixed salt). If the correct key is provided, the state is loaded. If an incorrect key is provided, an entirely new state is created and the old one is lost. This way, only the creator of the state can reinitialize it. Salting is used to create a key from the provided password, which is then used to encrypt and decrypt the data in the image.

## API approach

The API uses four distinct classes. First is the _FileSystemObject_, which only has a name, parent, and time of creation. It has two subclasses, _File_ and _Directory_. Files can store written user data, and can be read. Directories can have children (which can be files or subdirectories), and store the number of visits.
The API follows the basic principles of a Unix-type interface, which commands such as _cd_ and _ls_.
The intent is for the filesystem itself to be entirely memory-resident, with the filestate being stored in a PNG file to evade detection from antivirus programs. It was out of the scope of this project to test whether the program is any good at this, but this was meant more to show the principle anyway.
The fact that the filestate is stored in a PNG is likely not very efficient for larger filesystems, but works fine for what was intended here (immitating steganography). Additionally, the currently implemented stress test in __test_virtualfilesystem.py__ seems to indicate that it works well enough.

## Known limitations & areas for improvement.
1. Although storing the filestate in a PNG helps evade detection, placing a picture of a dog in the same directory as the program probably isn't very inconspicuous. Placing the PNG in a more discrete location, or somewhere where it likely wont be noticed among other images would likely fly under the radar better.
2. Adding flags would allow for more precise operations. For instance, _remove_dir_ currently removes all descendents of the directory. This is usually only achieved with a flag in command prompt.
3. There are some issues with user experience. For instance, when writing a file, the user can currently input file content for a file that doesn't exist. The user is only be informed of the files non-existence after inputting the content.
4. Absolute and relative paths have not been implemented for _remove_file_ and _remove_dir_.
5. Although I'm not entirely certain, I assume it might technically be possible to find a lost file state from the meta data of the PNG, and so the password system is not infallible. However, it does at least provide an extra layer of protection.
6. The password and encyption systems have not been tested with edge cases due to time constraints. However, the password itself is not executed as code, so injection does not seem like a real concern.
7. I entirely forgot that you can implement an End-of-file (EOF) feature in CMD, so currently the only way to save the program is by calling exit.
