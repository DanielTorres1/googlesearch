use 5.006;
use strict;
use warnings;
use ExtUtils::MakeMaker;

WriteMakefile(
    NAME             => 'googlesearch',
    AUTHOR           => q{Daniel Torres <daniel.torres@owasp.org>},
    VERSION_FROM     => 'lib/googlesearch.pm',
    ABSTRACT_FROM    => 'lib/googlesearch.pm',
    LICENSE          => 'artistic_2',
    PL_FILES         => {},
    MIN_PERL_VERSION => '5.006',
    CONFIGURE_REQUIRES => {
        'ExtUtils::MakeMaker' => '0',
    },
    BUILD_REQUIRES => {
        'HTML::Scrubber' => '0',
        'Text::Unidecode' => '0',
    },
    PREREQ_PM => {
    
        'Regexp::Common' => '0',
        #'Foo::Bar::Module' => '5.0401',
    },
    dist  => { COMPRESS => 'gzip -9f', SUFFIX => 'gz', },
    clean => { FILES => 'googlesearch-*' },
);
