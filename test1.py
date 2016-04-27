import os
import re
import test1_GUI

INIT_PATH2="/mnt/data/Multimedia/Music/Collection/"
INIT_PATH3="/mnt/data/Multimedia/Music/SORT/"
INIT_PATH="/run/media/marek/Storage/Music/SORT/"
INIT_PATH_SD="/run/media/marek/7266-0950"



class Matchbox:
    """TODO!!! Redo the whole class. Seriously."""
    def __init__(self):
        self.delete_keywords = re.compile(r'(\- )?[([{]?(flac|deluxe version)[)\]}]?', re.IGNORECASE)
        self.omit_directories = re.compile(r'scan|scans|artwork|art|cover', re.IGNORECASE)
        self.years = re.compile(r'[([{]?[0-9]{4}[)\]}]?')
        self.brackets = re.compile(r'[([{]?[)\]}]?')
        self.soundtrack = re.compile(r'[([{]?(ost|soundtrack|score)[)\]}]?', re.IGNORECASE)

        self.init_tags()

    def init_tags(self):
        self.tags = [
            ["soundtrack", r'(ost|soundtrack|score)'],
            ["va", r'(va|various artists)']
        ]
        for tag in self.tags:
            tag[1] = r'[([{\- ]' + tag[1] + r'[)\]}\- ]'
            tag[1] = re.compile(tag[1], re.IGNORECASE)

    def get_tag_pair(self, tag_name):
        for tag in self.tags:
            if tag[0] == tag_name:
                return (tag[0], tag[1])
        return False


class Artist:
    def __init__(self, name):
        self.name = name
        self.albums = []

    def add_album(self, newAlbum):
        self.albums.append(newAlbum)


class Album:
    def __init__(self, name, path):
        self.name = name
        self.path = path
        self.year = ""
        self.tags = []

    def set_year(self, year):
        self.year = year

    def has_tag(self, tag_name):
        if tag_name in self.tags:
            return True
        return False


class Monitor:
    def __init__(self):
        pass

    def folder_to_list(self, root):
        def process(path):
            entries = []
            for entry in os.scandir(path):
                if entry.is_dir():
                    subs = process(path + entry.name + "/")
                    if subs:
                        entries.append([entry.name, subs])
                    else:
                        entries.append([entry.name])
            return entries

        return process(root)

    def folder_to_text(self, root):
        def process(path, level):
            entries = ""
            for entry in os.scandir(path):
                if entry.is_dir():
                    entries += level*4*" " + entry.name + '\n'
                    entries += process(path + entry.name + "/", level + 1)
            return entries

        return process(root, 0)

    def list_to_text(self, list):
        def process(list, level):
            entries = ""
            for entry in list:
                entries += level*4*" " + entry[0] + '\n'
                if len(entry) > 1:
                    entries += process(entry[1], level + 1)

            return entries

        return process(list, 0)

    def text_to_list(self, text):
        # TODOOOOOO
        list = []
        for line in text.splitlines():
            if line.startswith("    "):
                pass
            print(line)

class Maiden:
    def __init__(self, init_path):
        self.init_path = init_path
        if not self.init_path.endswith("/"):
            self.init_path += "/"
        self.artists = []
        self.init_artibtrary_artists()

        #self.process_path(self.init_path)

        self.mon = Monitor()
        #list = self.mon.folder_to_list(self.init_path)

        #self.process_list(list, self.init_path)

    def init_artibtrary_artists(self):
        self.insert_artist("_OST")
        self.insert_artist("_VA")

    def process_path(self, path):
        """Process current path and recursively descend into each of the directories listed."""
        for entry in os.scandir(path):
            if entry.is_dir():
                if not re.match(mb.omit_directories, entry.name):
                    self.process_dir(entry.name, path + entry.name)
                self.process_path(path + entry.name + "/")

    def process_list(self, list, path):
        for entry in list:
            if not re.match(mb.omit_directories, entry[0]):
                self.process_dir(entry[0], path + entry[0])
            if len(entry) > 1:
                self.process_list(entry[1], path + entry[0] + "/")

    def process_dir(self, input, curr_path):
        """Process the directory path, split the label into artist-album pair and call insert functions."""
        input = self.parse_pre(input)

        input, tags = self.analyze_tags(input)

        artist_str, album_str = self.dir_split(input)
        artist = self.insert_artist(artist_str)
        self.insert_album(artist, album_str, curr_path)

    def analyze_tags(self, input):
        tags = []
        for (tag_name, tag_regx) in mb.tags:
            m = re.search(tag_regx, input)
            if m:
                input = re.sub(tag_regx, '', input)
                input = self.parse_post(input)
                tags.append(tag_name)
        return (input, tags)

    def insert_artist(self, artist_str):
        """Insert artist into database and return the inserted artist."""
        for artist in self.artists:
            if artist.name == artist_str:
                return artist
        new_artist = Artist(artist_str.strip())
        self.artists.append(new_artist)
        return new_artist

    def insert_album(self, artist, album_str, curr_path):
        """Insert new album for the artist."""
        m = re.search(mb.years, album_str)
        album_str = re.sub(mb.years, '', album_str)
        new_album = Album(self.parse_post(album_str), curr_path)
        if m:
            year = m.group(0)
            year = re.sub(mb.brackets, '', year)
            new_album.set_year(year)

        artist.add_album(new_album)


    def parse_pre(self, input):
        """Delete obsolete keywords before splitting."""
        input = re.sub(mb.delete_keywords, '', input)

        return input

    def parse_post(self, input):
        """Delete trash after splitting and parsing."""
        input = input.strip()
        if input.endswith(" -"):
            input = input[:-2]

        return input

    def dir_split(self, input):
        """Split the input by the dash delimeter."""
        parts = input.split(" - ", maxsplit=1)
        if len(parts) == 2:
            return parts[0], parts[1]
        else:
            return "", parts[0]

    def print_artists(self):
        """Simple printout for the database."""
        for artist in self.artists:
            print(artist.name)
            for album in artist.albums:
                print("    " + album.year + "  " + album.name)

    def handler_run(self):
        self.list = self.mon.folder_to_list(self.init_path)

        self.process_list(self.list, self.init_path)



print("Welcome to MAIDS !")

mb = Matchbox()
m = Maiden(INIT_PATH3)
#m.handler_run()
m.print_artists()

#mon = Monitor()
#list = mon.folder_to_list(INIT_PATH3)
#for l in list:
#    pass
#    #print(l)
#text = mon.list_to_text(list)
#print(text)