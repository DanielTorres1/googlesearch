#module-starter --module=googlesearch --author="Daniel Torres" --email=daniel.torres@owasp.org
package googlesearch;
our $VERSION = '1.1';
use Moose;
use Data::Dumper;
use LWP::UserAgent;
use URI;
use HTML::TreeBuilder;
use HTML::Scrubber;
use HTTP::Cookies;
use Regexp::Common qw/URI/;
use HTML::Entities;
use HTML::TokeParser;
use Encode;
use URI::Escape;

{
has proxy_host      => ( isa => 'Str', is => 'rw', default => '' );
has proxy_port      => ( isa => 'Str', is => 'rw', default => '' );
has proxy_user      => ( isa => 'Str', is => 'rw', default => '' );
has proxy_pass      => ( isa => 'Str', is => 'rw', default => '' );
has browser  => ( isa => 'Object', is => 'rw', lazy => 1, builder => '_build_browser' );


sub search  {
	my $self = shift;
	my %options = @_;
	
	my $keyword = $options{ keyword };
	my $date = $options{date};
	my $lang = $options{lang};
	my $filter = $options{filter};
	my $start = $options{start};
	my $country = $options{country};
	my $log_file = $options{log};

	my $proxy_host = $self->proxy_host;
	my $tries=0;
	SEARCH:
	
	if ($country ne "" )
		{$country = ".$country";} 

	my @results;                           
	#https://www.google.com/search?client=firefox-b-d&q=site%3Agithub.com+intext%3Aempoderar.gob.bo 
	my $url = "https://www.google.com$country/search??client=firefox-b-d&q=$keyword&btnG=&gbv=1&num=100&filter=0";
	if (defined $start )
	{$url.= "&start=$start";}
	
	if ( defined $date )
		{$url.= "&tbs=qdr:$date";} 
	
	if (defined $lang )
		{$url.= "&hl=$lang";}


	#print "url $url \n"; 

	#print "going to www.google.com \n";

	my $response = '';
	my $status;
	eval {
		$response = $self->dispatch(url =>"https://www.google.com$country",method => 'GET');
	};

	if ($@)
		{warn $@;} 
	sleep 5;

	eval {
		$response = $self->dispatch(url =>$url,method => 'GET');	
	};

	sleep 5;

	my $tree = HTML::TreeBuilder->new; # create a new object to clear preview data
	my $content = $response->content;
	
	$status = $response->status_line;
	print "status ($status)\n";	
	
	if($content =~ /Name or service not known/m){
	   if ($tries == 3)
			{die;}
	   $tries++;
	   goto SEARCH;		 
	 }
	
	if($content =~ /Our systems have detected unusual traffic from your computer network/m){
		print "Captcha detected !!";
		sleep 60;
		goto SEARCH;				
	}

	
	$tree->parse($content);	
	sleep 2;
	    
	my $scrubber = HTML::Scrubber->new( allow => [ qw[ p i li ol ul div h2 a ] ] ); 	
	$scrubber->rules(        
         a => {
			 href => 1 , 
            class => 1,           
            #href => qr{^((?!$domain).)*$}i,
        },     
    );
    
	my $final_content = $scrubber->scrub($content);	

	open (SALIDA,">google.html") || die "ERROR: No puedo abrir el fichero google.html\n";
	print SALIDA $final_content;
	close (SALIDA);


my $results_list = `egrep -o '?q=http[[:print:]]{10,350}&amp;' google.html | egrep -v "webcache|accounts.google.com"`;
system("cat google.html >> $log_file");
                        
$results_list =~ s/\?|q=//g; 
my @results_array = split("\n",$results_list);
#print Dumper @results_array ;
my $url_list = "";
foreach (@results_array )
{	
	$_ =~ s/&amp;.*//s;	#delete everything after &amp;	
	print "$_ \n";
	$url_list = $url_list.";".Encode::decode('utf8', uri_unescape($_));	
}

$url_list =~ s/\n//g; 
return $url_list;
}    


sub isIndexed  {
	my $self = shift;
	my %options = @_;
	
	my $keyword = $options{ keyword };

	my $tries=0;

	my @results;                            
	my $url = "https://www.google.com.uy/search?output=search&sclient=psy-ab&q=$keyword&btnG=&gbv=1&num=100";

	#print "going to www.google.com \n";

	my $response = '';
	eval {
		$response = $self->dispatch(url =>"https://www.google.com.uy",method => 'GET');
		my $status = $response->status_line;
	if($status =~ /504/m){
		if ($tries == 3)
			{die;}
	$tries++;
	goto CHOOSE;		 
	}
	};

	if ($@)
		{warn $@;} 
	sleep 5;

	eval {
		$response = $self->dispatch(url =>$url,method => 'GET');
	};

	sleep 5;
	
	my $content = $response->content;
	
	open (SALIDA,">google.html") || die "ERROR: No puedo abrir el fichero google.html\n";
	print SALIDA $content;
	close (SALIDA);
	
	
	if($content =~ /unusual traffic/){
		print "UPPS. IP BLOCKED";	
		die;		
	}
		
	if($content =~ /No se han encontrado resultados/){
		return "NO esta indexado";	
	}
	else
	{
		return "SI esta indexado";	
	}
	

}    




sub _build_browser {    

#print "building browser \n";
my $self = shift;

my $proxy_host = $self->proxy_host;
my $proxy_port = $self->proxy_port;
my $proxy_user = $self->proxy_user;
my $proxy_pass = $self->proxy_pass;

my @user_agents=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
"Mozilla/5.0 (Windows NT 10.0; WOW64; rv:56.0) Gecko/20100101 Firefox/56.0",
"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.89 Safari/537.36",); 
			  
my $user_agent = @user_agents[rand($#user_agents+1)];    
#print "user_agent $user_agent \n" if ($debug);


my $browser = LWP::UserAgent->new;
$browser->timeout(10);
$browser->show_progress(0);
$browser->default_header('User-Agent' => $user_agent); 
$browser->default_header('Accept' => 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'); 
$browser->default_header('Accept-Language' => 'en-US,en;q=0.5'); 
$browser->default_header('Connection' => 'keep-alive'); 

$browser->cookie_jar(HTTP::Cookies->new(file => "cookies.txt", autosave => 1));



if ($proxy_host eq 'tor')
{
 print "Using tor \n";
 $browser->proxy([qw/ http https /] => 'socks://localhost:9050');
}
elsif ($proxy_host eq 'incloak')
{}
else
{
  if (($proxy_user ne "") && ($proxy_host ne ""))
  {
   #print "Using private proxy \n " if ($debug);
   $browser->proxy(['http', 'https'], 'http://'.$proxy_user.':'.$proxy_pass.'@'.$proxy_host.':'.$proxy_port); # Using a private proxy
  }
  elsif ($proxy_host ne "")
    {   print "Using public proxy \n ";
	    $browser->proxy(['http', 'https'], 'http://'.$proxy_host.':'.$proxy_port);} # Using a public proxy    
}
return $browser;     
}


sub dispatch {    
my $self = shift;
my %options = @_;

my $url = $options{ url };
my $method = $options{ method };

my $response = '';
if ($method eq 'GET')
  { $response = $self->browser->get($url);}
  
if ($method eq 'POST')
  {     
   my $post_data = $options{ post_data };        
   $response = $self->browser->post($url,$post_data);
  }  
      
  
return $response;
}

}
1; 
