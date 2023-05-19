import requests
import json
import sqlite3


def artist_info(artist_name):
    return requests.get(f"http://ws.audioscrobbler.com/2.0/"
                        f"?method=artist.getinfo&artist={artist_name.replace(' ', '+')}"
                        f"&api_key=66257839044cef7e32d32b97b3be2384&format=json")


def export_json(artist_name):
    response_dict = artist_info(artist_name).json()
    json_file = open(f"{artist_name}_Info.json".replace(" ", "_"), 'w')
    json.dump(response_dict, json_file, indent=3)
    json_file.close()


def artist_important_info(artist_name):
    response_dict = artist_info(artist_name).json()
    similar_artists = [i['name'] for i in response_dict['artist']['similar']['artist']]
    tags = [i['name'] for i in response_dict['artist']['tags']['tag']]
    description = response_dict['artist']['bio']['summary'].replace('\n', '')
    return f"Artist: {artist_name}\nSimilar Artists: {', '.join(similar_artists)}\nTags: {', '.join(tags)}" \
           f"\nDescription: {description}"


def create_table(cursor_obj):
    cursor_obj.execute('''
    create table if not exists bands
        ('id' integer primary key,
        'Artist' varchar(50),
        'Similar Artists' varchar(200),
        'Tags' varchar(200),
        'Description' longtext)
    ''')


def sql_insert_artist(artist_name, cursor_obj):
    response_dict = artist_info(artist_name).json()
    similar_artists = [i['name'] for i in response_dict['artist']['similar']['artist']]
    tags = [i['name'] for i in response_dict['artist']['tags']['tag']]
    description = response_dict['artist']['bio']['summary'].replace('\n', '')
    sql_tuple = artist_name, ', '.join(similar_artists), ', '.join(tags), description
    cursor_obj.execute('''
    insert into bands ('Artist', 'Similar Artists', 'Tags', 'Description')
    values (?, ?, ?, ?)
    ''', sql_tuple)


def main():
    connection = sqlite3.connect("Bands.sqlite")
    cursor = connection.cursor()

    while True:
        choice = input("What Do You Wish To Do?\n1) Export Json\n2) Print Text\n3) Add To Database\n4) Check Header "
                       "And Status\nType [Q] To Quit\n").strip()
        artist_title = input("Insert Artist Name:")
        if choice == "1":
            # Exports All Artist Info As A JSON File
            export_json(artist_title)

        elif choice == "2":
            # Prints Artist Info
            print(artist_important_info(artist_title))

        elif choice == "3":
            # Creates Table If It Doesn't Exist
            create_table(cursor)
            # Inserts Important Artist Info Into Database
            sql_insert_artist(artist_title, cursor)
            connection.commit()

        elif choice == "4":
            # Status Code And Header Info
            print(artist_info(artist_title).status_code)
            print(artist_info(artist_title).headers)

        elif choice.lower() == "q":
            break

        else:
            print("Error: Invalid Choice")

    connection.close()


if __name__ == "__main__":
    main()






