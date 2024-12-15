import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="jetracerpy",                        
    version="0.1.0",                          
    author="Votre Nom",
    author_email="deepmindtrainer@gmail.com",
    description="Python JetRacer library including support for video streaming and state packets",
    long_description=long_description,        
    long_description_content_type="text/markdown",
    url="https://github.com/F-KHENFRI/JetRacerPy",  
    packages=setuptools.find_packages(),      
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',                 
    install_requires=[
        'opencv-python'
    ],
    
)