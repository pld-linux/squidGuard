Summary:	Filter, redirector and access controller plugin for Squid. 
Name:		squidGuard
Version:	1.1.4
Release:	1
License:	GPL
Group:		Networking/Daemons
Group(de):	Netzwerkwesen/Server
Group(pl):	Sieciowe/Serwery
Source0:	ftp://ftp.ost.eltele.no/pub/www/proxy/squidGuard/%{name}-%{version}.tar.gz
Source1:	http://ftp.ost.eltele.no/pub/www/proxy/squidGuard/contrib/blacklists.tar.gz
Source2:	%{name}.conf
Source3:	%{name}.cgi
Source4:	%{name}-nulbanner.png
#Patch0:		%{name}-paths.patch
URL:		http://www.squidguard.org
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)
BuildRequires:	db2-devel
Requires:	squid

%define		_sysconfdir	/etc/%{name}
%define		_datadir	%{_sysconfdir}

%description
SquidGuard is a combined filter, redirector and access controller
plugin for Squid. It is free, very flexible, extremely fast, easily
installed, portable. SquidGuard can be used to
- limit the web access for some users to a list of accepted/well known
  web servers and/or URLs only.
- block access to some listed or blacklisted web servers and/or URLs
  for some users.
- block access to URLs matching a list of regular expressions or words
  for some users.
- enforce the use of domainnames/prohibit the use of IP address in
  URLs.
- redirect blocked URLs to an "intelligent" CGI based info page.
- redirect unregistered user to a registration form.
- redirect popular downloads like Netscape, MSIE etc. to local copies.
- redirect banners to an empty GIF.
- have different access rules based on time of day, day of the week,
  date etc.
- have different rules for different user groups.


Neither squidGuard nor Squid can be used to

- filter/censor/edit text inside documents
- filter/censor/edit embeded scripting languages like JavaScript or
  VBscript inside HTML

%prep
%setup -q
#%patch0 -p1
%build
aclocal
autoconf
%configure \
	--with-db-inc=%{_includedir}/db2

%{__make}

%install
rm -rf $RPM_BUILD_ROOT

%{__make} install DESTDIR=$RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT/var/log/%{name}
install -d $RPM_BUILD_ROOT/etc/squid
install -d $RPM_BUILD_ROOT%{_sysconfdir}/db/{advertising,bannedsource,banneddestination}
install -d $RPM_BUILD_ROOT%{_sysconfdir}/db/{timerestriction,lansource,privilegedsource}

touch $RPM_BUILD_ROOT%{_sysconfdir}/db/advertising/{domains,urls}
touch $RPM_BUILD_ROOT%{_sysconfdir}/db/banneddestination/{domains,urls,expressions}
touch $RPM_BUILD_ROOT%{_sysconfdir}/db/bannedsource/ips
touch $RPM_BUILD_ROOT%{_sysconfdir}/db/lansource/lan
touch $RPM_BUILD_ROOT%{_sysconfdir}/db/timerestriction/lan
touch $RPM_BUILD_ROOT%{_sysconfdir}/db/privilegedsource/ips

touch $RPM_BUILD_ROOT/var/log/%{name}/%{name}.{log,error}

tar zxf %{SOURCE1}   -C $RPM_BUILD_ROOT%{_sysconfdir}/db
install %{SOURCE2}	$RPM_BUILD_ROOT%{_sysconfdir}

gzip -9nf README ANNOUNCE

%post
echo "WARNING !!! WARNING !!! WARNING !!! WARNING !!!"
echo ""
echo "Modify the following line in the /etc/squid/squid.conf file:"
echo "redirect_program /usr/bin/squidGuard -c /etc/squid/squidGuard.conf"

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc *.gz doc/*.{html,gif,txt}
%attr(755,root,root) %{_bindir}/*
%attr(750,root,squid) %dir %{_sysconfdir}
%attr(640,root,squid) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/squidGuard.conf
%attr(755,root,root) %{_sysconfdir}/db
%attr(750,root,squid) %dir /var/log/%{name}
%attr(644,squid,squid) %ghost /var/log/%{name}/*
