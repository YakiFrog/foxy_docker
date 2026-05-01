from setuptools import setup

package_name = 'turtlesim_logic'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
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
            'rotate_turtle = turtlesim_logic.rotate_turtle_node:main'
        ],
    },
)
