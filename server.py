from sqlite3 import Cursor
from flask import Flask,Response, abort, request
from about_me import me
from mock_data import catalog 
import json
from config import db
from bson import ObjectId 
from flask_cors import CORS 

app = Flask('funguycollective')
CORS(app)

@app.route("/", methods=['GET'])
def home():
    return "This is the home page"

#create an about endpoint and show your name
@app.route("/about")
def about():
    return me["first"] + " " + me["last"]

@app.route("/myaddress")
def address():
    return f'{me["address"]["street"]} {me["address"]["number"]}'

###########################
###########################
###########################
# postman -> test endpoints of rest apis


@app.route("/api/catalog", methods=["GET"])
def get_catalog():
    results = []
    cursor = db.products.find({}) # get all data from the collection

    for prod in cursor:
        prod["_id"] = str(prod["_id"])
        results.append(prod)
    
    return json.dumps(results)


#post method to create new products
@app.route("/api/catalog", methods=["POST"])
def save_product():
    try:
        product = request.get_json()
        errors = ""

          #title, 5 chars long
        if not "title" in product or len(product["title"]) < 5:
           errors = "Title is required and should at least 5 chars"

        # must have an image
        if not "image" in product:
           errors += ", Image is required"

        #must have a price, the price should be greater/equal to 1
        if not "price" in product or product["price"] < 1:
           errors += ", Price is required and should be >= 1"

        if errors:
            return abort(400, errors)

        db.products.insert_one(product)
        product["_id"] = str(product["_id"])

        return json.dumps(product)
    
    except Exception as ex:
        return abort(500, F"Unexcepted error: {ex}")


#make an endpoint to send back how many products we have in the catalog
@app.route("/api/catalog/count", methods=["GET"])
def get_count():
    cursor = db.products.find({})
    num_items = 0
    for prod in cursor:
        num_items += 1

    return json.dumps(num_items)#return the value


@app.route("/api/product/<id>", methods=["GET"])
def get_product(id):
    try:
        if not ObjectId.is_valid(id):
            return abort(400, "Invalid id")

        product = db.products.find_one({"_id": ObjectId(id)})

        if not product:
           return abort(404, "Product not found")

        product["_id"] = str(product["_id"])
        return json.dumps(product)

    except:
        return abort(500, "Unexpected error")


    #return abort(404, "id does not match any product")

#################
##############


# @app.route('/api/catalog/total', methods=['GET'])
@app.get("/api/catalog/total")
def get_total():
    cursor = db.products.find({})
    total = 0
    for prod in cursor:
        total += prod["price"]

    return json.dumps(total)

# get products by category
#get /api/products/<category>
@app.get("/api/products/<category>")
def products_by_category(category):
    results = []
    cursor = db.products.find({"category": category})
    for prod in cursor:
        prod["_id"] = str(prod["_id"])
        results.append(prod)

    return json.dumps(results)

# get the list of  categories
#get /api/categories
@app.get("/api/categories")
def get_unique_categories():
    cursor = db.products.find({})
    results = []
    for prod in cursor:
        cat = prod["category"]
        if not 'cat' in results:
            results.append(cat)

    return json.dumps(results)



# get the cheapest product
@app.get("/api/product/cheapest")
def get_cheapest_product():
    cursor = db.products.find({})
    solution = cursor[0]
    for prod in cursor:
        if prod["price"] < solution["price"]:
            solution = prod


    solution["_id"] = str(solution["_id"])
    return json.dumps(solution)


@app.get("/api/exercise1")
def get_exe1():
    nums = [123,123,654,124,8865,532,4768,8476,45762,345,-1,234,0,-12,-456,-123,-865,532,4768]
    solution = {}

    # A: find the lowest number
    solution["a"] = 1


    # B: find how many numbers are lowe than 500
    solution["b"] = 1

    # C: sum all the negatives ( -xxxx )
    solution["c"] = 1


    # D: find the sum of numbers except negatives
    solution["d"] = 1


    return json.dumps(solution)



##############################
###########coupon codes ########
###############################

#get all 
@app.route("/api/coupons", methods=["GET"])
def get_all_coupons():
    cursor = db.coupons.find({})
    results = []
    for cc in cursor:
        cc["_id"] = str(cc["_id"])
        results.append(cc)
    
    return json.dumps(results)

#save coupon code
@app.route("/api/coupons", methods=["POST"])
def save_coupons():
    try:
        coupon = request.get_json()

        #validations
        errors = ""
        if not "code" in coupon or len(coupon["code"]) <5:
            errors += "Coupon should have at least 5 chars, "

        if not "discount" in coupon or coupon["discount"] <1 or coupon["discount"] > 50:
            errors += "Discount is required and should be between 1 and 50, "
    
        if errors:
            return Response(errors, status=400)

        #do not duplicate code
        exist = db.coupons.find_one({"code": coupon["code"]})
        if exist:
            return Response( "A coupon already exist for that code", status=400)

        db.coupons.insert_one(coupon)

        coupon["_id"] = str(coupon["_id"])
        return json.dumps(coupon)
    
    except Exception as ex:
        print(ex)
        return Response("Unexcepted error", status=500)

# get cc by code
@app.route("/api/coupons/<code>", methods=["GET"])
def get_coupon_by_code(code):

    #code, code > 4

    coupon = db.coupons.find_one({"code": code})
    if not coupon:
        return abort(404, "coupon not found")
    
    coupon["_id"] = str(coupon["_id"])
    return json.dumps(coupon)



app.run(debug=True)