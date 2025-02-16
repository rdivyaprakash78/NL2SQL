from get_embed import generate_embeddings
from schema_embed import client
from qdrant_client.models import VectorParams, Distance

few_shots = [
    {
        "question" : "How many orders are made from London?",
        "query" : 
        """
        SELECT COUNT(order_id) 
        FROM orders 
        JOIN customers ON orders.customer_id = customers.customer_id 
        WHERE customers.city = 'London';
        """ 
    },
    {
        "question" : "What is the prize after discount for order id 10250",
        "query" : 
        """
        SELECT SUM(quantity*unit_price * (1 - discount)) AS prize_after_discount FROM order_details WHERE order_id = 10250;
        """ 
    },
    {
        "question" : "List of products and its corresponding supplier where we have less in stocks as compared to the orders we have recieved",
        "query" : 
        """
        SELECT p.product_name, s.company_name 
        FROM products p JOIN suppliers s 
        ON p.supplier_id = s.supplier_id 
        WHERE p.units_in_stock < p.units_on_order;
        """ 
    },
    {
        "question" : "What is the type of the customer who orders Chai a lot?",
        "query" : 
        """
        SELECT T2.contact_title FROM orders AS T1 
        INNER JOIN customers AS T2 ON T1.customer_id = T2.customer_id 
        INNER JOIN order_details AS T3 ON T1.order_id = T3.order_id 
        INNER JOIN products AS T4 ON T3.product_id = T4.product_id 
        WHERE T4.product_name = 'Chai' 
        GROUP BY T2.contact_title 
        ORDER BY SUM(T3.quantity) DESC LIMIT 1
        """ 
    },
    {
        "question" : "Identify the customer who has spent most amount of money overall",
        "query" : 
        """
        SELECT c.company_name, SUM(unit_price * quantity) AS total_spent FROM orders AS o 
        JOIN order_details AS od ON o.order_id = od.order_id 
        JOIN customers AS c ON c.customer_id = o.customer_id
        GROUP BY c.customer_id ORDER BY total_spent DESC LIMIT 1
        """ 
    },
]

few_shots_string = [f"Question: {shot['question']}\nQuery: {shot['query']}" for shot in few_shots]

points = []
for index, example in enumerate(few_shots_string):
    id_ = index
    sample = example
    few_shot_embedding = generate_embeddings(example)

    point = {
            "id": index,  # Unique ID for each point
            "vector": few_shot_embedding,  # Convert embedding to list
            "payload": {
                "index": index ,
                "few_shot" : example
            }
        }
            
    points.append(point)
    print(f"Stored few shot: {index}")

client.recreate_collection(
    collection_name="few_shots",
    vectors_config=VectorParams(size=768, distance=Distance.COSINE)  # Size based on 'all-MiniLM-L6-v2'
)

client.upsert(collection_name="few_shots",points=points)