import setuptools


with open('README.md', 'r') as fo:
    long_description = fo.read()

setuptools.setup(
    name='mercury',
    version='0.1',
    author='Ivan Nikolaev',
    author_email='voidexp@gmail.com',
    description='A lightweight game development middleware',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='',
    packages=setuptools.find_packages(
        exclude=["*.tests", "*.tests.*", "tests.*", "tests"]
    ),
    install_requires=[
        'Inject>=4.1.1',
        'lxml>=4.5.0',
        'PySDL2==0.9.7',
        'pysdl2-dll==2.0.10',
    ],
    classifiers=[
        'Programming Language :: Python :: 3 :: Only',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Multimedia',
        'Typing :: Typed',
    ],
    python_requires='>=3.7',
)
