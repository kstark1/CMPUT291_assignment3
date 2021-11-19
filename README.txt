Group 77
ccids: albakoum, muzammil, kstark, asalm
Besides the lab and class notes, we used the following resources: 
https://docs.python.org/3/library/random.html?highlight=random#module-random for random sampling of csv files

https://www.sqlitetutorial.net/sqlite-functions/sqlite-random/ for the sqlite random function

-- Reasoning for choices made for each query under the "User Optimized" Scenario --

Query #1:

    We executed the following SQL query:

        SELECT COUNT(O.order_id)
        FROM Customers C, Orders O
        WHERE C.customer_postal_code = :code
        AND C.customer_id = O.customer_id

    Because SQLite creates indexes on the primary keys by default, to test the uninformed case we disabled the primary keys, by creating identical tables following the guidance of the forum post. For the user optimized case, we created indexes both on customer_id + customer_postal_code, and customer_id + order_id. These two indexes prevent additional accesses to Customers and Orders tables, respectively. Note that no index creation, or other such code is included in the timing of the queries. Python overhead is included, however, to prevent repeated float addiitons for the timing which could accumulate inaccuracies, particularily in the very fast user optimized case.
    
    
 
Query #2:
We executed the following SQL query:
                
                SELECT COUNT(*), AVG(OS.size)
                FROM Orders O, Customers C, OrderSize OS
                WHERE O.customer_id = C.customer_id
                AND C.customer_postal_code=:code
                AND OS.oid=O.order_id
 code represents the randomly chosen customer_postal_code that is fed into the query, OrderSize is the view that was created. We assumed that SQLite would create indices on the primary keys, namely order_id and customer_id, for Orders and Customers respectively. However, since we are looking for customers belonging to a specific postal code area we opted to create a composite index on customer_id + customer_postal_code, from the Customers table, then we created an index on customer_id and order_id from Orders. the first index will help us find more efficiently the customers who belong to the postal code we are concerned with and the second will speed up the process of finding orders that correspond to those customers.
 
 Query #3:
 We executed the following SQL query:
                   
                 SELECT COUNT(*), AVG(OS.size)
                FROM Orders O, Customers C, ( SELECT order_id as oid, COUNT(DISTINCT order_item_id) as size FROM Order_items O GROUP BY O.order_id )as OS
                WHERE O.customer_id = C.customer_id
                AND C.customer_postal_code=:code
                AND OS.oid=O.order_id
 Since the task was to rewrite the previous query without the use of the view, we used a subquery that perfomed the same task. We assumed that SQLite would create indices on the primary keys, namely order_id and customer_id, for Orders and Customers respectively. However, since we are looking for customers belonging to a specific postal code area we opted to create a composite index on customer_id + customer_postal_code, from the Customers table, then we created an index on customer_id and order_id from Orders. The first index will help us find more efficiently the customers who belong to the postal code we are concerned with and the second will speed up the process of finding orders that correspond to those customers.
 
 Query #4:
 We executed the following SQL query:
            SELECT COUNT(DISTINCT S.seller_postal_code)
            FROM Order_items O, Sellers S
            WHERE S.seller_id = O.seller_id AND O.order_id = :orderID
 
Where orderID is randomly selected.

We assumed that SQLite would create indices on the primary keys, namely "seller_id" and "order_id","order_item_id","product_id","seller_id" for Sellers and Order_items respectively. However those would not help since we are looking for specific order_id so we created a composite index on Sellers "seller_id, seller_postal_code" to prevent additional accesses to Sellers. Simmilarly, we created a composite index on Order_items "order_id, seller_id" to prevent additional accesses to Order_items.
Note that no index creation, or other such code is included in the timing of the queries. Python overhead is included, however, to prevent repeated float addiitons for the timing which could accumulate inaccuracies, particularily in the very fast user optimized case.
