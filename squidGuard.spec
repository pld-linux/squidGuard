%define		blist_ver 20041023
%define		ver 1.2.0
Summary:	Filter, redirector and access controller plugin for Squid
Summary(pl):	Wtyczka z filtrem, przekierowywaniem i kontrolerem dostêpu dla Squida
Name:		squidGuard
Version:	%{ver}_%{blist_ver}
Release:	2
Epoch:		2
License:	GPL
Group:		Networking/Daemons
Source0:	ftp://ftp.teledanmark.no/pub/www/proxy/%{name}/%{name}-%{ver}.tar.gz
# Source0-md5:	c6e2e9112fdbda0602656f94c1ce31fd
Source1:	%{name}.conf
Source2:	ftp://ftp.teledanmark.no/pub/www/proxy/%{name}/contrib/blacklists-%{blist_ver}.tar.gz
# Source2-md5:	abbea06a368d81ad43b4f971dd673106
Patch0:		%{name}-db.patch
Patch1:		%{name}-makefile.patch
URL:		http://www.squidguard.org/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	db3-devel
BuildRequires:	gettext-devel
BuildRequires:	libtool
Requires(post,preun):	grep
Requires(post,preun):	squid
Requires(preun):	fileutils
Requires:	squid
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

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
SquidGuard jest wtyczk± dla Squida bêd±c± po³±czonym filtrem,
przekierowywaniem i kontrolerem dostêpu. Jest darmowy, elastyczny,
bardzo szybki, ³atwo instalowalny, przeno¶ny. Mo¿e byæ u¿ywany do:
- ograniczenia dostêpu do WWW dla niektórych u¿ytkowników na podstawie
  listy akceptowanych serwerów lub URL-i
- blokowania dostêpu do niektórych serwerów lub URL-i dla niektórych
  u¿ytkowników
- blokowania dostêpu do URL na podstawie wyra¿eñ regularnych lub
  s³ów dla niektórych u¿ytkowników
- narzucenia u¿ywania nazw domen/zabronienia u¿ywania adresów IP w
  URL-ach
- przekierowania zablokowanych URL-i na "inteligentn±" stronê
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
%setup -q -n %{name}-%{ver}
%patch0 -p1
%patch1 -p1

%build
rm -f missing
%{__libtoolize}
%{__gettextize}
%{__aclocal}
%{__autoconf}
%configure \
	--with-sg-logdir=/var/log/%{name} \
	--with-sg-config=%{_sysconfdir}/squidGuard.conf \
	--with-sg-dbhome=%{_sysconfdir}/db \
	--with-db=%{_prefix}

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/var/log/%{name},%{_bindir}} \
	$RPM_BUILD_ROOT%{_sysconfdir}/db/{advertising,bannedsource,banneddestination} \
	$RPM_BUILD_ROOT%{_sysconfdir}/db/{timerestriction,lansource,privilegedsource}

install src/squidGuard $RPM_BUILD_ROOT%{_bindir}

touch $RPM_BUILD_ROOT%{_sysconfdir}/db/advertising/{domains,urls}
touch $RPM_BUILD_ROOT%{_sysconfdir}/db/banneddestination/{domains,urls,expressions}
touch $RPM_BUILD_ROOT%{_sysconfdir}/db/bannedsource/ips
touch $RPM_BUILD_ROOT%{_sysconfdir}/db/lansource/lan
touch $RPM_BUILD_ROOT%{_sysconfdir}/db/timerestriction/lan
touch $RPM_BUILD_ROOT%{_sysconfdir}/db/privilegedsource/ips

touch $RPM_BUILD_ROOT/var/log/%{name}/%{name}.{log,error}

tar zxf %{SOURCE2} -C $RPM_BUILD_ROOT%{_sysconfdir}/db
install %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}
rm -rf samples/dest

rm -f $(find $RPM_BUILD_ROOT%{_sysconfdir}/db -name *diff -type f)

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
	umask 027
	grep -E -v "^redirect_program.*%{_bindir}/%{name}" /etc/squid/squid.conf > \
		/etc/squid/squid.conf.tmp
	mv -f /etc/squid/squid.conf.tmp /etc/squid/squid.conf
	chown root:squid /etc/squid/squid.conf
	if [ -f /var/lock/subsys/squid ]; then
		/etc/rc.d/init.d/squid reload 1>&2
	fi
fi

%files
%defattr(644,root,root,755)
%doc README ANNOUNCE samples/* doc/*.{html,gif,txt}
%doc contrib/{squidGuardRobot/{squidGuardRobot,RobotUserAgent.pm},sgclean/sgclean,hostbyname/hostbyname}
%attr(755,root,root) %{_bindir}/*
%attr(750,root,squid) %dir %{_sysconfdir}
%attr(640,root,squid) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/squidGuard.conf
%{_sysconfdir}/db
%attr(770,root,squid) %dir /var/log/%{name}
%attr(640,squid,squid) %ghost /var/log/%{name}/*
