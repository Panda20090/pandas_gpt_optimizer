import unittest
import os
import json
import tempfile
from brain.list_files_and_directories import list_files_and_directories, save_file_list
from tkinter import Tk, Text, Scrollbar, END

# Ensure the test output directory exists
test_output_dir = os.path.join(os.path.dirname(__file__), 'test_output_files')
os.makedirs(test_output_dir, exist_ok=True)

class TestListFilesAndDirectories(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory for testing
        self.test_dir = tempfile.TemporaryDirectory()
        self.root_directory = self.test_dir.name
        # Create some test files and directories
        os.makedirs(os.path.join(self.root_directory, 'dir1'))
        os.makedirs(os.path.join(self.root_directory, 'dir2'))
        with open(os.path.join(self.root_directory, 'file1.txt'), 'w') as f:
            f.write('This is a test file.')
        with open(os.path.join(self.root_directory, 'file2.txt'), 'w') as f:
            f.write('This is another test file.')

    def tearDown(self):
        # Cleanup the temporary directory
        self.test_dir.cleanup()

    def test_list_files_and_directories(self):
        result = list_files_and_directories(self.root_directory)
        self.assertIn('files', result)
        self.assertIn('directories', result)
        self.assertEqual(len(result['files']), 2)
        self.assertEqual(len(result['directories']), 2)
        self._display_test_output(result)

    def test_save_file_list(self):
        output_file = os.path.join(test_output_dir, "test_file_list.txt")
        save_file_list(self.root_directory, output_file)
        self.assertTrue(os.path.exists(output_file))
        with open(output_file, 'r') as f:
            data = json.load(f)
            self.assertIn('files', data)
            self.assertIn('directories', data)
            self.assertEqual(len(data['files']), 2)
            self.assertEqual(len(data['directories']), 2)
        os.remove(output_file)
        self._display_test_output(data)

    def _display_test_output(self, data):
        root = Tk()
        root.title("Test Output")

        text = Text(root)
        scroll = Scrollbar(root, command=text.yview)
        text.configure(yscrollcommand=scroll.set)
        text.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        text.insert(END, json.dumps(data, indent=4))
        text.insert(END, "\nFiles created in test_output_files directory match the project directory.")

        root.after(5000, root.destroy)  # Automatically close after 5 seconds
        root.mainloop()

if __name__ == '__main__':
    unittest.main()
