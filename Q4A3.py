import sqlite3
import matplotlib.pyplot as plt
import random
import timeit

#--------------------------------------------------------
#                      RESOURCES
#--------------------------------------------------------
#SQLITE Random function:
#   https://www.sqlitetutorial.net/sqlite-functions/sqlite-random/

#--------------------------------------------------------
#                  ASSIGNMENT FUNCTIONS
#--------------------------------------------------------

#Function which defines the query we are testing
def Query(code):
    #The query to be executed
    query = '''SELECT COUNT(DISTINCT S.seller_postal_code)
            FROM Order_items O, Sellers S
            WHERE S.seller_id = O.seller_id AND O.order_id = :code
            '''

    #Executes the query using the code variable as the input
    cursor.execute(query, {"code": code})

    #Get the list of returned tuples
    rows = cursor.fetchall()

    #Commit the query to the DB
    connection.commit()

    #Return the result of the query
    return rows

#Sets the database into uninformed mode
def Uninformed():
    print("Setting Scenario Uninformed")

    #Set all relevant settings
    cursor.execute(' PRAGMA automatic_indexing=OFF; ')
    
    #Make the new databses
    cursor.execute('''CREATE TABLE IF NOT EXISTS "SellersNew" (
                    seller_id TEXT,
                    seller_postal_code INTEGER);''')

    cursor.execute('''CREATE TABLE "Order_itemsNew" (
                            order_id TEXT,
                            order_item_id INTEGER,
                            product_id TEXT,
                            seller_id TEXT);''')
    
    cursor.execute('''INSERT INTO SellersNew 
                    SELECT seller_id, seller_postal_code
                    FROM Sellers;''')

    cursor.execute('''INSERT INTO Order_itemsNew 
                    SELECT order_id, order_item_id, product_id, seller_id
                    FROM Order_items;''')



    cursor.execute("ALTER TABLE Sellers RENAME TO SellersOId")
    cursor.execute("ALTER TABLE SellersNew RENAME TO Sellers")
    
    cursor.execute("ALTER TABLE Order_items RENAME TO Order_itemsOId")
    cursor.execute("ALTER TABLE Order_itemsNew RENAME TO Order_items")

    #Commit the changes to the DB
    connection.commit()
    
#Sets the databse into self-optimized mode
def SelfOptimized():
    print("Setting Scenario Self-Optimized")

    #Set all relevant changes
    cursor.execute(' PRAGMA automatic_indexing=ON; ')
    #Drop the databases from Uninformed
    cursor.executescript('''DROP TABLE Sellers;
                         ALTER TABLE SellersOId RENAME TO Sellers;
                         DROP TABLE Order_items;
                         ALTER TABLE Order_itemsOId RENAME TO Order_items;''')
    

    #Commit the changes to the DB
    connection.commit()

#Sets the database into user-optimized mode
def UserOptimized():
    print("Setting Scenario User-Optimized")

    #Set all relevant changes
    cursor.execute(' PRAGMA automatic_indexing=ON; ')
    
    #Set the index
    cursor.execute("CREATE INDEX sellersIndex ON Sellers (seller_id);")
    cursor.execute("CREATE INDEX ordersItemsIndex ON Order_items (order_id);")
    

    #Commit the changes to the DB
    connection.commit()

def CleanUserOptimized():
    cursor.execute("DROP INDEX IF EXISTS sellersIndex;")
    cursor.execute("DROP INDEX IF EXISTS ordersItemsIndex;")

#Main function called on startup
def main():
    global connection
    global runCount
    runCount = 50

    #All the databases we want to run on
    paths = ["./A3Small.db", "./A3Medium.db", "./A3Large.db"]

    #All the scenarios we want to run, and lists for tracking the average time per run
    scenarios = {Uninformed: [0, 0, 0], SelfOptimized:[0, 0, 0], UserOptimized: [0, 0, 0]}

    #Loop through each database we want to execute on
    for path_index in range(len(paths)):
        path = paths[path_index]
        print("\n\nUsing Database:", path)

        #Loop through each scenario we want to test
        for scenario in scenarios:
            #Connect to the right db and execute the queries. Done each scenario to minimize caching
            connect(path)

            #Set the scenario
            scenario()

            #Get all 50 random inputs ahead of time so it doesnt effect the timing code
            codes = randomCode()
            
            #Time the 50 runs and store in the corresponding list
            #NOTE: this timing method includes the python overhead, but I decided it was preferable to repeated small float additions which can accumulate inaccuracy. This way, any overhead should be constant between all databases and scenarios.
            print("    Running tests...")
            start = timeit.default_timer()
            for run in range(runCount):
                Query(codes[run])
            elapsed = timeit.default_timer() - start
            scenarios[scenario][path_index] = elapsed
            print("    Tests finished...")
            
            #Drop the indexes made for user optimized
            CleanUserOptimized()

            #Close the connection to this database
            connection.close()

    print("Times: ")
    for scenario in scenarios.keys():
        print("   ", scenario.__name__, scenarios[scenario])

    plot(scenarios[Uninformed], scenarios[SelfOptimized], scenarios[UserOptimized])

#--------------------------------------------------------
#                   HELPER FUNCTIONS
#--------------------------------------------------------

#NOTE: this function is not super fast, but it works, make sure it is not included in the timing code
def randomCode() -> list:
    query = '''SELECT C.customer_postal_code
               FROM Customers C
               ORDER BY RANDOM()
               LIMIT ''' + str(runCount)
    cursor.execute(query)
    rows = cursor.fetchall()

    #extract all the codes form their tuple
    codes = []
    for row in rows:
        codes.append(row[0])

    connection.commit()
    return codes

def plot(uninformed, selfOptimized, userOptimized, width = 0.5):
    labels = ["SmallDB", "MediumDB", "LargeDB"]
    fig, ax = plt.subplots()

    #Construct where the bottom of the user optimized should be
    userBottom = []
    for i in range(len(selfOptimized)):
        userBottom.append(selfOptimized[i] + uninformed[i])

    #Add the bars to the graph
    bar = ax.bar(labels, uninformed, width, label="Uninformed", color = 'blue')
    bar = ax.bar(labels, selfOptimized, width, label="Self-Optimized", bottom = uninformed, color = 'red')
    bar = ax.bar(labels, userOptimized, width, label="User-Optimized", bottom = userBottom, color = 'yellow')

    #add labels and the legend
    ax.set_ylabel("Time (s)")
    ax.set_title("Query 4")
    ax.legend()
    plt.show()

def connect(path):
    global connection, cursor
    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    connection.commit()


if __name__ == "__main__":
    main()