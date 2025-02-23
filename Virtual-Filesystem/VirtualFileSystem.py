import time
import math
import json
import base64
from PIL import Image, PngImagePlugin
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import os

class FileSystemObject:
    """
    This is the base class for both files and directories.
    """
    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent
        self.when_created = time.time()

class File(FileSystemObject):
    """
    This class represents a file in the filesystem.
    """
    def __init__(self, name, parent, content=b''):
        super().__init__(name, parent)
        self.content = content # The binary, readable content of the file.

    def write(self, content) -> None:
        """
        Write content to the file.
        """
        self.content = content

    def read(self) -> bytes:
        """
        Read the content of the file.
        """
        return self.content

class Directory(FileSystemObject):
    """
    Directories can contain both files and subdirectories. 
    """
    id_counter = 0 # Variable to store unique ID. Currently not used.
    def __init__(self, name, parent=None, filesystem=None) -> None:
        super().__init__(name, parent)
        self.children = {} # Stores the directory's children.
        self.filesystem = filesystem
        self.id = Directory.id_counter # Assigns an id to the directory.
        self.visit_count = 0 # A variable to store the number of times the directory has been visited.
        self.last_visit = time.time()
        Directory.id_counter += 1  # Increments the id counter.
    
    def add_child(self, child) -> None:
        self.children[child.name] = child

    def get_path(self) -> str:
        """
        A recursive function for returning the file path.
        """
        if self.parent is None:
            return self.name
        elif self.parent == self.filesystem.root:
            return "/" + self.name
        else:
            return self.parent.get_path() + "/" + self.name

class VirtualFileSystem:
    """
    Initializes a system which can hold a structure of files and directories.
    """
    def __init__(self, password: str):
        self.root = Directory("/", None, self)
        self.current_dir = self.root
        self.encrypt_key = self.derive_key_from_password(password) # Derive a key from the password
        self.cipher = Fernet(self.encrypt_key) # Create a Fernet cipher object.
        self.load_state() # Load the previous state of the filesystem.
        
    def derive_key_from_password(self, password: str) -> bytes:
        """
        Derives a key from the given password using PBKDF2.
        """
        salt = b'\x00' * 16  # Use a fixed salt for consistency
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))

    def make_dir(self, path) -> None:
        """
        Creates a new directory. Supports relative and absolute paths.
        """
        parts = path.strip("/").split("/")
        dir_name = parts.pop() # The directory that will be created.
        parent_path = "/".join(parts) # Create the parth to the parent directory. It is empty if the directory is created in the current directoy.
        if path[0] == "/":
            parent_path = "/" + parent_path
        try:
            parent_dir = self.path_validator(parent_path) if parent_path else self.current_dir # If given a path, find the parent directory. Otherwise, use the current directory.
            if not isinstance(parent_dir, Directory):
                print(f"'{parent_path}' is not a valid directory.")
                return
            if dir_name in parent_dir.children:
                print(f"A directory with the name '{dir_name}' already exists!")
            else: 
                parent_dir.add_child(Directory(dir_name, parent_dir, self))
                print(f"Created a directory with the name '{dir_name}'.")
        except FileNotFoundError as e:
            print(e)
    
    def remove_dir(self, name) -> None:
        """
        Removes a directory and all it's children.
        """
        if name in self.current_dir.children:
            if isinstance(self.current_dir.children[name], Directory):
                del self.current_dir.children[name]
                print(f"Removed the directory '{name}'.")
            else:
                print(f"'{name}' is not a valid directory.")
        else:
            print(f"A directory with the name '{name}' does not exist.")

    def make_file(self, path) -> None:
        """
        Creates a new file. Supports relative and absolute paths.
        """
        parts = path.strip("/").split("/") # Split the path into parts.
        file_name = parts.pop() # The file that will be created (since it's always at the end of the path, even if the path is only one directory/file).
        parent_path = "/".join(parts) # Create the path to the parent directory. It is empty if the file is created in the current directory.

        try:
            parent_dir = self.path_validator(parent_path) if parent_path else self.current_dir 
            if not isinstance(parent_dir, Directory): # If the parent directory is not a directory, raise an error.
                print(f"'{parent_path}' is not a directory.")
                return

            if file_name in parent_dir.children: # If a file with the same name already exists, raise an error.
                print(f"A file or directory with the name '{file_name}' already exists!")
            else:
                parent_dir.add_child(File(file_name, parent_dir)) # Otherwise, create the file.
                print(f"Created a file with the name '{file_name}'.")
        except FileNotFoundError as e:
            print(e)

    def remove_file(self, name) -> None:
        """
        Removes a file from the filesystem.
        """
        if name in self.current_dir.children:
            if isinstance(self.current_dir.children[name], File):
                del self.current_dir.children[name]
                print(f"Removed the file '{name}'.")
            else:
                print(f"'{name}' is not a file.")
        else:
            print(f"A file with the name '{name}' does not exist.")
    
    def ls(self) -> None:
        """
        Lists all children of the current directory. Prints [DIR] or [FILE] before the name for readability.
        """
        for child in self.current_dir.children.values():
            if isinstance(child, Directory): # If the child is a directory, print [DIR] before the name.
                print(f"[DIR] {child.name}")
            elif isinstance(child, File): # If the child is a file, print [FILE] before the name.
                print(f"[FILE] {child.name}")
    
    def cd(self, path) -> None:
        """
        Changes the current directory.
        Supports both relative and absolute paths, as well as the .. operator.
        """
        try:
            target = self.path_validator(path)
            if target == self.root: # If the target is the root, set the current directory to the root.
                self.current_dir = self.root
            if isinstance(target, Directory): # If the target is a directory, set the current directory to the target.
                self.current_dir = target
                self.current_dir.visit_count += 1
                self.current_dir.last_visit = time.time()
            else:
                print(f"'{path}' is not a valid directory.")
        except FileNotFoundError:
            print(f"'{path}' is not a valid directory.")
        

    def get_all_directories(self, directory) -> list:
        """
        A recursive function to get all directories in the filesystem.
        directory: Directory object to start the search from.
        """
        directories = [directory]
        for child in directory.children.values(): # Recursively get all directories.
            if isinstance(child, Directory):
                directories.extend(self.get_all_directories(child))
        return directories
    
    def calculate_sorting_value(self, directory) -> float:
        """
        Calculates a sorting value for a directory based on its visit count and last visit time.
        The formula has an inverse relationship with the time since the last visit.
        """
        time_since_last_visit = time.time() - directory.last_visit
        recency_factor = 1 / (1 + math.log1p(time_since_last_visit)) # The +1 is to avoid division by zero.
        return directory.visit_count * recency_factor
    
    def quickaccess(self) -> list:
        """
        Get the top 5 most visited directories
        """
        all_directories = self.get_all_directories(self.root)
        most_visited = sorted(all_directories, key=self.calculate_sorting_value, reverse=True) # Sort the directories based on the sorting value.
        return most_visited[:5]
    
    def path_validator(self, path) -> FileSystemObject:
        """
        Checks if a valid relative or absolute path exists to a directory. Returns the directory if it exists.
        """
        if path == "/":
            return self.root
        target_dir = self.root if path.startswith("/") else self.current_dir
        path_split = path.strip("/").split("/")

        for part in path_split:
            if part == "..":
                if target_dir.parent: # As in normal command prompt, nothing will happen if cd .. is called in the root directory.
                    target_dir = target_dir.parent # A parent was found!
            elif part in target_dir.children: # Navigates to the directory in case it exists and is a directory.
                target_dir = target_dir.children[part]
            else:
                raise FileNotFoundError(f"Path '{path}' not found.")
        return target_dir

    
    def save_state(self) -> None:
        """
        Saves the state of the filesystem.
        """
        current_state = self.serialize_directory(self.root) # Serialize the root directory.
        json_data = json.dumps(current_state) # Convert the dictionary to a json string.
        encrypted_data = self.cipher.encrypt(json_data.encode('utf-8')) # Encrypt the json string in utf8 byte form.

        puppy_picture = Image.open("puppy_picture.png")
        meta = PngImagePlugin.PngInfo() # Create a metadata object.

        meta.add_text("vfs_state", encrypted_data.decode('latin1')) # Add the encrypted data to the metadata.

        puppy_picture.save("puppy_picture.png", "PNG", pnginfo=meta) # Save metadata within the image.
    
    
    def load_state(self) -> None:
        """
        Loads the state of the filesystem from a png_image.
        Only currently works with a png image that has been previously saved with the save_state method.
        The image "puppy_picture.png" has been previously uploaded with metadata for this to work.
        """
        try:
            puppy_picture = Image.open("puppy_picture.png") # Open the image.
            encrypted_data = puppy_picture.info.get("vfs_state", None) # Get the 'vfs_state' metadata.
            if encrypted_data is None:
                raise FileNotFoundError("No state found.") # If no metadata is found, raise an error.
            
            try:
                decrypted_data = self.cipher.decrypt(encrypted_data.encode('latin1')) # Try to decrypt the data.
            except InvalidToken:
                # If decryption fails, assume the data is unencrypted and decode it directly
                decrypted_data = encrypted_data.encode('latin1')
            
            system_state = json.loads(decrypted_data) # Load the json string to a dictionary.
            
            self.root = self.deserialize_directory(system_state, None) # Deserialize the dictionary to a directory.
            self.current_dir = self.root # Set the root as current directory.
        except FileNotFoundError: # If no state is found, initialize a new filesystem.
            self.root = Directory("/", None, self)
            self.current_dir = self.root
        except json.JSONDecodeError: # If the json is corrupted, initialize a new filesystem.
            self.root = Directory("/", None, self)
            self.current_dir = self.root
        except KeyError as e: # If a key error occurs, the state is corrupted. Initialize a new filesystem.
            self.root = Directory("/", None, self)
            self.current_dir = self.root



    def serialize_directory(self, directory) -> dict:
        """
        Recursively serializes a directory and its children.
        """
        return {
            'name': directory.name,
            'children': {name: self.serialize_directory(child) if isinstance(child, Directory) else self.serialize_file(child) for name, child in directory.children.items()},
            'visit_count': directory.visit_count,
            'last_visit': directory.last_visit
        }
    
    def serialize_file(self, file) -> dict:
        """
        Serializes the file.
        """
        return {
            'name': file.name,
            'content': base64.b64encode(file.content).decode('utf-8'),
            'when_created': file.when_created
        }
    
    def deserialize_directory(self, data, parent) -> 'Directory':
        """
        Deserializes a dictionary to a directory. Occures when loading the filesystem state.
        """
        if 'name' not in data:
            raise KeyError("The 'name' key is missing in the directory data.")
        
        directory = Directory(data['name'], parent, self)
        directory.visit_count = data.get('visit_count', 0)
        directory.last_visit = data.get('last_visit', time.time())
        for name, child_data in data.get('children', {}).items():
            if 'content' in child_data:
                directory.add_child(self.deserialize_file(child_data, directory))
            else:
                directory.add_child(self.deserialize_directory(child_data, directory))
        return directory
    
    def deserialize_file(self, data, parent) -> 'File':
        """
        Deserializes a dictionary to a file.
        """
        file = File(data['name'], parent, base64.b64decode(data['content']))
        file.when_created = data['when_created']
        return file
    
    def write_file(self, path, content) -> None:
        """
        Writes content to a file.
        """
        try:
            file = self.path_validator(path)
            if isinstance(file, File): # If the path is a file, write the content.
                file.write(content)
                print(f"Content written to '{path}'.")
            else:
                print(f"'{path}' is not a file.")
        except FileNotFoundError as e:
            print(e)

    def read_file(self, path) -> bytes:
        """
        Reads the content of a file.
        """
        try:
            file = self.path_validator(path)
            if isinstance(file, File): # If the path is a file, read the content.
                return file.read()
            else:
                print(f"'{path}' is not a file.")
        except FileNotFoundError as e:
            print(e)