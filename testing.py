import unittest
import test1

class TestMaiden_dirsplit(unittest.TestCase):

    def setUp(self):
        self.maid = test1.Maiden("")

    def test_dirsplit_normal(self):
        self.assertEqual(self.maid.dir_split("Artist - Album"), ("Artist", "Album"))

    def test_dirsplit_not_present(self):
        self.assertEqual(self.maid.dir_split("Artist Album"), ("", "Artist Album"))

    def test_dirsplit_extra(self):
        self.assertEqual(self.maid.dir_split("Artist - Album - Extra"), ("Artist", "Album - Extra"))

    def test_dirsplit_single_dash(self):
        self.assertEqual(self.maid.dir_split("-"), ("", "-"))

    def test_dirsplit_dash_with_spaces(self):
        self.assertEqual(self.maid.dir_split(" - "), ("", ""))


class TestMaiden_list_processing(unittest.TestCase):

    def setUp(self):
        self.maid = test1.Maiden("PREPATH/")

    def test_one_item(self):
        list = [["Artist - Album"]]
        self.maid.process_list(list, "PATH/")
        result = self.maid.print_artists()
        self.assertEqual(result, "Artist\n    Album")


class TestMaiden_real_stuff(unittest.TestCase):

    def setUp(self):
        self.maid = test1.Maiden("/mnt/data/Multimedia/Music/SORT/")

    def test_print(self):
        #print(self.maid.mon.folder_to_list(self.maid.init_path))
        pass