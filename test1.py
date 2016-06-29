import os
import re
import argparse
import json
import cmd

INIT_PATH2="/mnt/data/Multimedia/Music/Collection/"
INIT_PATH3="/mnt/data/Multimedia/Music/SORT/"
INIT_PATH="/run/media/marek/Storage/Music/SORT/"
INIT_PATH_SD="/run/media/marek/7266-0950"


class Argumentor:
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        group = self.parser.add_mutually_exclusive_group()

        group.add_argument("-j", "--json", help="output JSON", action="store_true")
        group.add_argument("-l", "--list", help="output list", action="store_true")
        group.add_argument("-a", "--artists", help="output artists", action="store_true")
        self.parser.add_argument("path", help="The path that will be analyzed")



        self.args = self.parser.parse_args()

        self.path = self.args.path


class Matchbox:
    """TODO!!! Redo the whole class. Seriously."""
    def __init__(self):
        #self.delete_keywords = re.compile(r'(\- )?[([{]?(flac|hdtracks)[)\]}]?', re.IGNORECASE)
        self.delete_keywords = re.compile(r'(flac|hdtracks)', re.IGNORECASE)
        self.omit_directories = re.compile(r'scan|scans|artwork|art|cover', re.IGNORECASE)
        self.years = re.compile(r'[([{]?[0-9]{4}[)\]}]?')
        self.brackets = re.compile(r'[([{][)\]}]')
        self.unbracket = re.compile(r'[([{)\]}]')
        self.soundtrack = re.compile(r'[([{]?(ost|soundtrack|score)[)\]}]?', re.IGNORECASE)
        self.additional = re.compile(r'[([{](?:(.*))[)\]}]')
        self.dash = re.compile(r' *- *')

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


class Questionnaire:

    def ask(self, question):
        print(question)
        answer = input("> ")
        return answer

    def ask_artist_album(self, input_str):
        print("---------------------------------------")
        print("MAIDS could not process directory name.")
        print("DIRECTORY: " + input_str)
        print()
        print("Please insert ARTIST name below:")
        artist = input()
        print()
        print("Please insert ALBUM name below:")
        album = input()
        print()

        return (artist, album)

    def ask_years(self, dir_name, list_of_years):
        print("MAIDS could not process the album year.")
        print("DIRECTORY: " + dir_name)
        print("FOUND YEARS: " + list_of_years)
        print()
        print("Please input the correct year below:")
        year = input()
        print()

        return year

class Artist:
    def __init__(self, name):
        self.name = name
        self.albums = []

    def add_album(self, newAlbum):
        self.albums.append(newAlbum)

    def toJSON(self):
        JSONalbums = []
        for alb in self.albums:
            JSONalbums.append(alb.toJSON())
        return dict(name=self.name, albums=JSONalbums)

class ArtistEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Artist):
            return o.toJSON()
        return json.JSONEncoder.default(self, o)

class Album:
    def __init__(self, name, path):
        self.name = name
        self.path = path
        self.year = ""
        self.tags = []
        self.additional = ""

    def set_year(self, year):
        self.year = year

    def has_tag(self, tag_name):
        if tag_name in self.tags:
            return True
        return False

    def toJSON(self):
        return dict(name=self.name)

class AlbumEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Album):
            return {'name':o.name}
        return json.JSONEncoder.default(self, o)

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

    def list_to_json(self, list):
        return json.dumps(list, separators=(',', ':'), sort_keys=True, indent=2)

    def json_to_list(self, input_json):
        return json.loads(input_json)

class Maiden:
    def __init__(self, init_path, box):
        self.init_path = init_path
        if not self.init_path.endswith("/"):
            self.init_path += "/"
        self.artists = []

        self.box = box
        self.mon = Monitor()
        self.que = Questionnaire()


        self.list = self.mon.folder_to_list(self.init_path)

        self.process_list(self.list, self.init_path)

    def process_list(self, list, path):
        for entry in list:
            if not re.match(self.box.omit_directories, entry[0]):
                self.process_dir(entry[0], path + entry[0])
            if len(entry) > 1:
                pass
                #self.process_list(entry[1], path + entry[0] + "/")

    def process_dir(self, dir_name, curr_path):
        dir_name_cleaned = self.parse_pre(dir_name)

        dir_name_detagged, tags = self.analyze_tags(dir_name_cleaned)

        artist_str, album_str = self.dir_split(dir_name_detagged)
        year = self.analyze_year(dir_name_detagged, album_str)
        if not artist_str:
            (input_artist, input_album) = self.que.ask_artist_album(dir_name_detagged)
            if input_artist:
                artist_str = input_artist
            if input_album:
                album_str = input_album

        artist = self.insert_artist(artist_str)
        self.insert_album(artist, album_str, year, curr_path)

    def analyze_year(self, dir_name, string_with_year):
        years = []
        m = re.search(self.box.years, string_with_year)
        if m:
            years = m.groups()

        if len(years) > 2:
            year = self.que.ask_years(dir_name, years)
        elif len(years) == 1:
            year = years[0]
        else:
            year = ""

        year = re.sub(self.box.unbracket, '', year)

        return year

    def analyze_tags(self, tagged_string):
        tags = []
        for (tag_name, tag_regx) in self.box.tags:
            m = re.search(tag_regx, tagged_string)
            if m:
                tagged_string = re.sub(tag_regx, '', tagged_string)
                tagged_string = self.parse_post(tagged_string)
                tags.append(tag_name)
        return (tagged_string, tags)

    def insert_artist(self, artist_str):
        """Insert artist into database and return the inserted artist."""
        for artist in self.artists:
            if artist.name == artist_str:
                return artist
        new_artist = Artist(artist_str.strip())
        self.artists.append(new_artist)
        return new_artist

    def insert_album(self, artist, album_str, year, curr_path):
        """Insert new album for the artist."""
        album_str = re.sub(self.box.years, '', album_str)
        new_album = Album(self.parse_post(album_str), curr_path)
        new_album.set_year(year)

        artist.add_album(new_album)

    def delete_empty_brackets(self, input_str):
        output = re.sub(self.box.brackets, '', input_str)

        return output

    def parse_pre(self, input_str):
        """Delete obsolete keywords before splitting."""
        output = re.sub(self.box.delete_keywords, '', input_str)
        output = self.delete_empty_brackets(output)

        return output

    def parse_post(self, input_str):
        """Delete trash after splitting and parsing."""
        output = re.sub(self.box.additional, '', input_str)
        output = output.strip()
        output = re.sub(self.box.dash, '', output)

        return output

    def dir_split(self, input_str):
        """Split the input by the dash delimeter. Artist - Album"""
        parts = input_str.split(" - ", maxsplit=1)
        if len(parts) == 2:
            return parts[0], parts[1]
        else:
            return "", parts[0]

    def print_artists(self):
        """Simple printout for the database."""
        result = ""
        for artist in self.artists:
            result += artist.name + '\n'
            #print(artist.name)
            for album in artist.albums:
                result += "    " + album.year + "  " + album.name + '\n'
                #print("    " + album.year + "  " + album.name)
        return result

    def handler_run(self):
        pass

    def get_artists(self):
        ret = ""
        for artist in self.artists:
            ret += artist.name
            for album in artist.albums:
                ret += "    " + album.year + "  " + album.name
                ret += "\n"

        return ret

if __name__ == "__main__":
    print("Welcome to MAIDS !")

    arg = Argumentor()

    box = Matchbox()
    maid = Maiden(arg.path, box)

    if arg.args.list:
        print(maid.mon.list_to_text(maid.list))
    elif arg.args.json:
        print(json.dumps(maid.artists, separators=(',', ':'), sort_keys=True, indent=2, cls=ArtistEncoder))
    elif arg.args.artists:
        print(maid.print_artists())
    #print(maid.artists)
    #m.handler_run()
    #print(maid.print_artists())
    #print(maid.list)

    #j = json.dumps(maid.artists, separators=(',', ':'), sort_keys=True, indent=2, cls=ArtistEncoder)
    #print(j)
    #print(json.loads(j) == maid.artists)