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

# Instalar ChromeDriver automáticamente
echo -e "$OKGREEN [+] ChromeDriver se instalará automáticamente con webdriver-manager $RESET"

echo -e "$OKGREEN [+] Instalación completada! $RESET"


