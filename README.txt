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