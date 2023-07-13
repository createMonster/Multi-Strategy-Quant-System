import setuptools #python3 -m pip install setuptools

#1. Create a folder for your private code library
#2. Create an __init__ py file inside the code library
#3. Create a setup file outside the private code library
#4. Now you can add code files inside the quantlib folder and use it as a package like any other! (pip install using developement mode) >> python3 -m pip install -e.

setuptools.setup(
    name="quantlib",
    version="0.1",
    description="code lib by Larry",
    url="#",
    author="Larry",
    install_requires=["opencv-python"],
    author_email="",
    packages=setuptools.find_packages(),
    zip_safe=False
) #do go and read what these parameters mean!