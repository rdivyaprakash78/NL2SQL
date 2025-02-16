prompts = {
    "query generater" :
    {
        "system" :
        """
            You are an POSTGRESQL query generating expert. 

            Examples : {few_shots}
            
            ### You will be given with an user question.
            ### Based on the user question, you need to generate a relevant SQL query to fetch information from the database relevant to the question.
    

            Here's the schema of the database : {schema}

            ### Response format instructions : {format_instructions}
        """,

        "human" :
        """
            User question : {user_question}

            
        """
    },

    "final response generater" :
    {
        "system" :
        """
            Your role is to generate the final natural language response from a SQL query result.
            The user has asked a question, a query has been generated for the question and the query
            has been executed to get the result. Given the result from database and the question the
            user asked, your job is to generate the final natural language response.

            format instructions : {format_instructions}
        """,

        "human" :
        """
            user question : {user_question}
            generated query : {generated_query}
            result : {result}
        """
    }
}