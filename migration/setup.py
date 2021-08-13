from setuptools import setup,find_packages
import os
from collections import OrderedDict

try:
    long_description = ""
    with open('README.md', encoding='utf-8') as f:
        long_description = f.read()

except:
    print('Curr dir:', os.getcwd())
    long_description = open('../README.md').read()

setup(name='OpenResearchMigration',
      version='0.0.27',
      description='python api to access OPENRESEARCH data',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://www.openresearch.org/wiki/Main_Page',
      download_url='https://github.com/SmartDataAnalytics/OpenResearch',
      author='Wolfgang Fahl',
      author_email='wf@bitplan.com',
      license='Apache',
      project_urls=OrderedDict(
        (
            ("Code", "https://github.com/SmartDataAnalytics/OpenResearch"),
            ("Issue tracker", "https://github.com/SmartDataAnalytics/OpenResearch/issues"),
        )
      ),
      classifiers=[
            'Programming Language :: Python',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9'
      ],
      packages=['ormigrate','ormigrate.smw','openresearch',''],
      package_data={'ormigrate': ['resources/*.json']},
      install_requires=[
          'pylodstorage',
          'python-dateutil',
          'py-3rdparty-mediawiki',
          'wikitextparser',
          'geograpy3',
          'ConferenceCorpus'
      ],
      entry_points={
         'console_scripts': [
         'eventcount = ormigrate.eventFixer:mainEventCount',
         'eventfix = ormigrate.eventFixer:mainEventFix',
      ],
    },
      zip_safe=False)
