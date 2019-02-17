#  -H "Content-Type: application/json" --data-binary @data.json
# Consulta numero de ocurrencias de una variable en un periodo

use Mojo::JSON qw(decode_json encode_json);
use Data::Dumper;
	
my $DEBUG = 1;   # 1: Con Debug, 0: Sin Debug

my $varname = "eco.sbc_current";
my $t_ini   = "2019-01-09T11:00:00"; 
my $t_fin   = "2019-01-09T12:00:00";
my $host    = "172.17.233.169:9200";
my $indexpat= "vtr-logs-6m-2019\*";

#my $CMD = "curl -XGET \"http://$host/vtr-logs-6m-2019*/_search\" -H 'Content-Type: application/json' -d'";
my $dep = ( $DEBUG == 1 ? "-v" : "" );
my $CMD = "curl ". $dep ." -XGET \"http://$host/$indexpat/_search\" -H \"Content-Type: application/json\" --data-binary \@data.json";

my $QUERY= << "END_QUERY";
{
  "query":{
      "range":{
         "\@timestamp":{
            "gte":"$t_ini",
            "lt":"$t_fin"
         }
      }
   },
   "aggregations": {
        "SUM($varname)": {
            "value_count": {
                "field": "$varname"
            }
        }
   },
   "_source": ["$varname"]
}

END_QUERY

print $QUERY if $DEBUG;

unlink "data.json";
open my $fh, "+>data.json" or die "$!\n";
print $fh $QUERY;
close $fh;

# Depuracion ...
#print $CMD;
#print "\n";
#print $QUERY;

my $resp = `$CMD`;
print "\n=== respuesta JSON ===============\n" if $DEBUG;
print $resp if $DEBUG;
my $hash  = decode_json $resp;   # La respuesta de JSON a Hash

print "\n==================\n";
print Dumper $hash->{'aggregations'}->{'SUM(eco.sbc_current)'}->{'value'} if $DEBUG;

my $valor = $hash->{'aggregations'}->{'SUM(eco.sbc_current)'}->{'value'};
print "\n==================\n";
print "Total: $valor\n";
				 

=begin
print Dumper $hash;
 'aggregations' => {
                   'SUM(eco.sbc_current)' => {
                                             'value' => 120
                                           }
                 },
=cut
