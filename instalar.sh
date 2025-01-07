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

echo -e "$OKBLUE [+] Instalando Google search $RESET" 

go build -o googlesearch-client googlesearch-client.go
sudo cp googlesearch-client /usr/bin/googlesearch-client
sudo chmod a+x /usr/bin/googlesearch-client


