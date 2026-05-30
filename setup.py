from distutils.core import setup
import py2exe
import sys
import glob

# Allow py2exe to bundle the json data files
data_files = [
    ('medpulse/data/scores', glob.glob('medpulse/data/scores/*.json')),
    ('medpulse/data/checklists', glob.glob('medpulse/data/checklists/*.json')),
    ('medpulse/data/drugs', glob.glob('medpulse/data/drugs/*.json')),
    ('medpulse/locales', glob.glob('medpulse/locales/*.json')),
]

sys.argv.append('py2exe')

setup(
    windows=[{
        'script': 'medpulse/app.py',
        'dest_base': 'MedPulse'
    }],
    options={
        'py2exe': {
            'bundle_files': 1, # 1 = bundle everything, including Python interpreter
            'compressed': True,
            'includes': ['medpulse', 'matplotlib', 'PIL'],
            'optimize': 2,
        }
    },
    data_files=data_files,
    zipfile=None,
)
