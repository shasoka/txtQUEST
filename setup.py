# -*- coding: utf-8 -*-

"""
:authors: shasoka, infern397
:license: Apache 2.0 License, LICENSE.md
"""

import TUI
from setuptools import setup

setup(
    name='TEMPLECMD',
    version=TUI.__version__,
    description='Текстовый квест по мотивам книги Г. Лавкрафта "ХРАМ"',
    long_description='Скорее всего вы оказались здесь, посетив наш репозиторий на GitHub. Если нет - подробнее на https://github.com/shasoka/TxtQUEST',
    author='shasoka',
    maintainer='infern397',
    author_email="shenbergarkadii@gmail.com",
    maintainer_email='Semenmochalov@gmail.com',
    url='https://github.com/shasoka/TxtQUEST',
    packages=['MAP', 'TUI', 'MAP.AI'],
    package_dir={'MAP': 'MAP', 'TUI': 'TUI', 'MAP.AI': 'MAP/AI'},
    package_data={'MAP': ['data/*.json'], 'TUI': ['saves/.gitkeep', 'data/*'], 'MAP.AI': ['data/*']},
    entry_points={
        'console_scripts':
            ['temple! = TUI.__main__ :main']
    },
    install_requires = ['py_win_keyboard_layout',
                        'windows-curses',
                        'setuptools',
                        'npyscreen',
                        'numpy',
                        'torch',
                        'asciimatics',
                        'keyboard',
                        'mouse',
                        ],
)
