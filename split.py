#!/usr/bin/env python3.2

import os
import sys
import random
import math
import numpy as np
import hashlib
import shutil
from distutils.dir_util import copy_tree




if len(sys.argv) != 2:
	print('Remember to indicate the assignment folder.\nExample: python3 split.py P6')
	sys.exit()

assignment_dir = sys.argv[1]

from ta import *
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



def move_assignment(student_dir, ta, instructions):
	student = student_dir.split('-',1)[0]
	student_raw_path = os.path.join(assignment_dir, 'raw', student_dir)
	student_new_path = os.path.join(assignment_dir, 'dist', ta.name, student)
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


student_dir = sorted(os.listdir(assignment_dir + '/raw'))
try:
    student_dir.remove('.DS_Store')
except:
    pass
total_students = len(student_dir)
print('Students: {}'.format(total_students))

print('TA assignments:')
rem = total_students % len(ta_list)
ta_assignment = list(
	math.floor(total_students * ta.percentage) + (1 if i < rem else 0) for i, ta in enumerate(ta_list)
)
for (ta, num) in zip(ta_list, ta_assignment):
	print('  · {}: {} students'.format(ta.name, num))

assigment_split = [0] + list(np.cumsum(ta_assignment))[:-1]

shutil.rmtree(os.path.join(assignment_dir, 'dist'), ignore_errors=True)
os.makedirs(os.path.join(assignment_dir, 'dist'), exist_ok=True)

for (ta, index, num) in zip(ta_list, assigment_split, ta_assignment):
	os.makedirs(os.path.join(assignment_dir, 'dist', ta.name), exist_ok=True)
	ta.setStudents(student_dir[index : (index + num)])
	for student in ta.students:
		move_assignment(student, ta, config['files'])
