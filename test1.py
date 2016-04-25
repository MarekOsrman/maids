import os
import re
import test1_GUI


INIT_PATH2="/mnt/data/Multimedia/Music/Collection/"
INIT_PATH="/run/media/marek/Storage/Music/SORT/"



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
            ["soundtrack", r'[([{]?(ost|soundtrack|score)[)\]}]?'],
            ["va", r'[([{]?(va|various artists)[)\]}]?']
        ]
        for tag in self.tags:
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


class Maiden:
    def __init__(self, init_path):

        self.init_path = init_path
        self.artists = []

        self.process_path(self.init_path)

    def init_artibtrary_artists(self):
        self.insert_artist("_OST")
        self.insert_artist("_VA")

    def process_path(self, path):
        """Process current path and recursively descend into each of the directories listed."""
        for entry in os.scandir(path):
            if entry.is_dir() and not re.match(mb.omit_directories, entry.name):
                self.process_dir(entry.name, path + entry.name)
                self.process_path(path + entry.name + "/")

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




print("Welcome to MAIDS !")

mb = Matchbox()
m = Maiden(INIT_PATH2)
m.print_artists()