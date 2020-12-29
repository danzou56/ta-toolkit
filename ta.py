#!/usr/bin/env python3.2

import sys
import random
import math
import numpy as np
import hashlib




# +============+
# | TA handler |
# +============+

LEAD_p = 1
GRAD_p = 2
UNDERGRAD_p = 1

class TeachingAssistant:

	def __init__(self, name, percentage):
		self.name = name
		self.percentage = float(percentage)

	def setStudents(self, list_students):
		self.students = list_students


ta_list = [

	# Lead TA
	TeachingAssistant('Alejandro', LEAD_p),

	# Graduate TAs
	TeachingAssistant('Ahmed', GRAD_p),
	TeachingAssistant('Nishant', GRAD_p),
	TeachingAssistant('Pedro', GRAD_p),


	# Undegraduate TAs
	TeachingAssistant('Dan', UNDERGRAD_p),
	TeachingAssistant('Vlad', UNDERGRAD_p),
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
