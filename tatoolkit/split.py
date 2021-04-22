#!/usr/bin/env python3

import csv
import hashlib
import math
import os
import random
import re
import shutil
from argparse import ArgumentParser, RawTextHelpFormatter
from distutils.dir_util import copy_tree

from tatoolkit.ta import TeachingAssistant, normalize_ta_list

parser = ArgumentParser(
	description='Distribute grading of student project submissions among TAs. \n\n'
				'After running the script, a new folder called dist '
				'will be created as a subdirectory of assignment_dir '
				'containing TA names. Each TA folder will have their '
				'assigned students. \n'
				'\n'
				'example usage:\n'
				'python3 split.py P6 --files Utilities.java\n'
				'./split.py P6 -fi Utilities.java',
	formatter_class=RawTextHelpFormatter
)
parser.add_argument(
	'assignment_dir',
	help='Directory where student submissions are located.\n'
		 'Directory structure should be as follows: \n'
		 'assignment_dir/\n'
		 '└── raw/\n'
		 '    ├── student1/\n'
		 '    ├── student2/\n'
		 '    └── ...\n'
		 '\n'
		 'If using legacy mode, the structure should be as follows: \n'
		 'assignment_dir/\n'
		 '├── raw/\n'
		 '│   ├── student1/\n'
		 '│   ├── student2/\n'
		 '│   └── ...\n'
		 '└── config.py'
)
parser.add_argument(
	'--files', '-fi', metavar='N', nargs='+', default=[],
	help='Include these files'
)
parser.add_argument(
	'--folders', '-fo', metavar='N', nargs='+', default=[],
	help='Include these folders'
)
parser.add_argument(
	'--folder-with', '-fw', metavar='N', nargs='+', default=[],
	help='Include the folders in which the following files are found'
)
parser.add_argument(
	'--extensions', '-ei', metavar='N', nargs='+', default=[],
	help='Include only these extensions. Ignored by --files. It is possible to '
		 'exclude the file specified in --folder-with if the file\'s extension '
		 'is not included.'
)
parser.add_argument(
	'--csv', '-c', metavar='CSV', default='tas.csv',
	help='Specify TA weighting via a CSV file. The file should have no headers, '
		 'and the columns should be the TA name, followed by their assigned '
		 'weight (weights do not have to add up to 100; they will be '
		 'normalized).'
)
parser.add_argument(
	'--legacy', '-l', default=False, action='store_true',
	help="Use legacy verison. Because the legacy version gets its configuration "
		 "from the config.py file, supplying --legacy will cause any other flags "
		 "to be ignored.",
)

args = parser.parse_args()


def get_ta_list():
	with open(args.csv, 'r') as f:
		rdr = csv.reader(f)
		ta_list = [TeachingAssistant(row[0], int(row[1])) for row in rdr]
		return normalize_ta_list(ta_list)


def distribute(ta_list):
	# The random generator should be consistent when running the code
	#  for the same assigment. In this way, modifications can be done without
	#  affecting the students assigned to each TA. To achieve this, the seed
	#  for the random library is set using the hash of the assignment name.
	random.seed(int(hashlib.sha1(args.assignment_dir.encode("utf-8")).hexdigest(), 16))
	random.shuffle(ta_list)

	# +====================+
	# | Assignment handler |
	# +====================+

	raw_path = os.path.join(args.assignment_dir, 'raw')
	new_path = os.path.join(args.assignment_dir, 'dist')

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
					if not set(args.extensions).isdisjoint({os.path.splitext(f)[1] for f in files}):
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
	assert sum(ta_assignment) == total_students, "Number of students to grade didn't match ta assignment!"

	shutil.rmtree(new_path, ignore_errors=True)
	os.makedirs(new_path, exist_ok=True)

	instructions = []
	instructions.extend([('file', s) for s in args.files])
	instructions.extend([('folder', s) for s in args.folders])
	instructions.extend([('folder_with', s) for s in args.folder_with])

	index = 0
	for ta, num in zip(ta_list, ta_assignment):
		os.makedirs(os.path.join(new_path, ta.name), exist_ok=True)
		ta.setStudents(student_dir[index:index + num])
		index += num
		for student in ta.students:
			move_assignment(student, ta, instructions)

	# Create file with which TAs have which students
	with open(os.path.join(args.assignment_dir, 'dist.txt'), 'w') as f:
		for ta in ta_list:
			f.write(f"====== {ta.name} ======\n")
			f.write(', '.join([re.split(r'[\-_]', student, 1)[0] for student in ta.students]))
			f.write("\n")


def main():
	if args.legacy:
		from tatoolkit import split_leg
		split_leg.distribute(args.assignment_dir)
		return

	if not (args.files or args.folders or args.folder_with):
		print("No files or folders specified; nothing will happen!")
		print("Aborting now!")
		return

	ta_list = get_ta_list()
	distribute(ta_list)


if __name__ == '__main__':
	main()

