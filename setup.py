from setuptools import find_packages, setup

setup(
    name='flaskrrmh',
    version='1.0.4',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "": ["templates/*.html", "templates/**/*.html"],
    },
    zip_safe=False,
    install_requires=[
        'flask',
        'werkzeug'
    ],
)
