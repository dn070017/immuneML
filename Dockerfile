FROM centos:latest

# Can't just copy '.', because it will copy '.git' folder too, which is ~600MB and we don't need it
COPY test .
COPY scripts .
COPY source .
COPY helpers .
COPY docs .
COPY datasets .
COPY requirements.txt .
COPY setup.py .

# Installing yum dependencies 
RUN yum update -y
RUN yum install -y python3 python3-devel python-numpy python-scipy python-matplotlib ipython ipython-notebook python-pandas python-sympy python-nose git dnf-plugins-core make openssl-devel libcurl-devel libxml2-devel gcc gcc-c++ autoconf automake libtool m4 lvm

# Installing R
RUN dnf install -y epel-release
RUN dnf config-manager --set-enabled PowerTools
RUN yum install -y R

# Installing R dependencies
RUN R -e "install.packages('devtools', repos = 'https://cran.uib.no/')" -e "devtools::install_github('keshav-motwani/ggexp'); install.packages('Rmisc', dependencies = TRUE, repos = 'https://cran.uib.no/')"

# Since we are not using venv's, we must install 'wheel' and 'setuptools' manually
RUN pip3 install wheel setuptools 

# Voila
RUN pip3 install -r requirements.txt
