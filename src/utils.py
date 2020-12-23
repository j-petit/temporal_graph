import matplotlib.pyplot as plt
import matplotlib.dates
import sqlite3

from datetime import datetime


def plot_occurances(occurances):

    plt.plot_date(x=[occ[1] for occ in occurances], y=[occ[1] for occ in occurances], ydate=False)
    plt.show()


class NeighborFinder:
    """Creates the temporal neighborhood"""

    def __init__(self, database, neighbor_limit, seed=None, uniform=False):
        """
        """
        self.database = f"file:{database}?mode=ro&cache=shared"
        self.neighbor_limit = neighbor_limit
        self.seed = seed
        self.uniform = uniform

    def get_temporal_neighbor(self, source_nodes, timestamps):

        for entity, time in zip(source_nodes, timestamps):
            try:
                conn = sqlite3.connect(self.database, uri=True)
                cursor = conn.cursor()
                cursor.execute(
                    f"""SELECT IIF(data.entity_1 == "{entity}, data.entity_2, data.entity_1)
                                   FROM data
                                   WHERE data.unix_time <= {time} AND
                                   (data.entity_1 == "{entity}" OR data.entity_2 == "{entity}")
                                   ORDER BY unix_time DESC
                                   LIMIT {self.neighbor_limit}"""
                )

                neighbor = cursor.fetchone()
                occurances = list(cursor.fetchall())
                occurances = [occ[0] for occ in occurances]

            except sqlite3.Error as exception:
                print(exception)
            finally:
                if conn:
                    conn.close()

        return (sample[0], sample[1], occ_1, sample[2], occ_2)
