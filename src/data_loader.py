import sqlite3
import datetime
from torch.utils.data import Dataset


def occurances_entity(start_date, entity, database, predict_horizon):

    date_format = "%Y-%m-%d"

    start_end_dates = (
        start_date.strftime(date_format),
        (start_date + datetime.timedelta(predict_horizon)).strftime(date_format),
    )

    try:
        conn = sqlite3.connect(database, uri=True)
        cursor = conn.cursor()

        cursor.execute(
            f"""
            SELECT
                IFNULL(ec1.occCount, 0) as occCount
            FROM dates
            LEFT OUTER JOIN
                (SELECT * FROM entity_counts WHERE entity_counts.entity_1 = '{entity}')
            AS ec1 ON dates.my_date == ec1.my_date
            WHERE (dates.my_date > '{start_end_dates[0]}' AND
                   dates.my_date <= '{start_end_dates[1]}')"""
        )

        occurances = list(cursor.fetchall())
        occurances = [occ[0] for occ in occurances]

    except sqlite3.Error as e:
        print(e)
    finally:
        if conn:
            conn.close()

    return occurances


class NewsEntityDataset(Dataset):
    """Face Landmarks dataset."""

    def __init__(self, database, predict_horizon, transform=None):
        """
        Args:
             (string): Path to the csv file with annotations.
            root_dir (string): Directory with all the images.
            transform (callable, optional): Optional transform to be applied
                on a sample.
        """
        self.database = f"file:{database}?mode=ro&cache=shared"
        print(self.database)
        self.predict_horizon = predict_horizon
        self.transform = transform

    def __len__(self):
        try:
            conn = sqlite3.connect(self.database, uri=True)
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(ROWID) from data")
            n = cursor.fetchone()[0]
        except sqlite3.Error as exception:
            print(exception)
        finally:
            if conn:
                conn.close()
        return n

    def __getitem__(self, idx):

        idx = idx + 1

        try:
            conn = sqlite3.connect(self.database, uri=True)
            cursor = conn.cursor()
            cursor.execute(f"""SELECT * FROM data WHERE data.ROWID == {idx}""")
            sample = cursor.fetchone()

            date = datetime.datetime.utcfromtimestamp(sample[0])

            occ_1 = occurances_entity(date, sample[1], self.database, self.predict_horizon)
            occ_2 = occurances_entity(date, sample[2], self.database, self.predict_horizon)

        except sqlite3.Error as exception:
            print(exception)
        finally:
            if conn:
                conn.close()

        if self.transform:
            sample = self.transform(sample)

        return (sample[0], sample[1], occ_1, sample[2], occ_2)
