import json, os
from redis_cache import Cache  # Assume your Redis Cache class is imported from here

def retrieve_and_save_redis_data(filename="redis_data.json"):
    """
    Retrieves all key-value pairs from Redis Cache and saves them to a specified file within the directory structure.
    
    :param filename: The name of the file where data will be saved.
    """
    cache_instance = Cache()  # Assuming Cache is a singleton as per your decorator
    
    # Dynamically construct the file path
    base_dir = os.getcwd()  # Get the current working directory
    target_dir = os.path.join(base_dir, "src", "metadata_strings")  # Append the desired subdirectories
    os.makedirs(target_dir, exist_ok=True)  # Ensure the target directory exists
    file_path = os.path.join(target_dir, filename)  # Construct the full file path
    
    # Assuming a method to iterate over keys, adjust as necessary
    keys = cache_instance.scan_iter("*")  # Method to retrieve all keys, modify based on your implementation
    
    data = {}
    for key in keys:
        value = cache_instance.get(key)
        data[key] = value
    
    # Save to file
    with open(file_path, "w") as file:
        json.dump(data, file)
    
    print(f"Data successfully saved to {file_path}")

