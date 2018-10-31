#!"C:/Program Files (x86)/Ampps\perl\bin\perl.exe"

use HTML::Perlinfo;
use CGI qw(header);

$q = new CGI;
print $q->header;

print "<html><head><title>Perl Info</title></head>";
print "<body><p><a href='http://localhost/ampps'>Back to AMPPS Home</a></p><center><h2>Perl Info</h2></center>";
print "</body></html>";

$p = new HTML::Perlinfo;
$p->info_general;
$p->info_variables;
$p->info_modules;
$p->info_license;
