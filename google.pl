#!/usr/bin/perl
use googlesearch;
use Data::Dumper;
use Getopt::Std;
use Term::ANSIColor qw(:constants);
use utf8;
use Text::Unidecode;
binmode STDOUT, ":encoding(UTF-8)";
my %opts;
getopts('t:o:p:l:d:h', \%opts);

my $GOOGLE_URL = "https://ipt5gxa9dh.execute-api.us-east-1.amazonaws.com/googleProxy";
my $term = $opts{'t'} if $opts{'t'};
my $total_pages = $opts{'p'} if $opts{'p'};
my $log_file = $opts{'l'} if $opts{'l'};
my $salida = $opts{'o'} if $opts{'o'};
my $date = $opts{'d'} if $opts{'d'};
my $debug=0;
#my $proxy = $opts{'r'} if $opts{'r'};

my $banner = <<EOF;

Google search                                                    

Autor: Daniel Torres Sandi
EOF


sub usage { 
  
  print $banner;
  print "Uso:  \n";  
  print "-t : Termino de busqueda \n";
  print "-o : Salida \n"; #lista urls
  print "-h : Ayuda \n";
  print "-d : Date \n";
  print "-l : log file \n";
  #print "-r : 1/0 Usar o no proxy \n";
  print "google.pl -t 'site:gob.bo' -l google2.html -o lista.txt \n";  
  
}	

# Print help message if required
if ($opts{'h'} || !(%opts)) {
	usage();
	exit 0;
}


$ENV{PERL_LWP_SSL_VERIFY_HOSTNAME} = 0; #proxy compatibility
use Time::localtime;

my $t = localtime;
$time = sprintf( "%04d-%02d-%02d",$t->year + 1900, $t->mon + 1, $t->mday);
my $google_search = googlesearch->new();

print YELLOW,"\t[+] Termino de busqueda: $term \n",RESET;
print BLUE,"\t[+] Buscando en google \n",RESET;

my $page = 0;		
while(1)
{
	my $printpage = $page + 1 ;
	print "\t\t[+] pagina: $printpage \n";
	# Results 1-100 
	$list = $google_search->search(keyword => $term, start => $page*100, log => $log_file, date => $date);
	my @list_array = split(";",$list);

	foreach $url (@list_array)
	{
		$url =~ s/\n//g; 
				
		open (SALIDA,">>$salida") || die "ERROR: No puedo abrir el fichero $salida\n";
		print SALIDA $url,"\n" ;
		close (SALIDA);
	}	

	$next_link=`egrep -i "Next &gt;|More results|>&gt;</" $log_file | wc -l`;
	print("next_link $next_link") if ($debug);
	if ($next_link > 0) 
		{$page = $page + 1;	}
	else
		{exit;}# ya no hay mas paginas a revisar

	sleep 1;
}	

#print "\t[+] Ordenando lista \n";
#system(" pwd; sort $salida | uniq > temp.txt");
#system(" mv temp.txt $salida");

