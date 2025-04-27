import datetime
import os
# Configure logging to write to the mounted directory



def log_query_response(filename:str, query: str, response: str, keywords: str = "", search_result: str = ""):
    log_dir = "/workspace/logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = f"log_{timestamp}_{filename}.txt"
    filename=os.path.join(log_dir, log_file)
    
    log_entry = f"""{timestamp} - Query: {query} \n\n 
                    Keywords: {keywords} \n\n 
                    Search Result: {search_result}\n\n 
                    Response: {response} """
    
    with open(filename, "a") as file:
        file.write(log_entry)