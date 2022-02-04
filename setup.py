from setuptools import setup, find_packages


requires_list =[
    "requests",
    "wget",
    "beautifulsoup4",
    "selenium",
    "mitmproxy",
    "efficientnet_pytorch==0.7.0",
    "google",
    "scikit_learn",
    "torch",
    "torchvision",
    "transformers",
]

setup(
    name="makeup",
    version="0.1",
    author="Lisa",
    author_email="linlisa0601@gmail.com",
    description="Contain functions which are using in Makeup Project",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages("src"),
    package_dir={"": "src"},
    python_requires=">=3.6, <3.8",
    install_requires=requires_list,
    zip_safe=False,
    include_package_data=True
)
