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
		 'and the columns should be the TA name, followed by their SID, and '
		 'finally their assigned weight (weights do not have to add up to 100; '
		 'they will be normalized). Supplied SIDs will be excluded from the '
		 'distribution. Extra columns are ignored (maybe use them for '
		 'comments? 🙂).'
)
parser.add_argument(
	'--exclude-sids', '-es', metavar='N', nargs='+', default=[],
	help='Any additional SIDs to exclude from the distribution.'
)
parser.add_argument(
	'--legacy', '-l', default=False, action='store_true',
	help="Use legacy verison. Because the legacy version gets its configuration "
		 "from the config.py file, supplying --legacy will cause any other flags "
		 "to be ignored.",
)

args = parser.parse_args()


def get_student_from_submission(submission_str):
	# include negative lookahead to prevent splitting psadeghi-student
	# Damn non-standard SIDs >:(
	return re.split(r'[\-](?!student)', submission_str, 1)[0]


def get_ta_list():
	with open(args.csv, 'r') as f:
		rdr = csv.reader(f)
		ta_list = [TeachingAssistant(row[0], int(row[2]), sid=row[1]) for row in rdr]
		args.exclude_sids.extend(ta.sid for ta in ta_list)
		return normalize_ta_list([ta for ta in ta_list if ta.percentage > 0])


def move_submission(student_dir, ta, instructions, raw_path, new_path):
	student = get_student_from_submission(student_dir)
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


def assign_ta_load(ta_list, students):
	print('Students: {}'.format(students))
	print('TA assignments:')
	ta_assignment = list(
		math.floor(students * ta.percentage) for i, ta in enumerate(ta_list)
	)
	rem = students - sum(ta_assignment)
	if rem > 0:
		ta_assignment = list(p + (1 if i < rem else 0) for i, p in enumerate(ta_assignment))
	for (ta, num) in zip(ta_list, ta_assignment):
		print('  · {}: {} students'.format(ta.name, num))
	assert sum(ta_assignment) == students, "Number of students to grade didn't match ta assignment!"
	return ta_assignment


def write_dist(ta_list):
	# Create file with which TAs have which students
	with open(os.path.join(args.assignment_dir, 'dist.txt'), 'w') as f:
		for ta in ta_list:
			f.write(f"====== {ta.name} ======\n")
			f.write(', '.join([get_student_from_submission(student) for student in ta.students]))
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

	# The random generator should be consistent when running the code
	#  for the same assigment. In this way, modifications can be done without
	#  affecting the students assigned to each TA. To achieve this, the seed
	#  for the random library is set using the hash of the assignment name.
	ta_list = sorted(get_ta_list(), key=lambda t: t.name)
	random.seed(int(hashlib.sha1(args.assignment_dir.encode("utf-8")).hexdigest(), 16))
	random.shuffle(ta_list)

	# +====================+
	# | Assignment handler |
	# +====================+

	raw_path = os.path.join(args.assignment_dir, 'raw')

	# Get students
	student_list = sorted(f.name for f in os.scandir(raw_path) if f.is_dir())
	student_list = [s for s in student_list if get_student_from_submission(s) not in args.exclude_sids]
	ta_assignment = assign_ta_load(ta_list, len(student_list))

	# Build instructions from args
	instructions = []
	instructions.extend([('file', s) for s in args.files])
	instructions.extend([('folder', s) for s in args.folders])
	instructions.extend([('folder_with', s) for s in args.folder_with])

	# Delete contents of assignment_dir/dist so nothing funky happens
	new_path = os.path.join(args.assignment_dir, 'dist')
	shutil.rmtree(new_path, ignore_errors=True)
	os.makedirs(new_path, exist_ok=True)

	# Actually distribute student files to TAs
	index = 0
	for ta, num in zip(ta_list, ta_assignment):
		os.makedirs(os.path.join(new_path, ta.name), exist_ok=True)
		ta.setStudents(student_list[index:index + num])
		index += num
		for student in ta.students:
			move_submission(student, ta, instructions, raw_path, new_path)

	write_dist(ta_list)


if __name__ == '__main__':
	main()

