import io


class InMemoryFileSystem:

  def __init__(self):
    self.root = {}  # Root directory represented as a dictionary
    self.current_dir = self.root
    self.current_path = ""

  def _get_path(self, path):
    """
    Returns a list representing the path as a sequence of directory names.
    """
    # print(path)
    return path.strip("/").split("/")

  def run(self):
    """
    Runs the infinite loop for user interaction.
    """
    while True:
      command = input("root/" + self.current_path.strip("/") + "> ").strip()
      if command == "exit":
        break
      elif command.startswith("ls"):
        path = command.split()[1] if len(command.split()) > 1 else ""
        self.ls(self.current_path + path)
      elif command.startswith("mkdir"):
        path = command.split()[1]
        self.mkdir(self.current_path + path)
      elif command.startswith("cd"):
        path = command.split()[1]
        if path not in ["`" , "/" ,".."]:
          path = self.current_path + path
        self.cd(path)
      elif command.startswith("grep"):
        pattern = command.split()[1].strip("'")
        path = command.split()[2]
        self.grep(pattern, self.current_path + path)
      elif command.startswith("touch"):
        path = command.split()[1]
        self.touch(self.current_path + path)
      elif command.startswith("echo"):
        content = ((" ").join(command.split()[1:-1])).strip("'")
        path = command.split()[-1]
        self.echo(content, self.current_path + path)
      elif command.startswith("cat"):
        path = command.split()[1]
        self.cat(self.current_path + path)
      elif command.startswith("cp"):
        source = self.current_path + command.split()[1]
        destination = command.split()[2]
        self.cp(source, destination)
      elif command.startswith("mv"):
        source = self.current_path + command.split()[1]
        destination = command.split()[2]
        self.mv(source, destination)
      elif command.startswith("rm"):
        source = command.split()[1]
        self.rm(self.current_path + source)
      else:
        print("Invalid command")

  def mkdir(self, path):
    """
    Creates a new directory.
    """
    current_dir = self.current_dir
    for directory in self._get_path(path):
      if directory not in current_dir:
        current_dir[directory] = {".": {}}
        current_dir = current_dir[directory]

  def cd(self, path):
    """
    Changes the current directory.
    """
    if path == "~" or path == "/":
      self.current_dir = self.root
      return
    if path == "..":
      print(self.current_path)
      path_array = self.current_path.strip("/").split("/")[0:-1]
      new_dir = self.root
      self.current_path = ""
    else:
      path_array = self._get_path(path)
      new_dir = self.current_dir
    current_path = ""
    for directory in path_array:
      if directory not in new_dir:
        print("Directory does not exist")
        return
      new_dir = new_dir[directory]
      current_path += directory + "/"

    self.current_path += current_path
    self.current_dir = new_dir

  def ls(self, path):
    """
    Lists contents of a directory.
    """
    initial_dir = self.current_dir
    if len(path) > 0:
      self.cd(path)

    current_dir = self.current_dir
    if not current_dir and len(current_dir) == 0:
      print("Directory does not exist")
    else:
      print(", ".join(current_dir.keys()))
    if initial_dir != self.current_dir:
      while initial_dir != self.current_dir:
        self.cd("..")

  def _get_dir(self, path):
    """
    Retrieves the directory object based on the path.
    """
    if len(path) == 0:
      return self.root
    current_dir = self.root
    for directory in self._get_path(path):
      if directory not in current_dir:
        return None
      current_dir = current_dir[directory]
    return current_dir

  def touch(self, path):
    """
    Creates a new empty file.
    """
    current_dir = self.current_dir
    filename = path.split("/")[-1]  # Extract filename from path
    if filename in current_dir and not isinstance(current_dir[filename], dict):
      print("File already exists")
      return
    current_dir[filename] = io.StringIO(
    )  # Empty string represents an empty file
    print("File created successfully")

  def echo(self, content, path):
    """
    Writes text to a file.
    """
    current_dir = self.current_dir
    if not current_dir:
      print("Directory does not exist")
      return
    filename = path.split("/")[-1]  # Extract filename from path
    current_dir[filename].write(content)
    print("Successfully wrote to file")

  def cat(self, path):
    """
    Display the contents of a file.
    """
    if len((path.strip("/").split("/"))) <= 1:
      current_dir = self.current_dir
    else:
      current_dir = self._get_dir("/".join(path.strip("/").split("/")[0:-1]))
    if not current_dir:
      print("Directory does not exist")
      return
    filename = path.split("/")[-1]  # Extract filename from path
    if filename not in current_dir or not isinstance(current_dir[filename],
                                                     io.StringIO):
      print("File does not exist or is not a text file")
      return
    print(current_dir[filename].getvalue())

  # Bonus: Grep implementation (basic string search)
  def grep(self, pattern, path):
    """
    Searches for a pattern in a file.
    """
    path_components = self._get_path(path)
    current_dir = self._get_dir("/".join(
                                 path_components[:-1]))
    if not current_dir:
      print("Directory does not exist")
      return
    filename = path.split("/")[-1]  # Extract filename from path
    if filename not in current_dir or not isinstance(current_dir[filename],
                                                     io.StringIO):
      print("File does not exist or is not a text file")
      return
    if pattern in current_dir[filename].getvalue().split():
      print(f"Pattern '{pattern}' found in {path}")
    else:
      print(f"Pattern '{pattern}' not found in {path}")

  def mv(self, source, destination):
    """
    Move a file or directory to another location.
    """
    source_dir, source_file = self._get_dir_and_filename(source)
    dest_dir = self._get_dir(destination)

    # Error handling for invalid source or destination
    if not source_dir or not source_file:
      print(f"Source '{source}' does not exist")
      return
    if not dest_dir:
      print(f"Destination directory '{destination}' does not exist")
      return

    # Check if destination is a file (not allowed)
    if destination.split("/")[-1] != "" and destination in dest_dir:
      print("Destination cannot be an existing file")
      return

    # Move the file/directory by removing from source and adding to destination
    moved_item = source_dir.pop(source_file)
    dest_dir[source.split("/")[-1]] = moved_item
    print(f"Successfully moved '{source}' to '{destination}'")

  def cp(self, source, destination):
    """
    Copy a file or directory to another location.
    """
    source_dir, source_file = self._get_dir_and_filename(source)
    dest_dir = self._get_dir(destination)
    # Error handling for invalid source or destination
    if not source_dir or not source_file:
      print(f"Source '{source}' does not exist")
      return
    if not dest_dir:
      print(f"Destination directory '{destination}' does not exist")
      return

    # Check if destination is a file (not allowed)
    if destination.split("/")[-1] != "" and destination in dest_dir:
      print("Destination cannot be an existing file")
      return

    # Copy the file/directory by creating a new entry in the destination
    copied_item = source_dir[source_file]
    if isinstance(copied_item, dict):  # Copying a directory (deep copy)
      dest_dir[source.split("/")[-1]] = {}
      self._copy_dir(copied_item, dest_dir[source.split("/")[-1]], source_file)
    elif isinstance(copied_item, io.StringIO):
      copied_data = copied_item.getvalue()
      dest_dir[source.split("/")[-1]] = io.StringIO(copied_data)
    else:  # Copying a file
      dest_dir[source.split("/")
               [-1]] = copied_item.copy()  # Shallow copy for files
    print(f"Successfully copied '{source}' to '{destination}'")

  def _copy_dir(self, source_dir, dest_dir, source_file):
    """
    Helper function to recursively copy a directory (deep copy).
    """
    #print(source_dir, dest_dir, source_file,"copy_dir")
    for item, value in source_dir.items():
      if isinstance(value, dict):
        dest_dir[item] = {}

        self._copy_dir(value, dest_dir[item], source_file)
      elif isinstance(value, io.StringIO):
        copied_data = value.getvalue()
        dest_dir[item] = io.StringIO(copied_data)
      else:

        dest_dir[source_file] = value.copy()  # Shallow copy for files

  def rm(self, path):
    """
    Remove a file or directory.
    """
    current_dir, filename = self._get_dir_and_filename(path)

    # Error handling for non-existent item
    if not current_dir or not filename:
      print(f"Item '{path}' does not exist")
      return
    print("Are you sure (Y/N)?")
    choice = input()

    if choice == "Y":
      # Remove the item from the current directory
      del current_dir[filename]
      print(f"Successfully removed '{path}'")
    return

  def _get_dir_and_filename(self, path):
    """
    Separates the directory path and filename from a given path.
    """
    path_components = self._get_path(path)
    if not path_components:
      return None, None
    directory = self._get_dir("/".join(
        path_components[:-1]))  # Construct path to parent dir
    if directory == None:
      directory = self.root
    filename = path_components[-1]
    return directory, filename


if __name__ == "__main__":
  file_system = InMemoryFileSystem()
  file_system.run()
