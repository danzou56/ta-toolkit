import sys

# +============+
# | TA handler |
# +============+

LEAD_p = 7
TEACHING_p = 7
GRADING_p = 12
GREG_p = 10

class TeachingAssistant:

	def __init__(self, name, percentage, sid=None):
		self.name = name
		self.sid = sid
		self.percentage = float(percentage)

	def setStudents(self, list_students):
		self.students = list_students

	def __str__(self):
		return self.name + ': ' + self.percentage.__str__()


ta_list = [

	# Grading TAs
	TeachingAssistant('Ahmed', GRADING_p),
	TeachingAssistant('Chujun', GRADING_p),
	TeachingAssistant('Gregory', GREG_p),
	TeachingAssistant('Hamid', GRADING_p),
	TeachingAssistant('Onur', GRADING_p),
	TeachingAssistant('Mohammad', TEACHING_p),

	# Teaching TAs
	TeachingAssistant('Alexis', TEACHING_p),
	TeachingAssistant('Arjun', TEACHING_p),
	TeachingAssistant('Dhanvee', TEACHING_p),
	TeachingAssistant('Gabriel', TEACHING_p),
	TeachingAssistant('Matthew', TEACHING_p),
	TeachingAssistant('Nikolay', TEACHING_p),

	TeachingAssistant('Dan', LEAD_p),
	TeachingAssistant('Vlad', LEAD_p),
]

# Checking for name duplicates
ta_names = (ta.name for ta in ta_list)
if len(ta_list) != len(set(ta_names)):
	print('No can do my friend...\nThere are TAs with the same name!')
	sys.exit()

# Normalizing the grading load
def normalize_ta_list(ta_list):
	total_grading = sum(ta.percentage for ta in ta_list)
	for ta in ta_list:
		ta.percentage /= total_grading
	return ta_list
