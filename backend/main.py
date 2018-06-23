from flask import Flask, render_template, jsonify, request
import pymysql
import rds_config
import json

app = Flask(__name__)
app.debug = True

@app.route('/')
def index():
    conn = pymysql.connect(
        host=rds_config.endpoint,
        user=rds_config.username,
        password=rds_config.password,
        port=rds_config.port,
        database=rds_config.database)

    if not conn.open:
        print("connection failed to open")
    else:
        print("connection successful!")

    graphs = []

    with conn.cursor() as cur:
        cur.execute("SELECT gameMode, count(*) FROM pubg.match GROUP BY gameMode;")
        result = cur.fetchall()

        gamemode = [];
        count = [];

        for row in result:
            gamemode.append(row[0])
            count.append(row[1])

        plot1 = dict(
            chart=dict(type='column'),
            title=dict(text="Game Mode Played"),
            xAxis=dict(categories=gamemode),
            yAxis=dict(title=dict(text="Number of Matches Played")),
            series=[dict(name="Game Modes", data=count)]
        )

        graphs.append(plot1)

        cur.execute("SELECT winPlace AS rank, avg(kills) AS average_kills FROM pubg.participant GROUP BY winPlace;")
        result = cur.fetchall()

        rank = [];
        kills = [];

        for row in result:
            rank.append(row[0])
            kills.append(float(row[1]))

        plot2 = dict(
            chart=dict(type='area'),
            title=dict(text="Average Kills For Each Game Rank"),
            xAxis=dict(categories=rank),
            yAxis=dict(title=dict(text="Average Kills")),
            series=[dict(name="Average kills", data=kills)]
        )

        graphs.append(plot2)

        cur.execute("SELECT damageCauserName AS killer, count(id) AS num_kills FROM pubg.logplayerkill WHERE damageCauserName NOT IN ('PlayerMale_A_C','PlayerFemale_A_C') GROUP BY damageCauserName;")
        result = cur.fetchall()

        gunkills = [];

        for row in result:
            gunkills.append(dict(name=row[0], y=row[1]))

        plot3 = dict(
            chart=dict(type='pie'),
            title=dict(text="Total Kills By Cause of Death"),
            series=[dict(name="Weapons", data=gunkills)]
        )

        graphs.append(plot3)

    ids = ['graph-{}'.format(i) for i, _ in enumerate(graphs)]

    conn.close()
    return render_template("index.html", ids=ids, graphs=graphs)


if __name__ == '__main__':
    app.run()
