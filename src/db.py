import psycopg2

def connect(user_, password_):
    global conn
    conn = psycopg2.connect(dbname='Users', user=user_, 
                        password=password_, host='localhost')
    conn.autocommit = True
    global cursor
    cursor = conn.cursor()

def update_paper_type(user_id, paper_type):
    cursor.execute('SELECT * FROM public."paperTypes" where "id"={}'.format(user_id))
    record = cursor.fetchone()
    if record == None:
        cursor.execute("insert into public.\"paperTypes\" values ({}, '{{{}}}', null)".format(user_id, paper_type))
    else:
        cursor.execute("update public.\"paperTypes\" set \"paperType\" = '{{{}}}' where id = {}".format(paper_type, user_id))

def get_paper_type(user_id):
    cursor.execute('SELECT * FROM public."paperTypes" where "id"={}'.format(user_id))
    record = cursor.fetchone()
    return record[1][0]

def add_paper(paper_properties, user_id):
    cursor.execute('SELECT * FROM public."stars" where "id_user"={} and \'{}\'=ANY("symbol")'.format(user_id, paper_properties[0]))
    record = cursor.fetchone()
    if record == None:
        cursor.execute("insert into public.\"stars\" values (default, {}, '{{{}}}', '{{{}}}', '{{{}}}')"\
            .format(user_id, paper_properties[0], paper_properties[1], paper_properties[2]))

def get_papers(user_id):
    cursor.execute('SELECT * FROM public."stars" where "id_user"={}'.format(user_id))
    records = cursor.fetchall()
    result = []
    for x in records:
        s = []
        s.append(x[2][0])
        s.append(x[3][0])
        s.append(x[4][0])
        result.append(s)
    return result

def update_active_paper(user_id, paper):
    cursor.execute('SELECT * FROM public."paperTypes" where "id"={}'.format(user_id))
    record = cursor.fetchone()
    if record == None:
        cursor.execute("insert into public.\"paperTypes\" values ({}, null, '{{{}}}')".format(user_id, paper))
    else:
        cursor.execute("update public.\"paperTypes\" set \"activePaper\" = '{{{}}}' where id = {}".format(paper, user_id))

def delete_paper(user_id):
    cursor.execute('SELECT * FROM public."paperTypes" where "id"={}'.format(user_id))
    record = cursor.fetchone()
    paper = record[2][0]
    cursor.execute('Delete FROM public."stars" where "id_user"={} and \'{}\'=ANY("symbol")'.format(user_id, paper))

def get_active_paper(user_id):
    cursor.execute('SELECT * FROM public."paperTypes" where "id"={}'.format(user_id))
    record = cursor.fetchone()
    paper = record[2][0]
    return paper

def get_tickers(user_id):
    cursor.execute('SELECT * FROM public."stars" where "id_user"={}'.format(user_id))
    records = cursor.fetchall()
    result = []
    for x in records:
        result.append(x[2][0])
    return result