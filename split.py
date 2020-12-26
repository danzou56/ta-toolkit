#!/usr/bin/env python3.2

import os
import sys
import random
import math
import numpy as np
import hashlib




# -------------

assignment_dir = 'P6'

# We want that the random generator is consistent for the
#  same assigment, so that modifications can be done without
#  affecting the assignment given to each TA. For this, we
#  use the name of the assignment (hashed) to generate the
#  seed for the random library.
random.seed(int(hashlib.sha1(assignment_dir.encode("utf-8")).hexdigest(), 16))


# +============+
# | TA handler |
# +============+

class TA:

	LEAD_p = 1
	GRAD_p = 2
	UNDERGRAD_p = 1

	def __init__(self, name, percentage):
		self.name = name
		self.percentage = float(percentage)

	def setStudents(self, list_students):
		self.students = list_students

ta_list = [

	# Lead TA
	TA('Alejandro', TA.LEAD_p),

	# Graduate TAs
	TA('Vlad1', TA.GRAD_p),
	TA('Vlad2', TA.GRAD_p),
	TA('Vlad3', TA.GRAD_p),

	# Undegraduate TAs
	TA('Dan1', TA.UNDERGRAD_p),
	TA('Dan2', TA.UNDERGRAD_p),
	TA('Dan3', TA.UNDERGRAD_p),
]

# Every split should be random so TAs grade
#  a different set of students every time
random.shuffle(ta_list)

# Normalizing the grading load
total_grading = sum(ta.percentage for ta in ta_list)
for ta in ta_list:
	ta.percentage /= total_grading

# Checking for name duplicates
ta_names = (ta.name for ta in ta_list)
if len(ta_list) != len(set(ta_names)):
	print('No can do my friend...\nThere are TAs with the same name!')
	sys.exit()




# +====================+
# | Assignment handler |
# +====================+

student_dir = sorted(os.listdir(assignment_dir + '/raw'))
#student_list = list(s.split('-',1)[0] for s in student_dir)
total_students = len(student_dir)
print('Students: {}'.format(total_students))

print('TA assignments:')
ta_assignment = list(math.ceil(total_students * ta.percentage) for ta in ta_list)
ta_assignment[-1] -= sum(ta_assignment) - total_students
for (ta, num) in zip(ta_list, ta_assignment):
	print('  · {}: {} students'.format(ta.name, num))

assigment_split = [0] + list(np.cumsum(ta_assignment))[:-1]

def move_assignment(student_dir, ta):
	student = student_dir.split('-',1)[0]
	os.makedirs(os.path.join(assignment_dir, 'dist', ta.name, student), exist_ok=True)
	# Here we need to start copying files

os.makedirs(os.path.join(assignment_dir, 'dist'), exist_ok=True)
for (ta, index, num) in zip(ta_list, assigment_split, ta_assignment):
	os.makedirs(os.path.join(assignment_dir, 'dist', ta.name), exist_ok=True)
	ta.setStudents(student_dir[index : (index + num)])
	for student in ta.students:
		move_assignment(student, ta)
