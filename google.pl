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

my $GOOGLE_URL = "https://pzhuqnayh7.execute-api.us-east-1.amazonaws.com/burpendpoint";
my $term = $opts{'t'} if $opts{'t'};
my $total_pages = $opts{'p'} if $opts{'p'};
my $log_file = $opts{'l'} if $opts{'l'};
my $salida = $opts{'o'} if $opts{'o'};
my $date = $opts{'d'} if $opts{'d'};
my $debug=1;
#my $proxy = $opts{'r'} if $opts{'r'};

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
  print "-d : Date \n";
  print "-l : log file \n";
  #print "-r : 1/0 Usar o no proxy \n";
  print "google.pl -t 'site:gob.bo' -l google.html -r 0 \n";  
  
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
#if ($proxy)
#{

#my $file_proxies="/usr/share/proxy/proxies.txt";
#srand;
#open FILE, "<$file_proxies" or die "Could not open $file_proxies: !\n";
#rand($.)<1 and ($proxy_line=$_) while <FILE>;
#close FILE;
#$proxy_line =~ s/\n//g; 

#my @line_array = split(";",$proxy_line);
#my $host = @line_array[0];
#my $port = @line_array[1];
#my $username = @line_array[2];
#my $password = @line_array[3];


#print "Usando: $proxy_line \n";	
#$google_search = googlesearch->new(proxy_host => $host,
								  #proxy_port => $port,
								  #proxy_user => $username,
								  #proxy_pass => $password);	
#}
#else
#{
 
#}


if ($total_pages eq "")
{
	print BLUE,"\t[+] Estimando resultados .. \n",RESET;
	my $url = "$GOOGLE_URL/search?q=$term&filter=0&num=100";
	if ( defined $date )
		{$url.= "&tbs=qdr:$date";} 
		
	$response = $google_search->dispatch(url =>$url ,method => 'GET');
	my $content = $response->content;
	print($content);

	open (SALIDA,">>googleCountRes.html") || die "ERROR: No puedo abrir el fichero googleCountRes.html \n";
	print SALIDA $content,"\n" ;
	close (SALIDA);
		
    $noresult=`egrep -io '"No se han encontrado resultados"|"did not match any documents"' googleCountRes.html`;    
    if ($noresult eq "")
	{
		$total_pages=`egrep -o ';start=[[:digit:]]{3,4}&' googleCountRes.html | sort | uniq | wc -l`+1; 
		#print "total_pages $total_pages \n";
	}
	else
	{print "No hay resultados en google para esa busqueda"; die;}
	#system("rm googleCountRes.html");
	
}

print YELLOW,"\t[+] Termino de busqueda: $term \n",RESET;
print YELLOW,"\t[+] Paginas a revisar: $total_pages \n",RESET;

print BLUE,"\t[+] Buscando en google \n",RESET;

		
for (my $page =0 ; $page<=$total_pages-1;$page++)		
{
		print "\t\t[+] pagina: $page \n";
		# Results 1-100 
		$list = $google_search->search(keyword => $term, start => $page*100, log => $log_file, date => $date);
		my @list_array = split(";",$list);

		foreach $url (@list_array)
		{
			$url =~ s/\n//g; 
			
			print "url $url" if ($debug);
			open (SALIDA,">>$salida") || die "ERROR: No puedo abrir el fichero $salida\n";
			print SALIDA $url,"\n" ;
			close (SALIDA);
		}	

		sleep 1;
}	

#print "\t[+] Ordenando lista \n";
#system(" pwd; sort $salida | uniq > temp.txt");
#system(" mv temp.txt $salida");

