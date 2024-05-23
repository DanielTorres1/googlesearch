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
cpanm Moose
cd googlesearch
sudo cpan .
cd ..


sudo cp google.pl /usr/bin/google.pl
sudo chmod a+x /usr/bin/google.pl


