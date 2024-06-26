import io
import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

# Avoids IDE errors, but actual version is read from version.py
__version__ = None
with open("rasa/version.py") as f:
    exec(f.read())

# Get the long description from the README file
with open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

tests_requires = [
    "pytest~=3.0",
    "pytest-pycodestyle~=1.3",
    "pytest-cov~=2.0",
    "pytest_localserver~=0.4.0",
    "pytest_sanic~=0.1.0",
    "treq>=17,<23",
    "freezegun~=0.3.0",
    "nbsphinx>=0.3",
    "matplotlib~=2.2",
    "responses~=0.9.0",
    "httpretty~=0.9.0",
    "aioresponses~=0.5.2",
    "mock~=2.0",
]

install_requires = [
    "attrs>=18",
    "jsonpickle~=1.0",
    "redis~=2.0",
    "fakeredis~=0.10.0",
    "pymongo>=3.7,<5.0",
    "numpy~=1.16",
    "scipy~=1.2",
    "typing~=3.0",
    "tensorflow>=1.13,<2.12",
    "apscheduler~=3.0",
    "tqdm~=4.0",
    "networkx~=2.2",
    "fbmessenger~=5.0",
    "pykwalify~=1.7.0",
    "coloredlogs~=10.0",
    "ruamel.yaml~=0.15.0",
    "scikit-learn~=0.20.0",
    "slackclient~=1.0",
    "python-telegram-bot~=11.0",
    "twilio~=6.0",
    "webexteamssdk~=1.0",
    "mattermostwrapper~=2.0",
    "rocketchat_API~=0.6.0",
    "colorhash~=1.0",
    "pika~=0.12.0",
    "jsonschema~=2.6",
    "packaging~=18.0",
    "gevent>=1.4,<24.0",
    "pytz~=2018.9",
    "python-dateutil~=2.7",
    "rasa_nlu~=0.15",
    "rasa_core_sdk~=0.14",
    "colorclass~=2.2",
    "terminaltables~=3.1",
    "sanic>=18.12,<20.13",
    "sanic-cors~=0.9.0",
    "sanic-jwt~=1.2",
    "aiohttp~=3.5",
    "questionary>=1.0.1",
    "python-socketio~=3.0",
    "pydot~=1.4",
    "async_generator~=1.10",
    "sqlalchemy~=1.2",
    "kafka-python~=1.4",
    "sklearn-crfsuite~=0.3.6"
]

extras_requires = {
    "test": tests_requires
}

setup(
    name="rasa",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        # supported python versions
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Software Development :: Libraries",
    ],
    packages=find_packages(exclude=["tests", "tools"]),
    entry_points={
        'console_scripts': ['rasa=rasa.__main__:main'],
    },
    version=__version__,
    install_requires=install_requires,
    tests_require=tests_requires,
    extras_require=extras_requires,
    include_package_data=True,
    description="Machine learning based dialogue engine "
                "for conversational software.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Rasa Technologies GmbH",
    author_email="hi@rasa.com",
    maintainer="Tom Bocklisch",
    maintainer_email="tom@rasa.com",
    license="Apache 2.0",
    keywords="nlp machine-learning machine-learning-library bot bots "
             "botkit rasa conversational-agents conversational-ai chatbot"
             "chatbot-framework bot-framework",
    url="https://rasa.com",
    download_url="https://github.com/RasaHQ/rasa_nlu/archive/{}.tar.gz"
                 "".format(__version__),
    project_urls={
        "Bug Reports": "https://github.com/rasahq/rasa_nlu/issues",
        "Source": "https://github.com/rasahq/rasa_nlu",
    },
)

print("\nWelcome to Rasa!")
print("If any questions please visit documentation "
      "page https://rasa.com/docs")
print("or join the community discussions on https://forum.rasa.com")
