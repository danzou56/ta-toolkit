#!/usr/bin/env python3

import os
import sys
import random
import math
import hashlib
import shutil
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

	student_dir = sorted(f.name for f in os.scandir(raw_path) if f.is_dir())
	total_students = len(student_dir)
	print('Students: {}'.format(total_students))

	print('TA assignments:')
	rem = total_students % len(ta_list)
	ta_assignment = list(
		math.floor(total_students * ta.percentage) + (1 if i < rem else 0) for i, ta in enumerate(ta_list)
	)
	for (ta, num) in zip(ta_list, ta_assignment):
		print('  · {}: {} students'.format(ta.name, num))

	shutil.rmtree(new_path, ignore_errors=True)
	os.makedirs(new_path, exist_ok=True)

	index = 0
	for ta, num in zip(ta_list, ta_assignment):
		os.makedirs(os.path.join(new_path, ta.name), exist_ok=True)
		ta.setStudents(student_dir[index:index + num])
		index += num
		for student in ta.students:
			move_assignment(student, ta, config['files'])


if __name__ == '__main__':
	from argparse import ArgumentParser, RawTextHelpFormatter

	parser = ArgumentParser(
		description='Distribute grading of student project submissions among TAs. \n\n'
					'After running the script, a new folder called dist '
					'will be created as a subdirectory of assignment_dir '
					'containing TA names. Each TA folder will have their '
					'assigned students. \n\n'
					'example usage:\n'
					'python3 split.py P6\n'
					'./split.py P6',
		formatter_class=RawTextHelpFormatter
	)
	parser.add_argument(
		'assignment_dir',
		help='Directory where student submissions are located.\n'
			 'Directory structure should be as follows: \n'
			 'assignment_dir/\n'
			 '├── raw/\n'
			 '│   ├── student1/\n'
			 '│   ├── student2/\n'
			 '│   └── ...\n'
			 '└── config.py'
	)

	args = parser.parse_args()

	distribute(args.assignment_dir)