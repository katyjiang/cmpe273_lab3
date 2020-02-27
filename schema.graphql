type Query {
	hello: String
	findStudent(id: Int): Student
	findClass(id: Int): Class
}

type Mutation {
	mutateStudent(name: String): Student
	mutateClass(name: String): Class
	addStudentToClass(stu_id: Int, cour_id: Int): Class
}

type Class {
	id: Int
	name: String
	students: [Student]
}

type Student {
	name: String
	id: Int
}
