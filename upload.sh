# my_pypi should set up in ~/.pypirc before, like below:

#[distutils]
#index-servers = pypi my_pypi
#
#[pypi]
#repository:
#username:
#password:
#
#[my_nexus]
#repository: your_pypi_repository
#username: name
#password: password

python setup.py bdist sdist
twine upload -r my_pypi dist/*
