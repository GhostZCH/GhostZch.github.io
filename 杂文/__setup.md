sudo apt-get update
sudo apt-get install gconf-service gconf-service-backend libgconf-2-4 gconf2-common git ipython zsh wget curl vim htop ifstat iostat wine tree terminator make cmake python-dev code
sudo apt-get upgrade

curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
sudo python get-pip.py


wget --no-check-certificate https://github.com/robbyrussell/oh-my-zsh/raw/master/tools/install.sh
chmod +x install.sh
sudo ./install.sh
sudo chsh -s /bin/zsh


wine source-insight

sudo add-apt-repository ppa:webupd8team/java
sudo apt-get update
sudo apt-get install oracle-java8-installer
sudo apt-get install oracle-java8-set-default

http://www.linuxidc.com/Linux/2016-11/136958.htm

