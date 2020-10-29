import sqlite3
import datetime


def occurances_entity(start_date, entity, config):

    date_list = [
        start_date + datetime.timedelta(days=x) for x in range(config["c_model"]["predict_horizon"])
    ]

    import pudb

    pudb.set_trace()

    starts = [int(date.timestamp()) for date in date_list]
    ends = [start + 24 * 60 * 60 for start in starts]

    dates = zip(starts, ends)

    occurances = []

    try:
        conn = sqlite3.connect(config["c_data"]["database"])
        cursor = conn.cursor()

        for day in dates:

            cursor.execute(
                f"""SELECT COUNT(*) FROM data WHERE unix_time >= {day[0]} and unix_time < {day[1]} and (entity_1 = "{entity}" or entity_2 = "{entity}")"""
            )

            occurances.append(cursor.fetchone()[0])

    except sqlite3.Error as e:
        print(e)
    finally:
        if conn:
            conn.close()

    return occurances
