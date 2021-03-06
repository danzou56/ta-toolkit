#!/usr/bin/env python3
import csv
import os
import sys
import random
import math
import hashlib
import shutil
import re
from distutils.dir_util import copy_tree

def distribute(assignment_dir):
	from ta import normalize_ta_list, ta_list
	sys.path.insert(0, assignment_dir)
	from config import config

	# Filtering the list
	if 'tas' in config:
		ta_list = [ta for ta in ta_list if not ta.name not in config['tas']]

	ta_list = normalize_ta_list(ta_list)

	# The random generator should be consistent when running the code
	#  for the same assigment. In this way, modifications can be done without
	#  affecting the students assigned to each TA. To achieve this, the seed
	#  for the random library is set using the hash of the assignment name.
	random.seed(int(hashlib.sha1(assignment_dir.encode("utf-8")).hexdigest(), 16))
	random.shuffle(ta_list)

	# +====================+
	# | Assignment handler |
	# +====================+

	raw_path = os.path.join(assignment_dir, 'raw')
	new_path = os.path.join(assignment_dir, 'dist')

	def move_assignment(student_dir, ta, instructions):
		student = student_dir.split('-', 1)[0]
		student_raw_path = os.path.join(raw_path, student_dir)
		student_new_path = os.path.join(new_path, ta.name, student)
		os.makedirs(student_new_path, exist_ok=True)
		for (inst, inst_path) in instructions:
			for root, dirs, files in os.walk(student_raw_path):
				if (inst == 'file' and inst_path in files):
					# COPY ONLY THE FILE
					shutil.copyfile(
						os.path.join(root, inst_path),
						os.path.join(student_new_path, inst_path)
					)
				elif ((inst == 'folder' and inst_path == os.path.basename(root)) or
					  (inst == 'folder_with' and inst_path in files)):
					# COPY THE ENTIRE FOLDER
					if not set(config['extensions']).isdisjoint({os.path.splitext(f)[1] for f in files}):
						copy_tree(root, student_new_path)

	student_dir = sorted(f.name for f in os.scandir(raw_path) if f.is_dir() and not f.name[:8] == 'psadeghi')
	total_students = len(student_dir)
	print('Students: {}'.format(total_students))

	print('TA assignments:')
	ta_assignment = list(
		math.floor(total_students * ta.percentage) for i, ta in enumerate(ta_list)
	)
	rem = total_students - sum(ta_assignment)
	if rem > 0:
		ta_assignment = list(p + (1 if i < rem else 0) for i, p in enumerate(ta_assignment))
	for (ta, num) in zip(ta_list, ta_assignment):
		print('  · {}: {} students'.format(ta.name, num))
	assert(sum(ta_assignment) == total_students, "Number of students to grade didn't match ta assignment!")

	shutil.rmtree(new_path, ignore_errors=True)
	os.makedirs(new_path, exist_ok=True)

	index = 0
	for ta, num in zip(ta_list, ta_assignment):
		os.makedirs(os.path.join(new_path, ta.name), exist_ok=True)
		ta.setStudents(student_dir[index:index + num])
		index += num
		for student in ta.students:
			move_assignment(student, ta, config['files'])

	# Create file with which TAs have which students
	with open(os.path.join(assignment_dir, 'dist.txt'), 'w') as f:
		# overbuilt but whatever
		csv_writer = csv.writer(f, delimiter=':')
		csv_writer.writerows([
			[
				ta.name,
				','.join([re.split(r'[\-_]', student, 1)[0] for student in ta.students])
			]
			for ta in ta_list
		])
