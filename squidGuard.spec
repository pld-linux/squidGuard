%define		_sver 2001-06-14
Summary:	Filter, redirector and access controller plugin for Squid
Summary(pl):	Wtyczka z filtrem, przekierowywaniem i kontrolerem dostêpu dla Squida
Name:		squidGuard
Version:	1.2.0
Release:	2
License:	GPL
Group:		Networking/Daemons
Source0:	ftp://ftp.ost.eltele.no/pub/www/proxy/squidGuard/development/%{_sver}.%{name}-%{version}.tar.gz
Source1:	%{name}.conf
Patch0:		%{name}-db.patch
Patch1:		%{name}-makefile.patch
URL:		http://www.squidguard.org
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)
Prereq:		grep
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	db3-devel
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

%description -l pl
SquidGuard jest wtyczk± dla Squida z po³±czonym filtrem,
przekierowywaniem i kontrolerem dostêpu. Jest darmowy, elastyczny,
bardzo szybki, ³atwo instalowalny, przeno¶ny. Mo¿e byæ u¿ywany do:
- ograniczenia dostêpu do WWW dla niektórych u¿ytkowników na podstawie
  listy akceptowanych serwerów lub URL
- blokowania dostêpu do niektórych serwerów lub URL dla niektórych
  u¿ytkowników
- blokowania dostêp do URL na podstawie wyra¿eñ regularnych lub s³ów
  dla niektórych u¿ytkowników
- narzucenia u¿ywanie nazw domen/zabronienia u¿ywania adresów IP w URL
- przekierowania zablokowanych URL na "inteligentn±" stronê
  informacyjn± w CGI
- przekierowania niezarejestrowanych u¿ytkowników do formularza
  rejestracyjnego
- przekierowania ¶ci±gania popularnego oprogramowania (Netscape, MSIE)
  na lokalne kopie
- przekierowania bannerów na puste GIF-y
- uzale¿nienia regu³ dostêpu w zale¿no¶ci od pory dnia, dnia tygodnia,
  daty itp.
- ró¿nych regu³ dostêpu dla ró¿nych grup u¿ytkowników.

Natomiast ani squidGuard ani Squid nie mo¿e byæ u¿yty do:
- filtrowania/cenzorowania/edycji tekstu wewn±trz dokumentu
- filtrowania/cenzorowania/edycji osadzonych w HTML skryptów
  (JavaScript, VBscript...)

%prep
%setup -q -n %{name}-%{version}
%patch0 -p1
%patch1 -p1

%build
%{__aclocal}
%{__autoconf}
%configure \
	--with-sg-logdir=/var/log/%{name} \
	--with-sg-config=%{_sysconfdir}/squidGuard.conf \
	--with-sg-dbhome=%{_sysconfdir}/db

%{__make}

%install
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT{/var/log/%{name},%{_bindir},%{_sysconfdir}}
install -d $RPM_BUILD_ROOT%{_sysconfdir}/db/{advertising,bannedsource,banneddestination}
install -d $RPM_BUILD_ROOT%{_sysconfdir}/db/{timerestriction,lansource,privilegedsource}

install src/squidGuard $RPM_BUILD_ROOT%{_bindir}

touch $RPM_BUILD_ROOT%{_sysconfdir}/db/advertising/{domains,urls}
touch $RPM_BUILD_ROOT%{_sysconfdir}/db/banneddestination/{domains,urls,expressions}
touch $RPM_BUILD_ROOT%{_sysconfdir}/db/bannedsource/ips
touch $RPM_BUILD_ROOT%{_sysconfdir}/db/lansource/lan
touch $RPM_BUILD_ROOT%{_sysconfdir}/db/timerestriction/lan
touch $RPM_BUILD_ROOT%{_sysconfdir}/db/privilegedsource/ips

touch $RPM_BUILD_ROOT/var/log/%{name}/%{name}.{log,error}

tar zxf samples/dest/blacklists.tar.gz -C $RPM_BUILD_ROOT%{_sysconfdir}/db
install %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}

gzip -9nf README ANNOUNCE samples/*.{cgi,conf}

%clean
rm -rf $RPM_BUILD_ROOT

%post
if [ -f /etc/squid/squid.conf ] && \
    ! grep -q "^redirect_program.*%{_bindir}/%{name}" /etc/squid/squid.conf; then
	echo "redirect_program /usr/bin/squidGuard -c /etc/squidGuard/squidGuard.conf" >>/etc/squid/squid.conf
	if [ -f /var/lock/subsys/squid ]; then
		/etc/rc.d/init.d/squid reload 1>&2
	fi
fi

%preun
if [ -f /etc/squid/squid.conf ]; then
    grep -E -v "^redirect_program.*%{_bindir}/%{name}" /etc/squid/squid.conf > \
    /etc/squid/squid.conf.tmp
    mv -f /etc/squid/squid.conf.tmp /etc/squid/squid.conf
    if [ -f /var/lock/subsys/squid ]; then
	/etc/rc.d/init.d/squid reload 1>&2
    fi
fi

%files
%defattr(644,root,root,755)
%doc *.gz doc/*.{html,gif,txt} samples/*.gz
%doc contrib/{squidGuardRobot/{squidGuardRobot,RobotUserAgent.pm},sgclean/sgclean,hostbyname/hostbyname}
%attr(755,root,root) %{_bindir}/*
%attr(750,root,squid) %dir %{_sysconfdir}
%attr(640,root,squid) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/squidGuard.conf
%{_sysconfdir}/db
%attr(750,root,squid) %dir /var/log/%{name}
%attr(640,squid,squid) %ghost /var/log/%{name}/*
