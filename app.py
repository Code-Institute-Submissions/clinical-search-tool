import os
from flask import Flask, render_template, redirect, request, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from os import path
if path.exists("env.py"):
    import env

app = Flask(__name__)

app.config["MONGO_DBNAME"] = "PharmacyLinks"
app.config["MONGO_URI"] = os.getenv("MONGODB_LIST")

mongo = PyMongo(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/results")
def results():
    return render_template("result.html", search_terms=mongo.db.tasks.find())

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/resourcelist")
def resourcelist():
    return render_template("resourcelist.html", resource=mongo.db.resource.find())

@app.route("/addresource")
def addresource():
    return render_template("addresource.html", categories=mongo.db.categories.find())

@app.route("/categorylist")
def categorylist():
    return render_template("categorylist.html",
    categories=mongo.db.categories.find())

@app.route("/edit_category/<category_id>")
def edit_category(category_id):
    return render_template('editcategory.html',
    category = mongo.db.categories.find_one({"_id": ObjectId(category_id)}))

@app.route("/delete_category/<category_id>")
def delete_category(category_id):
    mongo.db.categories.remove({"_id": ObjectId(category_id)})
    return redirect(url_for('categorylist'))

@app.route("/add_category", methods=['POST'])
def add_category():
    category_doc = {'resource_category': request.form.get('resource_category')}
    mongo.db.categories.insert_one(category_doc)
    return redirect(url_for('categorylist'))

@app.route("/update_category/<category_id>", methods=['POST'])
def update_category(category_id):
    mongo.db.categories.update(
        {'_id': ObjectId(category_id)},
        {'resource_category': request.form.get('resource_category')})
    return redirect(url_for('categorylist'))

@app.route("/new_category")
def new_category():
    return render_template('addcategory.html')

@app.route("/insertresource", methods=['POST'])
def insertresource():
    resource = mongo.db.resource
    resource.insert_one(request.form.to_dict())
    return redirect(url_for("resourcelist"))

@app.route("/editresource/<resource_id>")
def editresource(resource_id):
    the_resource = mongo.db.resource.find_one({"_id": ObjectId(resource_id)})
    all_categories = mongo.db.categories.find()
    return render_template('editresource.html', resource=the_resource, categories=all_categories)

@app.route("/updateresource/<resource_id>", methods=["POST"])
def updateresource(resource_id):
    resources = mongo.db.resource
    resources.update( {'_id': ObjectId(resource_id)},
    {
        'resource_category':request.form.get('resource_category'),
        'resource_name':request.form.get('resource_name'),
        'resource_link':request.form.get('resource_link'),
        'resource_description': request.form.get('resource_description'),
        'searchterms': request.form.get('searchterms'),
        'resource_updated': request.form.get('resource_updated')
    })
    return redirect(url_for('resourcelist'))

@app.route("/delete_resource/<resource_id>")
def delete_resource(resource_id):
    mongo.db.resource.remove({'_id': ObjectId(resource_id)})
    return redirect(url_for('resourcelist'))

@app.route('/search', methods = ['GET', 'POST'])
def search():
  search = request.form.get("search")
  resources = list(mongo.db.resource.find({"$text": {"$search": search}}))
  return render_template('resourcelist.html', resources=resources)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)