import requests
import json
import server
from eeg_data.eeg_utils import simulate_eeg

nbest = 3
# localhost = 'http://localhost:5000' # choose a port
path2eeg = 'eeg_data/EEGEvidence.txt-high'
simulator = simulate_eeg(path2eeg)

# init
r = requests.post(localhost + '/init', json={'nbest': nbest})
print r.status_code

# provide priors for a single likelihood evidence
# provide words for the same evidence
history = 'th'
# build evidence history
evidence = []
for target in history:
    evidence.extend(simulator.simulate(target))
print evidence
print "Charachter and Word distributions"
r = requests.post(localhost + '/state_update', json={'evidence': evidence, 'return_mode': 'word'})
print r.status_code
e = r.json()

# print priors for a history of evidence
print e['letter']
print e['word']

# reset
r = requests.post(localhost + '/reset')
print r.status_code

# feed new evidence and ask just for letter distribution
print "Character distribution"
target = 'y'
evidence = simulator.simulate(target)
r = requests.post(localhost + '/state_update', json={'evidence': evidence, 'return_mode': 'letter'})
print r.status_code
e = r.json()
print "status code of 200 implies a good connection"
