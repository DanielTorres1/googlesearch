#!/bin/bash
OKBLUE='\033[94m'
OKRED='\033[91m'
OKGREEN='\033[92m'
RESET='\e[0m'


function print_ascii_art {
cat << "EOF"
   
 GOOGLE
                                                  

					daniel.torres@owasp.org
					https://github.com/DanielTorres1

EOF
}


print_ascii_art

echo -e "$OKBLUE [+] Instalando Google search (Python) $RESET" 

# Verificar si pip está instalado
if ! command -v pip3 &> /dev/null; then
    echo -e "$OKRED [-] pip3 no está instalado. Instalando... $RESET"
    sudo apt-get update
    sudo apt-get install -y python3-pip
fi

# Instalar dependencias de Python
echo -e "$OKGREEN [+] Instalando dependencias de Python... $RESET"
pip3 install selenium webdriver-manager requests --break-system-packages

# Instalar Google Chrome si no está presente
if ! command -v google-chrome &> /dev/null && ! command -v google-chrome-stable &> /dev/null; then
    echo -e "$OKRED [-] google-chrome no está instalado. Instalando... $RESET"
    sudo apt-get update
    sudo apt-get install -y wget
    wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
    sudo apt-get install -y ./google-chrome-stable_current_amd64.deb
    rm -f google-chrome-stable_current_amd64.deb
fi

# Instalar ChromeDriver si no está presente
if ! command -v chromedriver &> /dev/null; then
    echo -e "$OKRED [-] chromedriver no está instalado. Instalando... $RESET"
    sudo apt-get update
    sudo apt-get install -y chromium-driver
fi


cp googlesearch-client.py /usr/bin/
chmod +x /usr/bin/googlesearch-client.py
cp -r googlesearch /usr/bin/

echo -e "$OKGREEN [+] Instalación completada! $RESET"




