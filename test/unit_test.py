import unittest
import sys
from io import StringIO
sys.path.append("..")
import main

class InMemoryFileSystemTest(unittest.TestCase):

  def setUp(self):
    self.fs = main.InMemoryFileSystem()

  def test_init(self):
    self.assertEqual(self.fs.current_dir, self.fs.root)
    self.assertEqual(self.fs.current_path, "")

  def test_mkdir(self):
    self.fs.mkdir("dir1")
    self.assertIn("dir1", self.fs.root)
    self.fs.mkdir("dir1/dir2")
    self.assertIn("dir2", self.fs.root["dir1"])

  def test_mkdir_existing(self):
    self.fs.mkdir("dir1")
    with self.assertRaises(Exception):
      self.fs.mkdir("dir1")

  def test_cd(self):
    self.fs.mkdir("dir1")
    self.fs.cd("dir1")
    self.assertEqual(self.fs.current_dir, self.fs.root["dir1"])
    self.assertEqual(self.fs.current_path, "dir1")
    self.fs.cd("/")
    self.assertEqual(self.fs.current_dir, self.fs.root)
    self.assertEqual(self.fs.current_path, "")

  def test_cd_invalid_path(self):
    with self.assertRaises(Exception):
      self.fs.cd("invalid/path")
    with self.assertRaises(Exception):
      self.fs.cd("..")  # No parent directory at root

  def test_ls(self):
    self.fs.mkdir("dir1")
    self.fs.touch("file1.txt")
    self.fs.ls("")
    self.assertIn("dir1", self.fs.root.keys())
    self.assertIn("file1.txt", self.fs.root.keys())
    self.fs.ls("dir1")
    # No check for output since it's printed

  def test_ls_empty_dir(self):
    self.fs.mkdir("dir1")
    self.fs.ls("dir1")
    # No check for output since it's printed

  def test_ls_invalid_path(self):
    with self.assertRaises(Exception):
      self.fs.ls("invalid/path")

  def test_touch(self):
    self.fs.touch("file1.txt")
    self.assertIn("file1.txt", self.fs.root)
    self.assertIsInstance(self.fs.root["file1.txt"], StringIO)
    with self.assertRaises(Exception):
      self.fs.touch("file1.txt")  # Already exists

  def test_echo(self):
    self.fs.mkdir("dir1")
    self.fs.touch("file1.txt")
    self.fs.echo("This is some text", "dir1/file1.txt")
    self.assertEqual(self.fs.root["dir1"]["file1.txt"].getvalue(), "This is some text")
    with self.assertRaises(Exception):
      self.fs.echo("Text", "invalid/path/file.txt")  # Directory doesn't exist

  def test_cat(self):
    self.fs.touch("file1.txt")
    self.fs.echo("Hello world", "file1.txt")
    self.fs.cat("file1.txt")
    # No check for output since it's printed
    with self.assertRaises(Exception):
      self.fs.cat("invalid/path/file.txt")  # File doesn't exist

  def test_cat_directory(self):
    with self.assertRaises(Exception):
      self.fs.cat("dir1")  # Can't cat a directory
  def test_grep(self):
    self.fs.grep("test", "file1.txt")
    # No direct output check, as the method prints to console
    self.fs.grep("invalid_pattern", "file1.txt")
    # No direct output check, as the method prints to console

  def test_grep_nonexistent_file(self):
    with self.assertRaises(Exception):
      self.fs.grep("test", "invalid/file.txt")

  def test_cp(self):
    self.fs.cp("file1.txt", "file2.txt")
    self.assertIn("file2.txt", self.fs.root)
    self.assertEqual(self.fs.root["file1.txt"].getvalue(), self.fs.root["file2.txt"].getvalue())
    with self.assertRaises(Exception):  # Destination as existing file
      self.fs.cp("file1.txt", "file2.txt")
    self.fs.mkdir("dir1")
    self.fs.cp("file1.txt", "dir1/file2.txt")  # Copy to directory
    self.assertIn("file2.txt", self.fs.root["dir1"])
    with self.assertRaises(Exception):  # Non-existent source
      self.fs.cp("invalid.txt", "file3.txt")
    with self.assertRaises(Exception):  # Non-existent destination directory
      self.fs.cp("file1.txt", "dir2/file3.txt")

  def test_mv(self):
    self.fs.mv("file1.txt", "moved_file.txt")
    self.assertNotIn("file1.txt", self.fs.root)
    self.assertIn("moved_file.txt", self.fs.root)
    with self.assertRaises(Exception):  # Move to existing file
      self.fs.mv("moved_file.txt", "file1.txt")
    self.fs.mkdir("dir2")
    self.fs.mv("moved_file.txt", "dir2/renamed_file.txt")  # Move to directory
    self.assertNotIn("moved_file.txt", self.fs.root)
    self.assertIn("renamed_file.txt", self.fs.root["dir2"])
    with self.assertRaises(Exception):  # Non-existent source
      self.fs.mv("invalid.txt", "new_file.txt")
    with self.assertRaises(Exception):  # Non-existent destination directory
      self.fs.mv("moved_file.txt", "dir3/renamed_file.txt")

  def test_rm(self):
    self.fs.rm("file1.txt")
    self.assertNotIn("file1.txt", self.fs.root)
    with self.assertRaises(Exception):  # Remove non-existent file
      self.fs.rm("invalid.txt")
    self.fs.touch("file2.txt")
    self.fs.echo("Some text", "file2.txt")
    print("Are you sure (Y/N)?")  # Simulate user input (assuming 'Y')
    self.fs.rm("file2.txt")
    self.assertNotIn("file2.txt", self.fs.root)
if __name__ == "__main__":
  unittest.main()
