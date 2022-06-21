
import pymongo
import certifi



con_str = "mongodb+srv://desilvey2:test123@cluster0.aunshtr.mongodb.net/?retryWrites=true&w=majority"


client = pymongo.MongoClient(con_str, tlsCAFile=certifi.where())

db = client.get_database("MushroomStore")