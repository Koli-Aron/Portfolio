from VirtualFileSystem import VirtualFileSystem, Directory, File
import cmd
import time

class FS_interface(cmd.Cmd):
    prompt = ">>> "
    intro = "Welcome to the filesystem interface. Type 'help' for a list of commands."

    def __init__(self):
        super().__init__()
        password = input("Enter the password: ")
        self.fs = VirtualFileSystem(password) # Creates the Filesystem object.
        self.update_prompt()

    def update_prompt(self):
        """
        Updates the CMD prompt to show the current directory. Necessary after changing the current directory.
        """
        self.prompt = f":{self.fs.current_dir.get_path()} > "

    def do_cd(self, arg):
        """
        Changes the current directory.
        """
        self.fs.cd(arg)
        self.update_prompt() # Update the prompt to show the new current directory

    def do_ls(self, arg):
        """
        Lists all children of the current directory.
        """
        self.fs.ls()

    def do_mkdir(self, arg):
        """
        Creates a new directory.
        """
        self.fs.make_dir(arg)

    def do_rmdir(self, arg):
        """
        Removes a directory.
        """
        self.fs.remove_dir(arg)

    def do_mkfile(self, arg) -> None:
        """
        Creates a new file.
        """
        self.fs.make_file(arg)

    def do_rmfile(self, arg) -> None:
        """
        Rmoves a file.
        """
        self.fs.remove_file(arg)

    def do_readfile(self, arg) -> None:
        """
        Reads the contents of a file.
        """
        output = self.fs.read_file(arg)
        print(output.decode('utf-8'))

    def do_writefile(self, arg) -> None:
        """
        Writes to a file.
        """
        text = input("Enter the text to write to the file: ")
        self.fs.write_file(arg, text.encode('utf-8'))

    def do_help(self, arg=None) -> None:
        """
        Displays all possible commands.
        """
        print("Commands:")
        print("     cd <dir_name/path> - Change the current directory.")
        print("     ls - List all children of the current directory.")
        print("     mkdir <dir_name/path> - Create a new directory.")
        print("     mkfile <file_name/path> - Create a new file.")
        print("     readfile <file_name> - Read the contents of a file.")
        print("     writefile <file_name> - Write to a file.")
        print("     rmdir <file_name> - Removes a directory and all subdirectories.")
        print("     rmfile <file_name> - Removes a file.")
        print("     quickaccess - Open the quicksearch interface.")
        print("     exit - Exit the interface.")
    
    def do_exit(self, arg) -> bool:
        """
        Exits the interface.
        """
        self.fs.save_state() # Save the current filesystem state.
        print("Fare thee well.")
        return True
    
    def do_quickaccess(self, arg=None) -> None:
        """
        Finds the top 5 most visited directories and allows the user to quickly navigate to them.
        """
        print("Quickaccess - quickly access the most visited directiories.")
        most_visited = self.fs.quickaccess() # Get the top 5 most visited directories
        for i, directory in enumerate(most_visited): # Use enumerate to get the indexes. This is necessary for cases where there are less than 5 directories.
            print(f"    {i+1}. {directory.get_path()} - {directory.visit_count} visits.") 
        while True:
            choice = input("Enter the number to navigate to the directory or 'exit' to return: ")
            if choice.lower() == 'exit': # Exit the quickaccess interface
                break
            elif choice.isdigit() and 1 <= int(choice) <= len(most_visited): # Check if the input is a number and within the range of the most visited directories
                selected_dir = most_visited[int(choice) - 1]
                self.fs.current_dir = selected_dir
                self.fs.current_dir.visit_count += 1  # Increment visit count
                self.fs.current_dir.last_visit = time.time()  # Update last visit time
                self.update_prompt() # Update the prompt to show the new current directory
                break
            else:
                print("Invalid choice. Please enter a number between 1 and 5 or 'exit'.")

if __name__ == "__main__":
    FS_interface().cmdloop()  # Start CMD loop