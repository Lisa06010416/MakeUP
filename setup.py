from setuptools import setup, find_packages


requires_list =[
    "requests",
    "wget",
    "beautifulsoup4",
    "selenium",
    "mitmproxy",
    "efficientnet_pytorch",
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
    package_dir={"makeup": "src/makeup"},
    python_requires=">=3.6, <3.8",
    install_requires=requires_list,
    scripts=['script/mitmdump_server', 'script/close_mitmdump_server'],
    entry_points={
        'console_scripts': ['mitmdump_server=makeup.cmdline:setup_mitmdump_server',
                            'close_mitmdump_server=makeup.cmdline:close_mitmdump_server'],
    },
)
