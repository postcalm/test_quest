import psycopg2
import sys

dStart = sys.argv[1]
dEnd = sys.argv[2]

if not dEnd: dEnd = dStart

conn = psycopg2.connect(dbname='test', user='postgres',
                        password='cannotbe', host='localhost', port='5432')
cursor = conn.cursor()

cursor.execute('''
    SELECT recognition.datetime::date, recognition."result", COUNT(recognition."result"), 
        array_agg(recognition."time"), "Project".name, "Server".name
    FROM recognition
    JOIN "Project" ON recognition.id_project = "Project".id
    JOIN "Server" ON recognition.id_server = "Server".id
    WHERE recognition.datetime::date
    BETWEEN %(start)s and %(end)s
    GROUP BY recognition.datetime::date, recognition."result", "Project".name, "Server".name
''', {'start': dStart, 'end': dEnd})

sel = cursor.fetchall()
