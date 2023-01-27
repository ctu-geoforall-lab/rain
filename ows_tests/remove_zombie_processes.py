import argparse
import sqlite3

def remove_zombie_processes(dbname, days=1):
    with sqlite3.connect(dbname) as con:
        cur = con.cursor()
        try:
            cur.execute(
            "DELETE from pywps_requests where status=2 and time_start > DATE('now','-{0} day')".format(
                days
            ))
            con.commit()
        except sqlite3.OperationalError as e:
            print("remove_zombie_processes: {}".format(e))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('dbname', metavar='dbname', type=str,
                        help='Path to the database')
    parser.add_argument('days', metavar='number_of_days', type=str,
                        help='Remove processes older than specied number of days')
    args = parser.parse_args()

    remove_zombie_processes(args.dbname, args.days)
