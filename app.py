from ariadne import gql, QueryType, ObjectType, MutationType, graphql_sync, make_executable_schema, load_schema_from_path
from ariadne.constants import PLAYGROUND_HTML
from flask import Flask, request, jsonify

#################################################
# Following DB acting as in-memory database
#################################################
DB = {
	"students":[],
	"classes":[]
}
student_id = 0
class_id = 0


#################################################
# Create GraphQL objects
#################################################
type_defs = gql(load_schema_from_path("schema.graphql"))
query = QueryType()
mutation = MutationType()


#################################################
# Define Resolver for Query type
#################################################
@query.field("hello")
def resolve_hello(_, info):
	request = info.context
	user_agent = request.headers.get("User-Agent", "Guest")
	return "Hello, %s!" % user_agent

# Retrieving an existing student
@query.field("findStudent")
def find_student(_, info, id=None):
	global DB, student_id, class_id
	for stu in DB["students"]:
		if id == stu["id"]:
			return stu
	return f"This student is not existed."

#retrieving an existing class	
@query.field("findClass")
def find_class(_, info, id=None):
	global DB, student_id, class_id
	for cls in DB["classes"]:
		if id == cls["id"]:
			return cls
	return f"This class is not existed."


#################################################
# Define Resolver for Mutation type
#################################################
# Mutate a new student
@mutation.field("mutateStudent")
def add_student(_, info, name=None):
	global DB, student_id, class_id
	for stu in DB["students"]:
		if name == stu["name"]:   #check if student existed
			return stu
	stu = {
		"name": name,
		"id": student_id
	}
	DB["students"].append(stu)
	student_id = student_id + 1
	return stu

# Mutate a new class    
@mutation.field("mutateClass")
def add_class(_, info, name=None):
	global DB, student_id, class_id
	for cls in DB["classes"]:
		if name == cls["name"]:   #check if class existed
			return cls
	cls = {
		"id": class_id,
		"name": name, 
		"students":[]
	}
	DB["classes"].append(cls)
	class_id = class_id + 1
	return cls

@mutation.field("addStudentToClass")
def add_sc(_, info, stu_id=None, cour_id=None):
	global DB, student_id, class_id
	course_existed = False	
	for cls in DB["classes"]:
		if cour_id == cls["id"]:     #check existed
			course_existed = True
			break 
	if not course_existed:
		return f"This course is not existed."
		
	student_existed = False
	found_student = None
	for stu in DB["students"]:
		if stu_id == stu["id"]:      #check existed
			student_existed = True
			found_student = stu
			break
	if not student_existed:
		return f"This student is not existed."
	
	student_added = False
	for cls in DB["classes"]:
		if cls["id"] == cour_id:
			for stu in cls["students"]:
				if stu["id"] == stu_id:
					student_added = True
					break
			if not student_added:
				cls["students"].append(found_student)
			return cls     

schema = make_executable_schema(type_defs, [query, mutation])

app = Flask(__name__)


@app.route("/graphql", methods=["GET"])
def graphql_playgroud():
    # On GET request serve GraphQL Playground
    # You don't need to provide Playground if you don't want to
    # but keep on mind this will not prohibit clients from
    # exploring your API using desktop GraphQL Playground app.
    return PLAYGROUND_HTML, 200


@app.route("/graphql", methods=["POST"])
def graphql_server():
    # GraphQL queries are always sent as POST
    data = request.get_json()

    # Note: Passing the request to the context is optional.
    # In Flask, the current request is always accessible as flask.request
    success, result = graphql_sync(
        schema,
        data,
        context_value=request,
        debug=app.debug
    )

    status_code = 200 if success else 400
    return jsonify(result), status_code


if __name__ == "__main__":
    app.run(debug=True)
