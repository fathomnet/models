# takes unmatched species in annotation error log and lists the distinct ones

import os
import ast


# where data is stored relative to this script
DATA_FILES_PREFIX = "../../data/"

# the file that contains all rows that could not be matched to a concept or were not localized
UNMATCHED_LOG_FILENAME = "mate_unmatched_labels.csv"
# the file that contains all rows that could not be matched to a concept or were not localized
CONDENSED_LOG_FILENAME = "mate_unmatched_labels_condensed.txt"

dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, DATA_FILES_PREFIX + UNMATCHED_LOG_FILENAME)
if not os.path.exists(filename):
  raise FileNotFoundError(filename + " does not exist")
unmatched_log_file = open(filename)

filename = os.path.join(dirname, DATA_FILES_PREFIX + CONDENSED_LOG_FILENAME)
if os.path.exists(filename):
  raise FileExistsError(filename + " exists, delete or rename before running")
condensed_log_file = open(filename, 'w')

lines = unmatched_log_file.readlines()
unmatched_set = set()
for line in lines:
  annotation = ast.literal_eval(line)
  if annotation[1] == '':
    # not actually unmatched, just not localized
    continue

  unmatched_set.add(str(annotation[5]))

for x in unmatched_set:
  condensed_log_file.write(str(x) + '\n')


