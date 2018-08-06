#!/usr/bin/perl
use googlesearch;
use Data::Dumper;
use Getopt::Std;
use Term::ANSIColor qw(:constants);
use utf8;
use Text::Unidecode;
binmode STDOUT, ":encoding(UTF-8)";
my %opts;
getopts('t:o:h', \%opts);

  
	  
my $term = $opts{'t'} if $opts{'t'};
my $salida = $opts{'o'} if $opts{'o'};

my $banner = <<EOF;

Google search                                                    

Autor: Daniel Torres Sandi
EOF


sub usage { 
  
  print $banner;
  print "Uso:  \n";  
  print "-t : Termino de busqueda \n";
  print "-o : Salida \n";
  print "-h : Ayuda \n";
  print "google.pl -t 'site:gob.bo' \n";  
  
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

print BLUE,"\t[+] Estimando resultados .. \n",RESET;
my $url = "http://www.google.com/search?output=search&sclient=psy-ab&q=$term&btnG=&gbv=1&filter=0&num=100";
$response = $google_search->dispatch(url =>$url ,method => 'GET');
my $content = $response->content;

open (SALIDA,">>google.html") || die "ERROR: No puedo abrir el fichero $salida\n";
print SALIDA $content,"\n" ;
close (SALIDA);
			
$total_pages=`grep -o 'start=' google.html | wc -l`;
system("rm google.html");

print YELLOW,"\t[+] Termino de busqueda: $term \n",RESET;
print YELLOW,"\t[+] Paginas a revisar: $total_pages \n",RESET;

print BLUE,"\t[+] Buscando en google \n",RESET;

		
for (my $page =0 ; $page<=$total_pages-1;$page++)		
{
		print "\t\t[+] pagina: $page \n";
		# Results 10-20 
		$list = $google_search->search(keyword => $term, country => "bo", start => $page*100);
		my @list_array = split(";",$list);

		foreach $url (@list_array)
		{
			$url =~ s/\n//g; 
			open (SALIDA,">>$salida") || die "ERROR: No puedo abrir el fichero $salida\n";
			print SALIDA $url,"\n" ;
			close (SALIDA);
		}	
		my $time_sleep = 30+($page*10);
		if ($time_sleep > 60)
			{
				my $random_number = int(rand(30));
				$time_sleep=60+$random_number;
			}
		print "\t\t[+] Durmiendo $time_sleep  segundos para evitar bloqueo de google \n";
		sleep $time_sleep ;
}	

print "\t[+] Ordenando lista \n";
system(" sort $salida | uniq > temp.txt");
system(" mv temp.txt $salida");
system("rm google2.html google.html");

