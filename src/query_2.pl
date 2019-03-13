# 
# Consulta numero de ocurrencias de una variable en un periodo
# Formato esperado de timestamp : "2019-01-09T11:00:00"
#

use Data::Dumper;
use Search::ElasticSearch;
	
my $DEBUG = 0;   # 1: Con Debug, 0: Sin Debug

my @servers    = ("172.17.233.169:9200", "172.17.233.170:9200");
my $indexpat   = "vtr-logs-6m-2019\*";

my $varname = shift || "eco.sbc_current";
my $t_ini   = shift || "2019-01-09T11:00:00"; 
my $t_fin   = shift || "2019-01-09T12:00:00";

my $e = Search::Elasticsearch->new(
    nodes => \@servers,
#    trace_to => 'Stderr'  # Si se desea depurar el request a ES
);


my $results = $e->search(
    index => $indexpat,
    body  => {
        query => {
            range => {
                "\@timestamp"=>{
                        "gte"   =>"$t_ini",
                        "lt"    =>"$t_fin"
                }
            }
        },
        aggregations => {
                "SUM($varname)" => {
                    "value_count" => {
                        "field" => "$varname"
                    }
                }
        },
        _source => ["$varname"]
    }
);

# print Dumper $results if $DEBUG;

print "\n=== Respuesta ===\n";
print $results->{'aggregations'}->{'SUM(eco.sbc_current)'}->{'value'};
print "\n";


