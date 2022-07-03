from setuptools import setup, find_packages

setup(
    name="chess",
    version="1.0",
    author="czy",
    author_email="chenzhiyuan@mail.ustc.edu.cn",
    description="Quantum Chess",
    url="https://github.com/czy-ustc/chess",
    packages=find_packages(),
    install_requires=["click", "uvicorn", "fastapi", "sqlalchemy"],
    python_requires=">=3.7",
    include_package_data=True,
    package_data={"chess": ["web/dist/*"]},
)
