# caller.pl
use DateTime;
use DateTime::Duration;
use strict;
use warnings;

# Parametros a recibir desde Criterios
my $varname         = "eco.sbc_current";
my $delta_minutos   = 60;   
my $umbral_min      = 120;   


my $dt_ini = DateTime->new(
    year       => 2019,
    month      => 01,
    day        => 01,
    hour       => 01,
    minute     => 00,
);
my $dt_fin = $dt_ini + DateTime::Duration->new( minutes => 10 );

# Ciclo a reemplazar por cron ...
my $t_i = $dt_ini;
my $t_f;
my $i = 0;
while ( 1 ) {
    $t_f = $t_i + DateTime::Duration->new( minutes => $delta_minutos );
    my $respuesta = `perl query_2.pl $varname $t_i $t_f`;
    
    print "variable: $varname | desde:$t_i | hasta:$t_f \n";
    my $valor = parse_value($respuesta);

    # Simula comparacion 
    if( $valor < $umbral_min ) {
        print "valor: $valor menor que $umbral_min ... ==> alertar !!!\n";
        print "\tinvocando alerta para $varname [ por desarrollar] ...\n";
    } else {
        print "valor: $valor no menor que $umbral_min, no hay problema\n";
    }
    ++$i;
    $t_i = $t_f;
    sleep 2;
}

sub parse_value {
    my $str = shift;
    my @lines = split(/\n/,$str);
    $lines[2] =~ s/\D//m;
    $lines[2] =~ s/\n//;
    return $lines[2];
}