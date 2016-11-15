#!/usr/bin/env python2.7

"""
Columbia W4111 Intro to databases
Example webserver

To run locally

    python server.py

Go to http://localhost:8111 in your browser


A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response
order ={}
tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# The following uses the postgresql test.db -- you can use this for debugging purposes
# However for the project you will need to connect to your Part 2 database in order to use the
# data
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@<IP_OF_POSTGRE_SQL_SERVER>/postgres
#
# For example, if you had username ewu2493, password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://ewu2493:foobar@<IP_OF_POSTGRE_SQL_SERVER>/postgres"
#
# Swap out the URI below with the URI for the database created in part 2
#DATABASEURI = "sqlite:///test.db"
#104.196.175.120
DATABASEURI = "postgresql://sz2624:46zyq@104.196.175.120/postgres"

#
# This line creates a database engine that knows how to connect to the URI above
#
engine = create_engine(DATABASEURI)


#
# START SQLITE SETUP CODE
#
# after these statements run, you should see a file test.db in your webserver/ directory
# this is a sqlite database that you can query like psql typing in the shell command line:
# 
#     sqlite3 test.db
#
# The following sqlite3 commands may be useful:
# 
#     .tables               -- will list the tables in the database
#     .schema <tablename>   -- print CREATE TABLE statement for table
# 
# The setup code should be deleted once you switch to using the Part 2 postgresql database
#
#engine.execute("""DROP TABLE IF EXISTS test;""")
#engine.execute("""CREATE TABLE IF NOT EXISTS test (
#  id serial,
#  name text
#);""")
#engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")
#
# END SQLITE SETUP CODE
#



@app.before_request
def before_request():
    """
    This function is run at the beginning of every web request 
    (every time you enter an address in the web browser).
    We use it to setup a database connection that can be used throughout the request

    The variable g is globally accessible
    """
    try:
        g.conn = engine.connect()
    except:
        print "uh oh, problem connecting to database"
        import traceback; traceback.print_exc()
        g.conn = None

@app.teardown_request
def teardown_request(exception):
    """
    At the end of the web request, this makes sure to close the database connection.
    If you don't the database could run out of memory!
    """
    try:
        g.conn.close()
    except Exception as e:
        pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to e.g., localhost:8111/foobar/ with POST or GET then you could use
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#

@app.route('/')
def index():
    """
    request is a special object that Flask provides to access web request information:

    request.method:   "GET" or "POST"
    request.form:     if the browser submitted a form, this contains the data in the form
    request.args:     dictionary of URL arguments e.g., {a:1, b:2} for http://localhost?a=1&b=2

    See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
    """

    # DEBUG: this is debugging code to see what request looks like
    print request.args


    #
    # example of a database query
    #
    '''
    cursor = g.conn.execute("SELECT address FROM address")
    addresses = []
    for result in cursor:
        addresses.append(result['address'])  # can also be accessed using result[0]
    cursor.close()
    '''
    #
    # Flask uses Jinja templates, which is an extension to HTML where you can
    # pass data to a template and dynamically generate HTML based on the data
    # (you can think of it as simple PHP)
    # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
    #
    # You can see an example template in templates/index.html
    #
    # context are the variables that are passed to the template.
    # for example, "data" key in the context variable defined below will be 
    # accessible as a variable in index.html:
    #
    #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
    #     <div>{{data}}</div>
    #     
    #     # creates a <div> tag for each element in data
    #     # will print: 
    #     #
    #     #   <div>grace hopper</div>
    #     #   <div>alan turing</div>
    #     #   <div>ada lovelace</div>
    #     #
    #     {% for n in data %}
    #     <div>{{n}}</div>
    #     {% endfor %}
    #
    #context = dict(addresses = addresses)


    #
    # render_template looks in the templates/ folder for files.
    # for example, the below file reads template/index.html
    #
    return render_template("index.html")#, **context)

# This is an example of a different path.  You can see it at
# 
#     localhost:8111/another
#
# notice that the functio name is another() rather than index()
# the functions for each app.route needs to have different names
#
@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    cmd = "select uid from users where email = :email1"
    cuid = g.conn.execute(text(cmd),email1 = email)
    cuids=[]
    for result in cuid:
        cuids.append(result['uid'])
    cuid.close()
    if cuids:
        cmd2 = "select uid from users where email = :email1 and password = :password1"
        uid = g.conn.execute(text(cmd2),email1 = email, password1=password)
        uids=[]
        for result in uid:
            uids.append(result['uid'])
        uid.close()
        if uids:
            uuid=int(uids[0])
            global order
            if 'uid' in order:
                del order['uid']
            order['uid']=uuid
            if 'email' in order:
                del order['email']
            order['email']=email
            
            cursor = g.conn.execute("SELECT name, type, dollar_range FROM restaurants")
            rnames = []
            for result in cursor:
                rest = result[0]+' Type: '+result[1]+' '+'$'*result[2]
                rnames.append(rest)  # can also be accessed using result[0]
                #rtypes.append(result['type'])
                #rdollar_ranges.append(result['dollar_range'])
            cursor.close()
            context = dict(restaurant = rnames)#+rtypes+rdollar_ranges)          
            return render_template("restaurant.html", **context)
        else:
            return render_template("anotherfile.html")
    else:
        return render_template("not_registered.html")
        

@app.route('/another')
def another():
    return render_template("anotherfile.html")


@app.route('/restaurant')
def restaurant():
    cursor = g.conn.execute("SELECT name, type, dollar_range FROM restaurants")
    rnames = []
    rtypes = []
    rdollar_ranges = []
    for result in cursor:
        rest = result[0]+' Type: '+result[1]+' '+'$'*result[2]
        rnames.append(rest)
    cursor.close()
    context = dict(restaurant = rnames)        
    return render_template("restaurant.html", **context)


@app.route('/create_account')
def create_account():
      return render_template("create_account.html")

@app.route('/rate')
def rate():
      return render_template("rate.html")

@app.route('/reserve')
def reserve():
      return render_template("reserve.html")

# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
    address = request.form['address']
    zipcode = request.form['zipcode']
    state = request.form['state']
    email = request.form['email']
    password = request.form['password']
    card_number = request.form['card_number']
    card_type = request.form['card_type']
    name_on_card = request.form['name_on_card']    
    cmd = 'INSERT INTO address (address, zipcode, state) VALUES (:address1, :zipcode1, :state1)';
    cmd2 = "SELECT aid FROM address where address = :address1";
    g.conn.execute(text(cmd), address1 = address, zipcode1=zipcode, state1 = state);
    aid = g.conn.execute(text(cmd2), address1 = address);
    aids=[]
    for result in aid:
        aids.append(result['aid'])
    aid.close()
    aaid=int(aids[0])
    cmd3 = 'INSERT INTO users (uid, email, aid, password) VALUES (:uid1, :email1, :aid1, :password1)';
    g.conn.execute(text(cmd3), uid1 = aaid+210000, email1=email, aid1 = aaid, password1=password);  
    cmd4 = 'INSERT INTO cards (uid, card_number, card_type, name_on_card) VALUES (:uid1, :card_number1, :card_type1, :name_on_card1)';
    g.conn.execute(text(cmd4), uid1 = aaid+210000, card_number1=card_number, card_type1 = card_type, name_on_card1=name_on_card); 
    cursor = g.conn.execute("SELECT name, type, dollar_range FROM restaurants")
    rnames = []
    rtypes = []
    rdollar_ranges = []
    for result in cursor:
        rest = result[0]+' Type: '+result[1]+' '+'$'*result[2]
        rnames.append(rest)
    cursor.close()
    context = dict(restaurant = rnames)        
    return render_template("restaurant.html", **context)

@app.route('/add2', methods=['POST'])
def add2():
    restaurant = request.form['restaurant']
    cmd = 'SELECT rid FROM restaurants where name = :restaurant1';
    rid = g.conn.execute(text(cmd), restaurant1 = restaurant);  
    rids = []
    for result in rid:
        rids.append(result['rid'])
    rid.close()
    rrid=int(rids[0])
    global order
    if 'rid' in order:
        del order['rid']
    order['rid']=rrid
    if 'restaurant' in order:
        del order['restaurant']
    order['restaurant']=restaurant
    cmd2 = 'select delivery_company.name, delivery_company.did, delivery_company.price from (delivery_company inner join hire on (delivery_company.did = hire.did)) where hire.rid = :rid1';
    cmd3 = 'select food.fid, food.name from ((restaurants inner join provide on (restaurants.rid = provide.rid)) inner join food on (food.fid=provide.fid)) where restaurants.rid = :rid1';
    did = g.conn.execute(text(cmd2), rid1 = rrid);
    dids=[]
    dprices=[]
    dnames=[]
    for result in did:
        dids.append(result['did'])
        dprices.append(result['price'])
        dnames.append(result['name'])
    did.close()
    ddid=int(dids[0])
    ddprice=int(dprices[0])
    ddname = dnames[0]
    if 'did' in order:
        del order['did']
    order['did']=ddid
    if 'dprice' in order:
        del order['dprice']
    order['dprice']=ddprice
    if 'dname' in order:
        del order['dname']
    order['dname']=ddname
    fid = g.conn.execute(text(cmd3), rid1 = rrid);
    fids=[]
    fnames=[]
    for result in fid:
        fids.append(result['fid'])
        fnames.append(result['name'])
    fid.close()
    context = dict(fids = fids, fnames = fnames, dids= dids, dprices=dprices)  
    return render_template("food.html", **context)

@app.route('/add3', methods=['POST'])
def add3():
    food = request.form['food']
    quantity = request.form['quantity']
    cmd = 'SELECT fid,price FROM food where name = :food1';
    ofid = g.conn.execute(text(cmd), food1 = food);  
    ofids = []
    prices = []
    for result in ofid:
        ofids.append(result['fid'])
        prices.append(result['price'])
    ofid.close()
    offid=int(ofids[0])
    pprice=float(prices[0])
    context = dict(ofids = ofids, prices = prices) 
    global order
    if 'fid' in order:
        del order['fid']
    order['fid']=offid
    if 'price' in order:
        del order['price']
    order['price']=pprice
    if 'food' in order:
        del order['food']
    order['food']=food
    if 'quantity' in order:
        del order['quantity']
    order['quantity']=int(quantity)
    if 'total_price' in order:
        del order['total_price']
    order['total_price']=order['dprice']+order['price']*order['quantity']
    cmd2 = 'INSERT INTO orders (did, rid, uid, fid, total_price, order_date,order_time) VALUES (:did1, :rid1, :uid1, :fid1, :total_price1, current_date, current_time)';
    g.conn.execute(text(cmd2), did1=order['did'], rid1=order['rid'], uid1=order['uid'], fid1=order['fid'], total_price1=order['total_price']);  
    cmd3 = 'select address, state, zipcode from address join users on address.aid = users.aid where email= :email1'
    address = g.conn.execute(text(cmd3),email1 = order['email'])
    #addresses = []
    for result in address:
        add = result[0]+', '+result[1]+', '+str(result[2])
        #addresses.append(add)
    address.close()
    if 'address' in order:
        del order['address']
    order['address']=add
    return render_template("order.html", order=order)

@app.route('/dorate', methods=['POST'])
def dorate():
    stars = request.form['stars']
    comments = request.form['comments']
    cmd = 'INSERT INTO rate (uid, rid, stars, comments) VALUES (:uid1, :rid1, :stars1, :comments1)';
    g.conn.execute(text(cmd), uid1 = order['uid'], rid1=order['rid'], stars1=stars, comments1=comments); 
    cursor = g.conn.execute("SELECT name, type, dollar_range FROM restaurants")
    rnames = []
    rtypes = []
    rdollar_ranges = []
    for result in cursor:
        rest = result[0]+' Type: '+result[1]+' '+'$'*result[2]
        rnames.append(rest)
    cursor.close()
    context = dict(restaurant = rnames)        
    return render_template("restaurant.html", **context)

@app.route('/doreserve', methods=['POST'])
def doreserve():
    number = request.form['number']
    date = request.form['date']
    time = request.form['time']
    cmd = 'INSERT INTO reserve (uid, rid, number, date, time) VALUES (:uid1, :rid1, :number1, :date1, :time1)';
    g.conn.execute(text(cmd), uid1 = order['uid'], rid1=order['rid'], number1=number, date1=date, time1=time); 
    cursor = g.conn.execute("SELECT name, type, dollar_range FROM restaurants")
    rnames = []
    for result in cursor:
        rest = result[0]+' Type: '+result[1]+' '+'$'*result[2]
        rnames.append(rest)
    cursor.close()
    context = dict(restaurant = rnames)        
    return render_template("restaurant.html", **context)

@app.route('/order_history')
def order_history():
    cmd = 'select restaurants.name, food.name,orders.order_date from (orders join food on food.fid=orders.fid) join restaurants on restaurants.rid=orders.rid where orders.uid=:uid1';
    orders = g.conn.execute(text(cmd), uid1 = order['uid']);
    oorder=[]
    for result in orders:
        tmp = 'Restaurant: '+result[0]+' food: '+result[1]+' order date: '+str(result[2])
        oorder.append(tmp)
    orders.close()
    context = dict(orders = oorder) 
    return render_template("order_history.html", **context)

@app.route('/seerate')
def seerate():
    cmd = 'select stars, comments from rate where rid = :rid1';
    rates = g.conn.execute(text(cmd), rid1 = order['rid']);
    rrates=[]
    for result in rates:
        rate = 'Stars: '+'*'*result[0]+' Comments: '+result[1]
        rrates.append(rate)
    rates.close()
    context = dict(rate = rrates) 
    return render_template("seerate.html", **context)

#@app.route('/login')
#def login():
#    abort(401)
#    this_is_never_executed()

'''
@app.route('/login', methods=['GET', 'POST'])
def login():
  cursor = g.conn.execute("SELECT email,password FROM users")
  emails = []
  passwords = []
  for result in cursor:
    emails.append(result['email'])  # can also be accessed using result[0]
    passwords.append(result['password'])
  cursor.close()
  context = dict(emails = emails, passwords = passwords) 
  error = None
  if request.method == 'POST':
      get_email= request.form['email']
      if get_email in emails:
        cmd = "SELECT password from users where email=\'"+get_email+"\'"
        get_pw = g.conn.execute(text(cmd))
        if request.form['password'] == get_pw:
          session['logged_in'] = True
          flash('You were logged in')  
          return redirect(url_for('restaurant'))
          error = 'Invalid email'
      else:
          error = 'Invalid email or password'
  return render_template('login.html', error=error)



@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            return redirect(url_for('home'))
    return render_template('login.html', error=error)
'''


if __name__ == "__main__":
    import click

    @click.command()
    @click.option('--debug', is_flag=True)
    @click.option('--threaded', is_flag=True)
    @click.argument('HOST', default='0.0.0.0')
    @click.argument('PORT', default=8111, type=int)
    def run(debug, threaded, host, port):
        """
        This function handles command line parameters.
        Run the server using

            python server.py

        Show the help text using

            python server.py --help

        """

        HOST, PORT = host, port
        print "running on %s:%d" % (HOST, PORT)
        app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


    run()
