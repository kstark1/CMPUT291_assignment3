import sqlite3
import random
import time
import matplotlib.pyplot as plt

connection = None
cursor = None

def connect(path):
    # using global variables already defined in main method, not new variables
    global connection, cursor
    # create a connection to the sqlite3 database
    connection = sqlite3.connect(path)
    # create a cursor object which will be used to execute sql statements
    cursor = connection.cursor()
    # execute a sql statement to enforce foreign key constraint
    cursor.execute(' PRAGMA foreign_keys=ON; ')
    # commit the changes we have made so they are visible by any other connections
    connection.commit() 
    return

def query(code):
    global connection, cursor
    
    connection.commit()
    
    query = ''' SELECT COUNT(*), AVG(OS.size)
                FROM Orders O, Customers C, ( SELECT order_id as oid, COUNT(DISTINCT order_item_id) as size FROM Order_items O GROUP BY O.order_id )as OS
                WHERE O.customer_id = C.customer_id
                AND C.customer_postal_code=:code
                AND OS.oid=O.order_id
            '''
    #found this method from https://stackoverflow.com/questions/7370801/how-to-measure-elapsed-time-in-python
    t = time.process_time()
    cursor.execute(query,{"code":code})
    elapsed_time = time.process_time() - t
    #Commit the query to the DB
    connection.commit()
    
 
    
    return elapsed_time

def uninformed(code):
    global connection, cursor
    cursor.execute(' PRAGMA automatic_index=FALSE; ')
    ordersnew = '''
    CREATE TABLE "OrdersNew" ("order_id"	TEXT,"customer_id" TEXT);
    INSERT INTO OrdersNew
    SELECT order_id, customer_id
    FROM Orders;
    ALTER TABLE Orders RENAME TO OrdersOriginal;
    ALTER TABLE OrdersNew RENAME TO Orders;
    '''
    cursor.executescript(ordersnew)
    
     
    Customersnew = '''
    CREATE TABLE "CustomersNew" ("customer_id" TEXT, "customer_postal_code" INTEGER);
    INSERT INTO CustomersNew 
    SELECT customer_id, customer_postal_code 
    FROM Customers;
    ALTER TABLE Customers RENAME TO CustomersOriginal;
    ALTER TABLE CustomersNew RENAME TO Customers;
    ''' 
    cursor.executescript(Customersnew)
    connection.commit()
    
    time_=query(code)
    
    cursor.execute('''DROP TABLE Customers;''')
    cursor.execute('''ALTER TABLE CustomersOriginal RENAME TO Customers;''')
    cursor.execute(''' DROP TABLE Orders;''')
    cursor.execute('''ALTER TABLE OrdersOriginal RENAME TO Orders;''')
    connection.commit()
    
    return time_*1000

def self_optimized(code):
    global connection, cursor
    cursor.execute(' PRAGMA automatic_index = TRUE; ')
    connection.commit()
    time_=query(code)
    return time_*1000


def user_optimized(code):
    global connection, cursor
    cursor.execute(' PRAGMA automatic_index = FALSE; ')
   
    index_ = ''' CREATE INDEX customer_index ON Customers (customer_postal_code, customer_id);
                 CREATE INDEX order_index ON Orders (customer_id, order_id);'''
    cursor.executescript(index_)
    connection.commit()
    time_=query(code)
    cursor.execute('''DROP INDEX customer_index''')
    cursor.execute('''DROP INDEX order_index''')
    connection.commit()
    return time_*1000
    
    
    
    
def main():
    global connection, cursor

    paths=['./A3small.db', './A3Medium.db', './A3Large.db']
   
    uninformedtime=[]
    self_optimizedtime=[]
    user_optimizedtime=[]     
    
    
    for p in paths:
        times=[]
        connect(p)
        #get a list of all postal codes
        codes=[]
        query='''SELECT C.customer_postal_code
                 FROM Customers C
        '''
        cursor.execute(query)
        rows=cursor.fetchall()
        for each in rows:
            codes.append(str(each[0]))
        #print(codes)
        
        for i in range(50): #uninformed scenario
            times.append(uninformed(random.choice(codes)))
            #get average time from times array
            #https://www.geeksforgeeks.org/find-average-list-python/
        avg_time=sum(times)/len(times)
        uninformedtime.append(avg_time)
        
        connection.close()
        connect(p)
        
        times=[]
        for i in range(50): #selfoptimized scenario
            #use random function to pick random postal code
            times.append(self_optimized(random.choice(codes)))
            
        avg_time=sum(times)/len(times)
        self_optimizedtime.append(avg_time)
        
        connection.close()
        connect(p)
        
        
        times=[]
        for i in range(50):
            times.append(user_optimized(random.choice(codes)))
        
        avg_time=sum(times)/len(times)
        user_optimizedtime.append(avg_time)
            
        connection.close()
    
   # print('uninformed',uninformedtime)
   # print('self-optimize',self_optimizedtime)
   # print('user-optimize',user_optimizedtime)
    
    
    bar_chart(uninformedtime, self_optimizedtime, user_optimizedtime)
    
def bar_chart(uninformedtime,self_optimizedtime,user_optimizedtime):
    width = 0.35
    #making stacked bar charts using resource provided on assignment page
    labels = ['SmallDB', 'MediumDB', 'LargeDB']
    uninformed_results=[]
    uninformed_results=uninformedtime
    self_optimized_results=[]
    self_optimized_results=self_optimizedtime
    user_optimized_results=[]
    user_optimized_results=user_optimizedtime
    last_sum=[]
    for i in range(3):
        last_sum.append(uninformed_results[i] + self_optimized_results[i])
        
    
    
    
    
    fig, ax = plt.subplots()
    
    ax.bar(labels, uninformed_results, width,  label='Uninformed')
    ax.bar(labels, self_optimized_results, width, bottom=uninformed_results,
    label='Self-Optimized')
    ax.bar(labels, user_optimized_results, width, bottom=last_sum,
    label='User-Optimized')
    ax.set_title('Query 3 (runtime in ms)')
    ax.legend()
    
    path = './{}chart.png'.format('Q3A3')
    plt.savefig(path)
    print('Chart saved to file {}'.format(path))
    
    
    # close figure so it doesn't display
    plt.close()
    return
    
# run main method when program starts
if __name__ == "__main__":
    main()

