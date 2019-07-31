
import game
import argparse
import sys


def main(args = sys.argv):
    parser = argparse.ArgumentParser(description="The connecticut game")
    parser.add_argument("--ClearDB", action="store_true", help="clears all data from the database")
    parser.add_argument("--ClearTable", type=String, required=False, default=None, help="clears all data from a specific table")

    args = parser.parse_args(args)

    if args.ClearDB:
        game.open_connection(drop=True)
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

        g = game.Game.create(
            player1=game.Player.create(name="joe"),
            player2=game.Player.create(name="john"),
        )

        g.start()

if __name__ == "__main__":
    main()



