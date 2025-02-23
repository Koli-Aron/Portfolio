import unittest
from unittest.mock import patch
from io import StringIO
from VirtualFileSystem import VirtualFileSystem, Directory, File

class TestFS(unittest.TestCase):
    def setUp(self):
        self.fs = VirtualFileSystem("test_password")

    def test_make_dir(self):
        self.fs.make_dir("test_dir")
        self.assertIn("test_dir", self.fs.current_dir.children)
        self.assertIsInstance(self.fs.current_dir.children["test_dir"], Directory)

    def test_delete_dir(self):
        self.fs.make_dir("test_dir")
        self.fs.remove_dir("test_dir")
        self.assertNotIn("test_dir", self.fs.current_dir.children)

    def test_make_file(self):
        self.fs.make_file("test_file")
        self.assertIn("test_file", self.fs.current_dir.children)
        self.assertIsInstance(self.fs.current_dir.children["test_file"], File)

    def test_delete_file(self):
        self.fs.make_file("test_file")
        self.fs.remove_file("test_file")
        self.assertNotIn("test_file", self.fs.current_dir.children)
    
    def test_cd_forward(self):
        self.fs.make_dir("test")
        self.fs.cd("test")
        self.assertEqual(self.fs.current_dir.name, "test")

    def test_cd_backward(self):
        self.fs.make_dir("test")
        self.fs.cd("test")
        self.fs.cd("..")
        self.assertEqual(self.fs.current_dir.name, "/")

    def test_cd_invalid(self):
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.fs.cd("invalid")
            output = fake_out.getvalue().strip()
            self.assertIn("'invalid' is not a valid directory.", output)

    def test_ls(self):
        self.fs.make_dir("test_dir")
        self.fs.make_file("test_file")
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.fs.ls()
            output = fake_out.getvalue().strip()
            self.assertIn("[DIR] test_dir", output)
            self.assertIn("[FILE] test_file", output)

    def test_cd_root(self):
        self.fs.make_dir("test")
        self.fs.cd("test")
        self.fs.cd("/")
        self.assertEqual(self.fs.current_dir.name, "/")

    def test_cd_slashes(self):
        self.fs.make_dir("/this")
        self.assertIn("this", self.fs.current_dir.children)
        self.fs.make_dir("/this/is")
        self.fs.make_dir("/this/is/a")
        self.fs.make_dir("/this/is/a/test")
        self.fs.cd("/this/is/a")
        self.assertIn("test", self.fs.current_dir.children)

    def test_stress(self):
        """
        Stress test quickaccess by adding 1000 directories and files.
        """
        for i in range(10000):
            self.fs.make_dir(f"dir_{i}")
            self.fs.make_file(f"file_{i}")
        self.fs.ls()
        self.fs.save_state()
        self.fs.load_state()
        self.fs.ls()
        self.assertIn("dir_999", self.fs.current_dir.children)
        for i in range(10000):
            self.fs.remove_dir(f"dir_{i}")
            self.fs.remove_file(f"file_{i}")
        self.fs.save_state()
        self.fs.quickaccess()


if __name__ == "__main__":
    unittest.main()