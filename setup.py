from setuptools import setup
import os

XRAY_SETUP_DIR = os.path.abspath(os.path.dirname(__file__))


def long_description():
    filepath = os.path.join(XRAY_SETUP_DIR, "README.md")
    with open(filepath) as f:
        return f.read()


PKG_INSTALL_REQS = ["pytest>=4.2.0", "requests>=2.21.0", "pytz"]


setup(
    name="pytest-xray",
    author="hongzhen.bi",
    author_email="hzhbee@qq.com",
    version="0.0.13",
    python_requires=">=3.6",
    long_description=long_description(),
    long_description_content_type="text/markdown",
    packages=['pytest_xray'],
    install_requires=PKG_INSTALL_REQS,
    summary="py.test Xray integration plugin, using markers",
    entry_points={"pytest11": ["pytest_xray = pytest_xray.plugin"]},
    classifiers=[
        "Development Status :: 3 - Alpha",
        'Framework :: Pytest',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Operating System :: OS Independent'
    ],
)

