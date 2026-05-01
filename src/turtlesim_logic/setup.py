from setuptools import setup
import os

package_name = 'turtlesim_logic'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), ['launch/turtlesim_logic.launch.py']),
        (os.path.join('share', package_name, 'config'), ['config/turtlesim_params.yaml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='kotantu',
    maintainer_email='kotantu@todo.todo',
    description='Foxy test logic',
    license='TODO',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'open_loop_drive = turtlesim_logic.open_loop_drive_node:main',
            'closed_loop_drive = turtlesim_logic.closed_loop_drive_node:main'
        ],
    },
)
