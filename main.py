
import game
import argparse
import sys


def main(args = sys.argv[1:]):
    parser = argparse.ArgumentParser(description="The connecticut game")
    parser.add_argument("--ClearDB", action="store_true", required=False, help="clears all data from the database")
    parser.add_argument("--ClearTable", type=str, required=False, default=None, help="clears all data from a specific table")

    args = parser.parse_args(args)

    if args.ClearDB:
        game.open_connection(game.db, drop=True)
    elif args.ClearTable is not None:
        for i in game.database.BaseModel.__subclasses__():
            if i.__name__ == args.ClearTable:
                i.delete()
                break
        else:
            print("table not found")
            exit()
    else:
        game.init(game.db)


        #start the ui server
        api = game.Server().run_in_thread()

if __name__ == "__main__":
    main()



